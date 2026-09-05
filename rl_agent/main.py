"""
main.py - RL agent for evolving ASTs to solve pixel riddles
Modern architecture: Graph Transformer + PPO
"""

import os
import sys

from matplotlib import pyplot as plt

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import code_writer
from logging_setup import setup_logger
from instruction_language.elements.base import Codeblock
from instruction_language.elements import types
from instruction_language.ast_transformer import encode_ast_nodes, hierarchy_plot
import networkx as nx
import json
import random
import numpy as np
from torch_geometric.utils import from_networkx
from torch_geometric.nn import GATConv, global_mean_pool
import torch.nn.functional as F
import torch.nn as nn
import torch
from datetime import datetime
import psutil
import time
import logging
from tqdm import tqdm


# Logging setup
logger = setup_logger(
    "main", level=logging.INFO, log_file="logs/main.log", to_console=False
)

if not os.path.exists("storage"):
    os.makedirs("storage")

proc = psutil.Process(os.getpid())

# Checkpoint setup
CHECKPOINT_DIR = os.path.join(os.path.dirname(__file__), "storage/rl_agent")
if not os.path.exists(CHECKPOINT_DIR):
    os.makedirs(CHECKPOINT_DIR)

REPORT_DIR = os.path.join(os.path.dirname(__file__), "reporting/rl_agent/data_repo")
if not os.path.exists(REPORT_DIR):
    os.makedirs(REPORT_DIR)


# Tracking setup
tracking_obj = {
    "reward_tracking": [],
    "memory_usage": [],
    "episode_times": [],
    "restart_episode_indices": [],
}

# Model definitions


class GraphTransformerEncoder(nn.Module):
    def __init__(self, in_channels, hidden_channels, heads=4):
        super().__init__()
        self.gat1 = GATConv(in_channels, hidden_channels, heads=heads)
        self.gat2 = GATConv(hidden_channels * heads, hidden_channels, heads=1)

    def forward(self, x, edge_index, batch):
        x = F.relu(self.gat1(x, edge_index))
        x = F.relu(self.gat2(x, edge_index))
        graph_repr = global_mean_pool(x, batch)
        return graph_repr


class ActionEncoder(nn.Module):
    def __init__(self, input_dim=3, hidden_dim=64, output_dim=32):
        super().__init__()
        self.fc = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, output_dim),
        )

    def forward(self, action_tensor):
        return self.fc(action_tensor)


class PPOPolicy(nn.Module):
    def __init__(self, state_dim, action_dim):
        super().__init__()
        self.fc = nn.Sequential(
            nn.Linear(state_dim + action_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 1),  # Output: action logit
        )

    def forward(self, state_embedding, action_embedding):
        # Expand state_embedding only for action selection (not PPO batch update)
        if (
            state_embedding.dim() == 2
            and state_embedding.size(0) == 1
            and action_embedding.dim() == 2
            and action_embedding.size(0) > 1
        ):
            state_embedding = state_embedding.expand(action_embedding.size(0), -1)
        x = torch.cat([state_embedding, action_embedding], dim=-1)
        return self.fc(x)


class PPOValue(nn.Module):
    def __init__(self, state_dim):
        super().__init__()
        self.fc = nn.Sequential(nn.Linear(state_dim, 128), nn.ReLU(), nn.Linear(128, 1))

    def forward(self, state_embedding):
        return self.fc(state_embedding)


def actions_to_tensor(action_space, ast: nx.DiGraph):
    action_tensor = []
    for node, n_type, order in action_space:
        # todo maybe add parent node_type to action space
        node_idx = list(ast.nodes).index(node)
        action_tensor.append([node_idx, types.t2int[n_type], order])

    return torch.tensor(action_tensor, dtype=torch.float)


# Placeholder for environment and AST logic
# You should implement or import your own environment, AST, and reward logic


class DummyEnv:
    def __init__(self):
        self.current_state = Codeblock()

    def reset(self):
        self.current_state = Codeblock()
        return self.current_state

    def step(self, chosen_action, carrying_value=None):
        # Apply action, return next_state, reward, done, info
        chosen_parent, chosen_type, chosen_order = chosen_action
        # Predict or select carrying_value if needed
        if chosen_type in ["constant", "read_var", "write_var"]:
            if carrying_value is None:
                # Random for now, can be replaced with model prediction
                carrying_value = random.randint(0, 50)
        else:
            carrying_value = None
        try:
            code_writer.new_node(
                chosen_parent, chosen_type, chosen_order, carrying_value
            )
            reward, skip_episode = code_writer.evaluate(self.current_state, [])
            done = reward == 1.0
        except Exception as e:
            reward, skip_episode, done = 0.0, True, True
            logger.warning(f"Error in env.step: {e}")
        return reward, skip_episode, done


