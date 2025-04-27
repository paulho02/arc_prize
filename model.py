import torch
from torch import nn
from torchrl.envs.utils import ParallelEnv
# from torchrl.data.replay_buffers import ReplayBuffer
# from torchrl.modules import MLP
# from torchrl.data import TensorDict

# # Define the environment
# class SequenceEnv:
#     def __init__(self):
#         self.state = 0  # Initialize starting number

#     def reset(self):
#         self.state = 0
#         return torch.tensor([self.state], dtype=torch.float32)

#     def step(self, action):
#         correct_action = self.state + 2
#         reward = 1 if action == correct_action else -1
#         self.state = correct_action
#         done = False
#         return torch.tensor([self.state], dtype=torch.float32), reward, done, {}

# # Define the agent (a simple MLP model)
# class SimpleAgent(nn.Module):
#     def __init__(self):
#         super().__init__()
#         self.model = nn.Sequential(
#             nn.Linear(1, 16),
#             nn.ReLU(),
#             nn.Linear(16, 1)  # Output next number prediction
#         )

#     def forward(self, x):
#         return self.model(x)

# # Initialize environment and agent
# env = SequenceEnv()
# agent = SimpleAgent()

# # Define optimizer and loss function
# optimizer = torch.optim.Adam(agent.parameters(), lr=0.01)
# loss_fn = nn.MSELoss()

# # Training loop
# for episode in range(100):  # Number of training episodes
#     state = env.reset()
#     episode_loss = 0

#     for step in range(10):  # Steps per episode
#         prediction = agent(state)
#         action = prediction.round().item()

#         next_state, reward, done, _ = env.step(action)

#         # Compute loss
#         target = next_state  # Correct next number
#         loss = loss_fn(prediction, target)
#         episode_loss += loss.item()

#         # Backpropagation
#         optimizer.zero_grad()
#         loss.backward()
#         optimizer.step()

#         state = next_state

#     print(f"Episode {episode + 1}, Loss: {episode_loss:.4f}")

# print("Training complete!")
