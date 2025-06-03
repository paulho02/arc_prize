import torch
import torch.nn as nn
import torch.optim as optim
import torch_geometric as pyg
from torch_geometric.data import Data
from torch_geometric.utils import to_networkx
import numpy as np
import random
import matplotlib.pyplot as plt
import networkx as nx

# Define a simple GNN model


class GNN(nn.Module):
    def __init__(self, input_dim, hidden_dim, output_dim):
        super(GNN, self).__init__()
        self.conv1 = pyg.nn.GCNConv(input_dim, hidden_dim)
        self.conv2 = pyg.nn.GCNConv(hidden_dim, output_dim)

    def forward(self, x, edge_index):
        x = self.conv1(x, edge_index).relu()
        x = self.conv2(x, edge_index)
        return x

# Define the RL agent


def add_edge(graph, src, dst):
    """Adds an edge between src and dst nodes."""
    new_edge = torch.tensor([[src, dst], [dst, src]],
                            dtype=torch.long)  # Bidirectional edge
    graph.edge_index = torch.cat([graph.edge_index, new_edge], dim=1)
    return graph


def remove_edge(graph, src, dst):
    """Removes an edge between src and dst nodes."""
    mask = ~((graph.edge_index[0] == src) & (graph.edge_index[1] == dst) |
             # Bidirectional removal
             (graph.edge_index[0] == dst) & (graph.edge_index[1] == src))
    graph.edge_index = graph.edge_index[:, mask]
    return graph


class RLAgent:
    def __init__(self, state_dim, action_dim, lr=0.01):
        self.model = GNN(state_dim, 64, action_dim)
        self.optimizer = optim.Adam(self.model.parameters(), lr=lr)
        self.loss_fn = nn.MSELoss()

    def select_action(self, graph):
        # Get node degrees
        degrees = torch.bincount(
            graph.edge_index[0], minlength=graph.x.shape[0])
        target_degree = 3

        # Select node with the largest degree deviation
        node = torch.argmax(torch.abs(degrees - target_degree)).item()

        # Decide to add or remove edges
        if degrees[node] < target_degree:
            # Add edge to a random node
            available_nodes = list(set(range(graph.x.shape[0])) - {node})
            target = random.choice(available_nodes)
            return "add", node, target
        else:
            # Remove edge from an existing connected node
            connected_nodes = graph.edge_index[1][graph.edge_index[0] == node].tolist(
            )
            if connected_nodes:
                target = random.choice(connected_nodes)
                return "remove", node, target
        return None

    def train(self, graph, action_info, reward, next_graph):
        # Simplified Q value estimate
        pred_q = self.model(graph.x, graph.edge_index).sum()
        target_q = reward + 0.99 * \
            self.model(next_graph.x, next_graph.edge_index).sum()
        loss = self.loss_fn(pred_q, target_q)

        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()


def plot_graph(graph):
    # Convert PyG graph to NetworkX format
    graph_nx = to_networkx(graph, to_undirected=True)

    # Draw the graph
    plt.figure(figsize=(8, 6))
    nx.draw(graph_nx, with_labels=True, node_color="lightblue",
            edge_color="gray", node_size=500, font_size=10)
    plt.show()


# Example AST graph representation
num_nodes = 5
edge_index = torch.tensor([[0, 1, 2, 3, 4], [1, 2, 3, 4, 0]], dtype=torch.long)
node_features = torch.rand((num_nodes, 10))  # Random features

# Create PyG Data object
ast_graph = Data(x=node_features, edge_index=edge_index)
plot_graph(ast_graph)

# Initialize RL agent
agent = RLAgent(state_dim=10, action_dim=num_nodes)

# Simulate RL training loop
for episode in range(100):
    action_info = agent.select_action(ast_graph)
    if action_info:
        action_type, src, dst = action_info
        if action_type == "add":
            ast_graph = add_edge(ast_graph, src, dst)
        elif action_type == "remove":
            ast_graph = remove_edge(ast_graph, src, dst)

    # Reward function: reward higher if degrees are close to 3
    degrees = torch.bincount(
        ast_graph.edge_index[0], minlength=ast_graph.x.shape[0])
    reward = -torch.sum(torch.abs(degrees - 3)).item()

    next_graph = ast_graph.clone()
    plot_graph(ast_graph)
    agent.train(ast_graph, action_info, reward, next_graph)

plot_graph(ast_graph)

print("Training complete!")
