import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.data import Data, DataLoader
from torch_geometric.nn import GCNConv, global_mean_pool

"""
The purpose of this file is to implement a simple GNN example for learning, illustrating and testing the basic functionality of a GNN.
Its totally unralted to the main use case of this project
"""


class GraphEncoder(nn.Module):
    def __init__(self, in_channels, hidden_channels):
        super().__init__()
        self.conv1 = GCNConv(in_channels, hidden_channels)
        self.conv2 = GCNConv(hidden_channels, hidden_channels)

    def forward(self, x, edge_index, batch):
        print(f"[Encoder] Eingabe x.shape: {x.shape}")
        x = F.relu(self.conv1(x, edge_index))
        x = F.relu(self.conv2(x, edge_index))
        graph_repr = global_mean_pool(x, batch)
        print(f"[Encoder] Ausgabe (Graph-Embeddings): {graph_repr.shape}")
        return graph_repr


class MoleculeClassifier(nn.Module):
    def __init__(self, in_channels, hidden_channels):
        super().__init__()
        self.encoder = GraphEncoder(in_channels, hidden_channels)
        self.classifier = nn.Linear(hidden_channels, 1)

    def forward(self, x, edge_index, batch):
        emb = self.encoder(x, edge_index, batch)
        out = self.classifier(emb)
        prob = torch.sigmoid(out)
        print(
            f"[Classifier] Wahrscheinlichkeit für toxisch: {prob.squeeze().detach().numpy()}")
        return prob


# Molekül 1: ungiftig
x1 = torch.tensor([[1, 0], [1, 0], [0, 1]], dtype=torch.float)  # 2x H, 1x O
edge_index1 = torch.tensor([[0, 2, 1, 2], [2, 0, 2, 1]], dtype=torch.long)
data1 = Data(x=x1, edge_index=edge_index1, y=torch.tensor([0]))

# Molekül 2: giftig
x2 = torch.tensor([[0, 1], [0, 1], [1, 0]], dtype=torch.float)  # 2x O, 1x H
edge_index2 = torch.tensor([[0, 2, 1, 2], [2, 0, 2, 1]], dtype=torch.long)
data2 = Data(x=x2, edge_index=edge_index2, y=torch.tensor([1]))

loader = DataLoader([data1, data2], batch_size=2)

model = MoleculeClassifier(in_channels=2, hidden_channels=4)
optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
loss_fn = nn.BCELoss()

for epoch in range(1, 100):
    for batch in loader:
        optimizer.zero_grad()
        out = model(batch.x, batch.edge_index, batch.batch)
        loss = loss_fn(out.squeeze(), batch.y.float())
        loss.backward()
        optimizer.step()

        print(f"[Epoch {epoch}] Loss: {loss.item():.4f}")
    print("---------------------------------------")

print()
print("Training ended")
print("Test with unknown molecule:")

x_new = torch.tensor([[0, 1], [0, 1], [0, 1], [0, 1]],
                     dtype=torch.float)  # 4x O
edge_index_new = torch.tensor([[0, 2, 1, 2], [2, 0, 2, 1]], dtype=torch.long)
data_new = Data(x=x_new, edge_index=edge_index_new)
loader_new = DataLoader([data_new], batch_size=1)

for batch in loader_new:
    model(batch.x, batch.edge_index, batch.batch)
