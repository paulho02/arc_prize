import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import MessagePassing, global_mean_pool
from torch_geometric.nn import GCNConv  # einfacher als Start
from torch_geometric.data import Data, Batch
from torch.distributions import Categorical
from torch_geometric.utils import from_networkx
from tqdm import tqdm
import code_writer
from instruction_language.ast_transformer import encode_ast_nodes
from instruction_language.elements import types
from instruction_language.elements.base import Codeblock


class GraphEncoder(nn.Module):
    def __init__(self, in_channels, hidden_channels):
        super().__init__()
        self.conv1 = GCNConv(in_channels, hidden_channels)
        self.conv2 = GCNConv(hidden_channels, hidden_channels)

    def forward(self, x, edge_index, batch):
        x = F.relu(self.conv1(x, edge_index))
        x = F.relu(self.conv2(x, edge_index))
        graph_repr = global_mean_pool(x, batch)  # [batch_size, hidden_dim]
        return graph_repr


class PolicyOld(nn.Module):
    def __init__(self, embedding_dim, action_dim):
        super().__init__()
        self.fc1 = nn.Linear(embedding_dim, 64)
        self.action_head = nn.Linear(64, action_dim)
        # regression head for carrying_value
        self.value_head = nn.Linear(64, 1)

    def forward(self, graph_embed):
        x = F.relu(self.fc1(graph_embed))
        logits = self.action_head(x)
        value = self.value_head(x)
        return logits, value


class Policy(nn.Module):
    def __init__(self, embedding_dim):
        super().__init__()
        self.fc1 = nn.Linear(embedding_dim, 64)
        self.value_head = nn.Linear(64, 1)

    def forward(self, graph_embed, action_candidates_embed):
        x = F.relu(self.fc1(graph_embed))  # [batch, 64]

        # Vergleiche Embedding mit allen möglichen Aktionen
        # z. B. per dot product oder MLP:
        logits = torch.matmul(action_candidates_embed,
                              x.T).T  # [batch, num_actions]
        value = self.value_head(x)  # scalar regression

        return logits, value


def encode_action_space(action_space):
    encoded_actions = []

    for parent_node, n_type, order in action_space:
        type_idx = types.t2int[n_type]  # One-hot or int encoding
        parent_id = parent_node.id if hasattr(
            parent_node, "id") else 0  # todo Use rework ID logic
        order_val = order

        # Simple example: concat as tensor [type_idx, parent_id, order_val]
        action_tensor = torch.tensor(
            [type_idx, parent_id, order_val], dtype=torch.float)
        encoded_actions.append(action_tensor)

    return torch.stack(encoded_actions)  # Shape: [num_actions, feature_dim]


one_hot_encoded_feature_len = len(types.all_types) + 1

encoder = GraphEncoder(
    in_channels=one_hot_encoded_feature_len, hidden_channels=64)
policy_net = Policy(embedding_dim=64)
optimizer = torch.optim.Adam(
    list(encoder.parameters()) + list(policy_net.parameters()), lr=1e-3)

for episode in tqdm(range(1000), total=1000):
    codeblock = Codeblock()

    ast, root = codeblock.to_ast()
    done = False
    rewards = []

    while not done:
        encode_ast_nodes(ast)
        data = from_networkx(ast)
        x = data.x
        edge_index = data.edge_index
        # Assuming single graph
        batch = torch.zeros(x.size(0), dtype=torch.long)

        added_nodes = 0
        with torch.no_grad():
            embed = encoder(x, edge_index, batch)

        action_space = code_writer.get_action_space(codeblock)
        action_space_tensor = encode_action_space(action_space)

        logits = policy_net(embed, action_space_tensor)
        dist = Categorical(logits=logits)
        action = dist.sample()
        # If action is an index, fetch the corresponding action from the action_space
        selected_action = action_space[int(action.item())]

        parent_node, n_type, order = selected_action
        carrying_value = None
        code_writer.new_node(parent_node, n_type, order, carrying_value)

        reward = code_writer.evaluate(codeblock)
        rewards.append(reward)

        # Policy-Update z. B. via REINFORCE:
        loss = -dist.log_prob(action) * reward
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        if added_nodes >= 50:
            done = True
        else:
            added_nodes += 1
