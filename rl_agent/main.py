"""
main.py - RL agent for evolving ASTs to solve pixel riddles
Modern architecture: Graph Transformer + PPO
"""
import os
import logging
import time
import psutil
from datetime import datetime
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import GATConv, global_mean_pool
from torch_geometric.utils import from_networkx
import numpy as np
import random
import json
import networkx as nx
import code_writer
from instruction_language.ast_transformer import encode_ast_nodes
from instruction_language.elements import types
from instruction_language.elements.base import Codeblock
from logging_setup import setup_logger

# Logging setup
logger = setup_logger("main", level=logging.INFO,
                      log_file="logs/main.log", to_console=False)

if not os.path.exists("storage"):
    os.makedirs("storage")

proc = psutil.Process(os.getpid())

# Checkpoint setup
CHECKPOINT_DIR = "../storage"
if not os.path.exists(CHECKPOINT_DIR):
    os.makedirs(CHECKPOINT_DIR)

# Tracking setup
tracking_obj = {
    "reward_tracking": [],
    "memory_usage": [],
    "episode_times": [],
    "restart_episode_indices": []
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
            nn.Linear(hidden_dim, output_dim)
        )

    def forward(self, action_tensor):
        return self.fc(action_tensor)


class PPOPolicy(nn.Module):
    def __init__(self, state_dim, action_dim):
        super().__init__()
        self.fc = nn.Sequential(
            nn.Linear(state_dim + action_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 1)  # Output: action logit
        )

    def forward(self, state_embedding, action_embedding):
        x = torch.cat([state_embedding, action_embedding], dim=-1)
        return self.fc(x)


class PPOValue(nn.Module):
    def __init__(self, state_dim):
        super().__init__()
        self.fc = nn.Sequential(
            nn.Linear(state_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 1)
        )

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

    def step(self, chosen_action):
        # Apply action, return next_state, reward, done, info
        chosen_parent, chosen_type, chosen_order = chosen_action
        code_writer.new_node(chosen_parent, chosen_type, chosen_order, 0)
        reward, skip_episode = code_writer.evaluate(self.current_state, [])
        done = reward == 1.0

        return reward, skip_episode, done


def main():
    # Hyperparameters
    ohc_feature_len = len(types.all_types) + 1
    action_encoding_dim = 32
    state_encoding_dim = 64
    num_episodes = 1000
    num_steps = 30
    ppo_epochs = 4
    batch_size = 16
    gamma = 0.99
    lr = 1e-3

    # Models
    graph_encoder = GraphTransformerEncoder(
        ohc_feature_len, state_encoding_dim)
    action_encoder = ActionEncoder(
        input_dim=3, hidden_dim=64, output_dim=action_encoding_dim)
    policy = PPOPolicy(state_encoding_dim, action_encoding_dim)
    value = PPOValue(state_encoding_dim)
    optimizer = torch.optim.Adam(list(graph_encoder.parameters()) +
                                 list(action_encoder.parameters()) +
                                 list(policy.parameters()) +
                                 list(value.parameters()), lr=lr)

    env = DummyEnv()

    for episode in range(num_episodes):
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

            state_emb = graph_encoder(x, edge_index, batch)
            action_space = code_writer.get_action_space(codeblock)
            action_tensor = actions_to_tensor(action_space, ast)
            action_embs = action_encoder(action_tensor)
            logits = policy(state_emb, action_embs)
            action_probs = torch.softmax(logits, dim=0)
            action_idx = torch.multinomial(action_probs, 1).item()
            # action_idx = int(torch.multinomial(action_probs, 1).item())

            action = action_space[action_idx]
            reward, skip_episode, done = env.step(action)
            memory.append((state_emb, action_embs[action_idx], reward, done))
            episode_reward += reward
            # make break logic more fine-grained
            if done or skip_episode:
                break
        # PPO update (placeholder)
        # ...
        episode_time = time.perf_counter() - episode_start_time
        tracking_obj["reward_tracking"].append(episode_reward)
        tracking_obj["episode_times"].append(episode_time)
        logger.info(
            f"Episode {episode+1}: Reward={episode_reward:.4f} Time={episode_time:.2f}s")
        if episode % 100 == 0:
            torch.save({
                "episode": episode,
                "tracking_obj": tracking_obj,
                "graph_encoder": graph_encoder.state_dict(),
                "action_encoder": action_encoder.state_dict(),
                "policy": policy.state_dict(),
                "value": value.state_dict(),
                "optimizer": optimizer.state_dict()
            }, os.path.join(CHECKPOINT_DIR, f"rl_agent_episode_{episode+1}.pth"))
    # Save tracking
    report_output_name = f"../reporting/data_repo/rl_agent_tracking_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_output_name, "w") as f:
        json.dump(tracking_obj, f, indent=2)
    logger.info(f"Tracking saved to '{report_output_name}'")


if __name__ == "__main__":
    main()