def main():
    # Hyperparameters
    ohc_feature_len = len(types.all_types) + 1
    action_encoding_dim = 32
    state_encoding_dim = 64
    num_episodes = 100000
    num_steps = 30
    ppo_epochs = 4
    batch_size = 16
    gamma = 0.99
    lr = 1e-3

    # Models
    graph_encoder = GraphTransformerEncoder(ohc_feature_len, state_encoding_dim)
    action_encoder = ActionEncoder(
        input_dim=3, hidden_dim=64, output_dim=action_encoding_dim
    )
    policy = PPOPolicy(state_encoding_dim, action_encoding_dim)
    value = PPOValue(state_encoding_dim)
    optimizer = torch.optim.Adam(
        list(graph_encoder.parameters())
        + list(action_encoder.parameters())
        + list(policy.parameters())
        + list(value.parameters()),
        lr=lr,
    )

    env = DummyEnv()

    batch_episodes = 8
    all_memory = []
    for episode in tqdm(range(num_episodes), desc="Episodes", total=num_episodes):
        episode_start_time = time.perf_counter()
        codeblock = env.reset()
        episode_reward = 0.0
        memory = []  # For PPO
        for step in range(num_steps):
            ast, root = codeblock.to_ast()
            encode_ast_nodes(ast)
            data = from_networkx(ast)
            x = data.x
            edge_index = data.edge_index
            batch = torch.zeros(x.size(0), dtype=torch.long)

            # Get state embedding as [1, state_dim]
            state_emb = graph_encoder(x, edge_index, batch)
            # Get action embeddings as [num_actions, action_dim]
            action_space = code_writer.get_action_space(codeblock)
            action_tensor = actions_to_tensor(action_space, ast)
            action_embs = action_encoder(action_tensor)
            # Score all actions for current state
            # Epsilon-greedy: choose random action with probability epsilon, else use policy
            epsilon = max(
                0.5 * (1 - episode / num_episodes), 0.05
            )  # Decay from 0.5 to 0.05
            if random.random() < epsilon:
                action_idx = random.randint(0, len(action_space) - 1)
            else:
                logits = policy(state_emb, action_embs)
                action_probs = torch.softmax(logits.squeeze(-1), dim=0)
                action_idx = torch.multinomial(action_probs, 1)[0].item()
            action = action_space[action_idx]

            # Carrying value prediction
            carrying_value = None
            if action[1] in ["constant", "read_var", "write_var"]:
                carrying_value = random.randint(0, 50)

            reward, skip_episode, done = env.step(action, carrying_value)
            # Store state and action embedding as 1D tensors for PPO batch
            memory.append(
                (
                    state_emb.squeeze(0).detach(),
                    action_embs[action_idx].detach(),
                    reward,
                    done,
                )
            )
            episode_reward += reward
            if done or skip_episode:
                break
        all_memory.extend(memory)
        episode_time = time.perf_counter() - episode_start_time
        tracking_obj["reward_tracking"].append(episode_reward)
        tracking_obj["episode_times"].append(episode_time)
        tracking_obj["memory_usage"].append(proc.memory_info().rss / 1024 / 1024)
        logger.info(
            f"Episode {episode+1}: Reward={episode_reward:.4f} Time={episode_time:.2f}s"
        )

        # print_ast, print_root = codeblock.to_ast()
        # plot_blueprint = hierarchy_plot(print_ast, print_root)
        # labels = nx.get_node_attributes(print_ast, "label")
        # nx.draw(
        #     print_ast, pos=plot_blueprint, labels=labels, with_labels=True, arrows=True
        # )
        # plt.title(f"Episode {episode+1}")
        # plt.show()

        # PPO update every batch_episodes
        if (episode + 1) % batch_episodes == 0:
            # Prepare batch
            states = torch.stack([m[0] for m in all_memory])  # [batch_size, state_dim]
            actions = torch.stack(
                [m[1] for m in all_memory]
            )  # [batch_size, action_dim]
            rewards = torch.tensor([m[2] for m in all_memory], dtype=torch.float)
            dones = torch.tensor([m[3] for m in all_memory], dtype=torch.float)
            # Compute returns (simple discounted sum)
            returns = []
            R = 0
            for r, d in zip(reversed(rewards), reversed(dones)):
                R = r + gamma * R * (1 - d)
                returns.insert(0, R)
            returns = torch.tensor(returns, dtype=torch.float)
            # PPO loss (simplified)
            values = value(states)
            advantages = returns - values.squeeze(-1)
            logits = policy(states, actions).squeeze(-1)
            action_log_probs = torch.log_softmax(logits, dim=0)
            policy_loss = -(advantages.detach() * action_log_probs).mean()
            value_loss = F.mse_loss(values.squeeze(-1), returns)
            loss = policy_loss + value_loss
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            all_memory = []
        if episode % 100 == 0:
            torch.save(
                {
                    "episode": episode,
                    "tracking_obj": tracking_obj,
                    "graph_encoder": graph_encoder.state_dict(),
                    "action_encoder": action_encoder.state_dict(),
                    "policy": policy.state_dict(),
                    "value": value.state_dict(),
                    "optimizer": optimizer.state_dict(),
                },
                os.path.join(CHECKPOINT_DIR, f"rl_agent_episode_{episode+1}.pth"),
            )
    # Save tracking
    report_output_name = f"{REPORT_DIR}/rl_agent_tracking_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_output_name, "w") as f:
        json.dump(tracking_obj, f, indent=2)
    logger.info(f"Tracking saved to '{report_output_name}'")


if __name__ == "__main__":
    main()
# todo test
# todo test
# todo test
# todo test
# todo test
# todo test
# todo test
