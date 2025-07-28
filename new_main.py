import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.data import Data, DataLoader
from torch_geometric.nn import GCNConv, global_mean_pool
from torch_geometric.utils import from_networkx
import torch.nn.functional as F

from matplotlib import pyplot as plt
import networkx as nx

import code_writer
from instruction_language.ast_transformer import encode_ast_nodes, hierarchy_plot
from instruction_language.elements import types
from instruction_language.elements.base import Codeblock
import random

from instruction_language.interpreter import InstructionInterpreter
from instruction_language.surroundings.environment import Environment, GEMService


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


node2int = []


def actions_to_tensor(action_space):
    action_tensor = []
    for node, n_type, order in action_space:
        if node not in node2int:
            node2int.append(node)
        node_idx = node2int.index(node)
        action_tensor.append([node_idx, types.t2int[n_type], order])

    return torch.tensor(action_tensor, dtype=torch.float)


# def execute_codeblock(codeblock: Codeblock):
#     initial_env = Environment.from_list([[1, 1, 1],
#                                         [0, 1, 1]])
#     GEMService.set(0, initial_env)
#     GEMService.set(1, Environment())

#     interpreter = InstructionInterpreter(memory_manager_id='production_mm_id')

#     try:
#         interpreter.execute(codeblock)

#     except Exception as e:
#         print(f"Codeblock execution failed with: {e} || -> return min reward")


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

    # Initialize Environments
    GEMService.add_env(0)
    initial_env = Environment.from_list([[1, 1, 1],
                                        [0, 1, 1]])
    GEMService.set(0, initial_env)
    GEMService.add_env(1)
    GEMService.add_env("EXP_OUTPUT_ENV")
    expected_output_env = Environment.from_list([[0, 0, 0],
                                                [1, 0, 0]])
    GEMService.set("EXP_OUTPUT_ENV", expected_output_env)

    # Initialize Codeblock

    # Configurable parameter: how much to rely on model vs. random (epsilon-greedy)
    rely_on_model_weight = 0.7  # 1.0 = always model, 0.0 = always random

    optimizer = torch.optim.Adam(code_predicter.parameters(), lr=1e-3)
    loss_fn = nn.MSELoss()

    num_episodes = 30  # For demonstration
    for episode in range(num_episodes):

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

        # Choose action: epsilon-greedy
        if random.random() < rely_on_model_weight:
            # Model chooses best action
            scores = []
            for i in range(action_embeddings.size(0)):
                score = code_predicter(state[0], action_embeddings[i])
                scores.append(score.item())
            best_action_idx = int(torch.tensor(scores).argmax())
        else:
            # Random action
            best_action_idx = random.randint(0, action_embeddings.size(0) - 1)

        # Apply action to get next state (simulate environment step)
        # (Assume you have a function: next_codeblock = apply_action(codeblock, chosen_action))
        # (Assume you have a function: reward = reward_function(next_codeblock))
        # For demonstration, we'll just use the same state and a dummy reward
        # Replace the following two lines with your environment logic:

        chosen_action = action_space[best_action_idx]
        chosen_parent, chosen_type, chosen_order = chosen_action
        code_writer.new_node(chosen_parent, chosen_type, chosen_order)
        reward = code_writer.evaluate(codeblock)
        reward = torch.tensor([reward])
        # next_codeblock = apply_action(codeblock, chosen_action)
        # reward = reward_function(next_codeblock)
        # reward = torch.tensor([random.uniform(0, 1)])  # Dummy reward

        # Forward pass for chosen action
        pred_score = code_predicter(
            state[0], action_embeddings[best_action_idx])

        # Loss (MSE between predicted score and reward)
        loss = loss_fn(pred_score, reward)

        # Backward pass
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        print(
            f"Episode {episode+1}: Loss={loss.item():.4f}, Reward={reward.item():.4f}, ActionIdx={best_action_idx}")

        if episode % 10 == 0:
            plot_blueprint = hierarchy_plot(ast, root)
            labels = nx.get_node_attributes(ast, 'label')
            nx.draw(ast, pos=plot_blueprint, labels=labels,
                    with_labels=True, arrows=True)
            plt.show()

        # todo in trainings phase: auf endlosschleifen aufpassen
