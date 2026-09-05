import argparse
from datetime import datetime
import logging
import time
import psutil
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.data import Data, DataLoader
from torch_geometric.nn import GCNConv, global_mean_pool
from torch_geometric.utils import from_networkx
import torch.nn.functional as F

from matplotlib import pyplot as plt
import networkx as nx
from tqdm import tqdm

import code_writer
from instruction_language.ast_transformer import encode_ast_nodes, hierarchy_plot
from instruction_language.elements import types
from instruction_language.elements.base import Codeblock
import random

from instruction_language.interpreter import InstructionInterpreter
from instruction_language.surroundings.environment import Environment, GEMService
from logging_setup import setup_logger
import numpy as np
from sklearn.linear_model import LinearRegression
import os
import json


logger = setup_logger("main", level=logging.INFO,
                      log_file="logs/main.log", to_console=False)

if not os.path.exists("storage"):
    os.makedirs("storage")

proc = psutil.Process(os.getpid())


class GraphEncoder(nn.Module):
    def __init__(self, in_channels, hidden_channels):
        super().__init__()
        self.conv1 = GCNConv(in_channels, hidden_channels)
        self.conv2 = GCNConv(hidden_channels, hidden_channels)

    def forward(self, x, edge_index, batch):
        x = F.relu(self.conv1(x, edge_index))
        x = F.relu(self.conv2(x, edge_index))
        graph_repr = global_mean_pool(x, batch)
        return graph_repr


class ActionEncoder(nn.Module):
    def __init__(self, input_dim=3, hidden_dim=64, output_dim=32):
        super(ActionEncoder, self).__init__()
        self.fc = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, output_dim)
        )

    def forward(self, action_tensor):
        """
        action_tensor: shape [batch_size, 3] — each row is (a1, a2, a3)
        """
        return self.fc(action_tensor)


class CodePredicter(nn.Module):
    def __init__(self, state_dim, action_dim):
        super(CodePredicter, self).__init__()
        self.fc = nn.Sequential(
            nn.Linear(state_dim + action_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 1)  # Output: score
        )

    def forward(self, state_embedding, action_embedding):
        x = torch.cat([state_embedding, action_embedding], dim=-1)
        return self.fc(x)


class CarryingValuePredicter(nn.Module):
    def __init__(self, state_dim, action_dim, hidden_dim=64):
        super(CarryingValuePredicter, self).__init__()
        self.fc = nn.Sequential(
            nn.Linear(state_dim + action_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 1)  # Output: predicted carrying value
        )

    def forward(self, state_embedding, action_embedding):
        x = torch.cat([state_embedding, action_embedding], dim=-1)
        return self.fc(x)


node2int = []


def actions_to_tensor(action_space):
    action_tensor = []
    for node, n_type, order in action_space:
        if node not in node2int:
            node2int.append(node)
        node_idx = node2int.index(node)
        action_tensor.append([node_idx, types.t2int[n_type], order])

    return torch.tensor(action_tensor, dtype=torch.float)


def choose_action(model: CodePredicter, rely_on_model_weight, state, action_embeddings):

    # Choose action: epsilon-greedy
    if random.random() < rely_on_model_weight:
        # Model chooses best action
        scores = []
        for i in range(action_embeddings.size(0)):
            score = model(state[0], action_embeddings[i])
            scores.append(score.item())
        best_action_idx = int(torch.tensor(scores).argmax())
    else:
        # Random action
        best_action_idx = random.randint(
            0, action_embeddings.size(0) - 1)

    return action_space[best_action_idx], best_action_idx


def choose_carrying_value(model: CarryingValuePredicter, state, action_embeddings, best_action_idx):
    if random.random() < rely_on_model_weight:
        # Use model to predict carrying value
        carrying_value = model(
            state[0], action_embeddings[best_action_idx])
        carrying_value = carrying_value.item()
    else:
        # maximum of 50 vars and envs
        carrying_value = random.randint(0, 50)

    return carrying_value


parser = argparse.ArgumentParser(
    description="Codewriter RL Training Program")

# Add a string parameter --checkpoint
parser.add_argument(
    '--checkpoint',
    type=str,
    default=None,
    help='Path to checkpoint directory to continue training from. If not set, training starts fresh.'
)

args = parser.parse_args()
checkpoint = args.checkpoint


