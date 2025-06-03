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

# -----------------------------------------------
# Graph Encoder (Graph Neural Network)
# -----------------------------------------------


class GraphEncoder(nn.Module):
    def __init__(self, input_dim, hidden_dim, output_dim):
        super(GraphEncoder, self).__init__()
        # Use GAT for better learning
        self.conv1 = pyg.nn.GATConv(input_dim, hidden_dim)
        self.conv2 = pyg.nn.GATConv(hidden_dim, output_dim)

    def forward(self, x, edge_index):
        x = self.conv1(x, edge_index).relu()
        x = self.conv2(x, edge_index)
        return x


# -----------------------------------------------
# RL Agent - Action Selection
# -----------------------------------------------
class RLAgent:
    def __init__(self, state_dim, action_dim, lr=0.01):
        self.model = GraphEncoder(state_dim, 64, action_dim)
        self.optimizer = optim.Adam(self.model.parameters(), lr=lr)
        self.loss_fn = nn.MSELoss()

    def select_action(self, graph):
        """Selects an action (Add/Remove Node, Modify Node Attributes)"""
        action_type = random.choice(
            ["add_node", "remove_node", "modify_params"])
        node = random.randint(0, graph.x.shape[0] - 1)  # Pick a random node

        if action_type == "add_node":
            new_node_features = torch.rand(
                (1, graph.x.shape[1]))  # Random new node
            return action_type, node, new_node_features
        elif action_type == "remove_node":
            return action_type, node, None
        elif action_type == "modify_params":
            new_params = torch.rand_like(graph.x[node])  # Modify attributes
            return action_type, node, new_params

        return None

    def train(self, graph, action_info, reward, next_graph):
        """Training the RL model using Q-learning (simplified approach)"""
        pred_q = self.model(graph.x, graph.edge_index).sum()
        target_q = reward + 0.99 * \
            self.model(next_graph.x, next_graph.edge_index).sum()
        loss = self.loss_fn(pred_q, target_q)

        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()


# -----------------------------------------------
# Graph Modifier Functions
# -----------------------------------------------
def add_node(graph, node_features):
    """Adds a node and connects it to valid existing nodes."""
    new_node_index = graph.x.shape[0]  # Index for the new node

    # Expand the node feature matrix
    graph.x = torch.cat([graph.x, node_features], dim=0)

    # Ensure valid connections (connect to existing nodes)
    valid_nodes = torch.arange(new_node_index)  # List of valid node indices
    connections = torch.randint(
        0, new_node_index, (2, 2), dtype=torch.long)  # Random connections
    graph.edge_index = torch.cat([graph.edge_index, connections], dim=1)

    return graph


def remove_node(graph, node_index):
    """Removes a node and updates edges safely."""
    if node_index >= graph.x.shape[0]:
        raise ValueError(
            f"Invalid node index {node_index}, graph only has {graph.x.shape[0]} nodes.")

    if graph.x.shape[0] <= 1:  # Prevent deleting the last node
        return graph

    # Remove node features
    mask = torch.ones(graph.x.shape[0], dtype=torch.bool)
    mask[node_index] = False
    graph.x = graph.x[mask]

    # Remove edges linked to the deleted node
    mask_edges = (graph.edge_index[0] != node_index) & (
        graph.edge_index[1] != node_index)
    graph.edge_index = graph.edge_index[:, mask_edges]

    # **Update node indices in edge list** to reflect removal
    graph.edge_index[graph.edge_index > node_index] -= 1  # Shift indices down

    return graph


def modify_node_params(graph, node_index, new_params):
    """Modify node attributes."""
    graph.x[node_index] = new_params
    return graph


# -----------------------------------------------
# Evaluation Function
# -----------------------------------------------
def evaluate_graph(graph):
    """Example metric: We want node degrees close to 3"""
    degrees = torch.bincount(graph.edge_index[0], minlength=graph.x.shape[0])
    score = -torch.sum(torch.abs(degrees - 3)).item()  # Minimize deviation
    return score


# -----------------------------------------------
# Utils
# -----------------------------------------------
def plot_graph(graph):
    # Convert PyG graph to NetworkX format
    graph_nx = to_networkx(graph, to_undirected=True)

    # Draw the graph
    plt.figure(figsize=(8, 6))
    nx.draw(graph_nx, with_labels=True, node_color="lightblue",
            edge_color="gray", node_size=500, font_size=10)
    plt.show()


# -----------------------------------------------
# Training Loop - Reinforcement Learning
# -----------------------------------------------
num_nodes = 5
node_features = torch.rand((num_nodes, 10))
edge_index = torch.tensor([[0, 1, 2, 3, 4], [1, 2, 3, 4, 0]], dtype=torch.long)
graph = Data(x=node_features, edge_index=edge_index)
plot_graph(graph)


agent = RLAgent(state_dim=10, action_dim=num_nodes)

for episode in range(10000):
    action_info = agent.select_action(graph)

    if action_info:
        action_type, node, data = action_info
        if action_type == "add_node":
            graph = add_node(graph, data)
        elif action_type == "remove_node":
            graph = remove_node(graph, node)
        elif action_type == "modify_params":
            graph = modify_node_params(graph, node, data)

    reward = evaluate_graph(graph)
    next_graph = graph.clone()
    agent.train(graph, action_info, reward, next_graph)

    if episode % 1000 == 0:
        print(f"Episode {episode}, Reward: {reward}")
        plot_graph(graph)


print("Training complete!")