if __name__ == "__main__":
    # one hot encoded feature length
    ohc_feature_len = len(types.all_types) + 1
    action_encoding_dim = 32
    state_encoding_dim = 64

    # Initialize models
    action_encoder = ActionEncoder(
        input_dim=3, hidden_dim=64, output_dim=action_encoding_dim)
    graph_encoder = GraphEncoder(
        in_channels=ohc_feature_len, hidden_channels=state_encoding_dim)
    code_predicter = CodePredicter(
        state_dim=state_encoding_dim, action_dim=action_encoding_dim)
    carrying_value_predicter = CarryingValuePredicter(
        state_dim=state_encoding_dim, action_dim=action_encoding_dim)
    optimizer = torch.optim.Adam(list(code_predicter.parameters()) +
                                 list(action_encoder.parameters()) +
                                 list(graph_encoder.parameters()) +
                                 list(carrying_value_predicter.parameters()),
                                 lr=1e-3)
    loss_fn = nn.MSELoss()

    # Initialize Environments
    GEMService.add_env("EXP_OUTPUT_ENV")
    expected_output_env = Environment.from_list([[0, 0, 0],
                                                [1, 0, 0]])
    GEMService.set("EXP_OUTPUT_ENV", expected_output_env)

    start_episode = 0
    tracking_obj = {}
    tracking_obj["reward_tracking"] = []
    tracking_obj["memory_usage"] = []
    tracking_obj["restart_episode_indices"] = []
    tracking_obj["episode_times"] = []

    # Load checkpoint if provided
    if checkpoint is not None:
        loaded_checkpoint = torch.load(f"storage/{checkpoint}.pth")

        start_episode = loaded_checkpoint["episode"]
        # todo rename key
        tracking_obj = loaded_checkpoint["tracking_obj"]
        # tracking at which episodes a restart was done
        tracking_obj["restart_episode_indices"] += [
            start_episode]

        action_encoder.load_state_dict(loaded_checkpoint["action_encoder"])
        graph_encoder.load_state_dict(loaded_checkpoint["graph_encoder"])
        code_predicter.load_state_dict(loaded_checkpoint["code_predicter"])
        carrying_value_predicter.load_state_dict(
            loaded_checkpoint["carrying_value_predicter"])

        optimizer.load_state_dict(loaded_checkpoint["optimizer"])

    # Configurable parameter: how much to rely on model vs. random (epsilon-greedy)
    rely_on_model_weight = 0.7  # 1.0 = always model, 0.0 = always random
    num_episodes = 11000
    num_steps = 30

    #####################################################
    #####################################################

    choosing_prep_time = []
    choosing_time = []
    executing_time = []
    executing_and_co = []
    optimizing_time = []

    #####################################################
    #####################################################

    for episode in tqdm(range(start_episode, num_episodes), initial=start_episode, total=num_episodes):

        episode_start_time = time.perf_counter()
        episode_loss = 0.0
        episode_reward = 0.0
        codeblock = Codeblock([])

        # plot_blueprint = hierarchy_plot(start_ast, start_root)
        # labels = nx.get_node_attributes(start_ast, 'label')
        # nx.draw(start_ast, pos=plot_blueprint, labels=labels,
        #         with_labels=True, arrows=True)
        # plt.title(f"Episode {episode+1}")
        # plt.show()

        for step in range(num_steps):

            choosing_prep_start_time = time.perf_counter()
            ast, root = codeblock.to_ast()
            encode_ast_nodes(ast)
            data = from_networkx(ast)
            x = data.x
            edge_index = data.edge_index
            batch = torch.zeros(x.size(0), dtype=torch.long)
            state = graph_encoder(x, edge_index, batch)

            action_space = code_writer.get_action_space(codeblock)
            action_tensor = actions_to_tensor(action_space)
            action_embeddings = action_encoder(action_tensor)

            choosing_prep_time.append(time.perf_counter() -
                                      choosing_prep_start_time)

            choosing_start_time = time.perf_counter()
            chosen_action, best_action_idx = choose_action(
                model=code_predicter,
                rely_on_model_weight=rely_on_model_weight,
                state=state,
                action_embeddings=action_embeddings
            )
            chosen_parent, chosen_type, chosen_order = chosen_action

            # predict carrying value only when needed
            carrying_value = None
            if chosen_type == "constant" or chosen_type == "read_var" or chosen_type == "write_var":
                carrying_value = choose_carrying_value(
                    carrying_value_predicter, state, action_embeddings, best_action_idx)

            choosing_time.append(time.perf_counter() - choosing_start_time)

            # todo make carrying value integer in all nodes
            executing_and_co_start_time = time.perf_counter()
            code_writer.new_node(chosen_parent, chosen_type,
                                 chosen_order, carrying_value)
            reward, skip_episode = code_writer.evaluate(
                codeblock, executing_time)

            executing_and_co.append(
                time.perf_counter() - executing_and_co_start_time)
            episode_reward = reward
            reward = torch.tensor([reward])
            # next_codeblock = apply_action(codeblock, chosen_action)
            # reward = reward_function(next_codeblock)
            # reward = torch.tensor([random.uniform(0, 1)])  # Dummy reward

            # Forward pass for chosen action
            # todo double check if this call is correct
            pred_score = code_predicter(
                state[0], action_embeddings[best_action_idx])

            optimizing_start_time = time.perf_counter()
            loss = loss_fn(pred_score, reward)
            episode_loss = loss.item()

            # Backward pass
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            optimizing_time.append(time.perf_counter() - optimizing_start_time)

            if skip_episode:
                logger.warning(
                    f"Skipping episode {episode+1} due execution timeouts.")
                for _ in range(num_steps - step):
                    choosing_prep_time.append(0)
                    choosing_time.append(0)
                    executing_time.append(0)
                    executing_and_co.append(0)
                    optimizing_time.append(0)
                break

        episode_time = time.perf_counter() - episode_start_time

        # if step % 10 == 0:
        end_ast, end_root = codeblock.to_ast()
        logger.info("========")
        logger.info(
            f"Episode {episode+1}: Loss={episode_loss:.4f}")
        logger.info("--------")
        logger.info(codeblock)
        logger.info(end_ast)
        logger.info(end_root)
        logger.info("-----------------")
        logger.info(f"Threads: {proc.num_threads()}")
        logger.info(f"Speicher: {proc.memory_info().rss / 1024 / 1024:.2f} MB")
        logger.info("--------")
        GEMService.get_initial_env().plot("INITIAL_ENV", print_func=logger.info)
        GEMService.get_output_env().plot("OUTPUT_ENV", print_func=logger.info)
        logger.info("========")

        tracking_obj["reward_tracking"].append(episode_reward)
        tracking_obj["memory_usage"].append(
            proc.memory_info().rss / 1024 / 1024)
        tracking_obj["episode_times"].append(
            time.perf_counter() - episode_start_time)

        if episode % 100 == 0:
            torch.save({
                "episode": episode,
                "tracking_obj": tracking_obj,
                "action_encoder": action_encoder.state_dict(),
                "graph_encoder": graph_encoder.state_dict(),
                "code_predicter": code_predicter.state_dict(),
                "carrying_value_predicter": carrying_value_predicter.state_dict(),
                "optimizer": optimizer.state_dict()
            }, f"storage/episode_{episode+1}.pth")

        # plot_blueprint = hierarchy_plot(end_ast, end_root)
        # labels = nx.get_node_attributes(end_ast, 'label')
        # nx.draw(end_ast, pos=plot_blueprint, labels=labels,
        #         with_labels=True, arrows=True)
        # plt.title(f"Episode {episode+1}")
        # plt.show()

    # Save reward_tracking to a file

    report_output_name = f"reporting/data_repo/tracking_obj_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_output_name, "w") as f:
        json.dump(tracking_obj, f, indent=2)

    logger.info(f"Reward tracking saved to '{report_output_name}'")
    logger.info("---------------------------------")

    import matplotlib.pyplot as plt

    # Convert timing lists to numpy arrays for easier slicing
    choosing_prep_time = np.array(choosing_prep_time)
    choosing_time = np.array(choosing_time)
    executing_time = np.array(executing_time)
    executing_and_co = np.array(executing_and_co)
    optimizing_time = np.array(optimizing_time)

    # Calculate episode boundaries
    episode_indices = np.arange(0, len(choosing_prep_time), num_steps)
    num_episodes_recorded = len(episode_indices)

    # Prepare averages per episode
    avg_choosing_prep = []
    avg_choosing = []
    avg_executing = []
    avg_executing_and_co = []
    avg_optimizing = []

    for i in range(num_episodes_recorded):
        start = episode_indices[i]
        end = episode_indices[i] + num_steps
        avg_choosing_prep.append(choosing_prep_time[start:end].mean())
        avg_choosing.append(choosing_time[start:end].mean())
        avg_executing.append(executing_time[start:end].mean())
        avg_executing_and_co.append(executing_and_co[start:end].mean())
        avg_optimizing.append(optimizing_time[start:end].mean())

    plt.figure(figsize=(15, 6))
    plt.plot(choosing_prep_time, label='Choosing Prep', color='blue')
    plt.plot(choosing_time, label='Choosing', color='orange')
    plt.plot(executing_time, label='Executing', color='green')
    plt.plot(executing_and_co, label='Executing & Co.', color='purple')
    plt.plot(optimizing_time, label='Optimizing', color='red')

    # Draw horizontal lines for each episode
    for idx in episode_indices:
        plt.axvline(x=idx, color='gray', linestyle='--', alpha=0.3)

    # Plot averages as horizontal lines
    for i, idx in enumerate(episode_indices):
        plt.hlines(avg_choosing_prep[i], idx, idx+num_steps,
                   colors='blue', linestyles='dashed', label=None)
        plt.hlines(avg_choosing[i], idx, idx+num_steps,
                   colors='orange', linestyles='dashed', label=None)
        plt.hlines(avg_executing[i], idx, idx+num_steps,
                   colors='green', linestyles='dashed', label=None)
        plt.hlines(avg_executing_and_co[i], idx, idx+num_steps,
                   colors='purple', linestyles='dashed', label=None)
        plt.hlines(avg_optimizing[i], idx, idx+num_steps,
                   colors='red', linestyles='dashed', label=None)

    plt.legend()
    plt.xlabel('Step')
    plt.ylabel('Time (seconds)')
    plt.title('Timing per Step and Episode Averages')
    plt.tight_layout()
    plt.show()
