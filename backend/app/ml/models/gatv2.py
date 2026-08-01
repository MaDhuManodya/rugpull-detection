"""
app/ml/models/gatv2.py
Graph Attention Network v2 Module.
Implements dynamic spatial attention as defined in Chapter 3.
"""
import torch
import torch.nn as nn
import torch.nn.functional as F

try:
    from torch_geometric.nn import GATv2Conv
except ImportError:
    pass

class GATv2SpatialEncoder(nn.Module):
    def __init__(
        self, 
        in_channels: int = 22, 
        hidden_channels: int = 128, 
        out_channels: int = 128, 
        heads: int = 4, 
        num_layers: int = 2,
        dropout: float = 0.6
    ):
        super().__init__()
        self.num_layers = num_layers
        self.dropout = dropout
        
        self.convs = nn.ModuleList()
        
        # Input Layer
        self.convs.append(
            GATv2Conv(in_channels, hidden_channels, heads=heads, concat=True, dropout=dropout)
        )
        
        # Hidden Layers
        for _ in range(num_layers - 2):
            self.convs.append(
                GATv2Conv(hidden_channels * heads, hidden_channels, heads=heads, concat=True, dropout=dropout)
            )
            
        # Output Layer (Aggregate heads by averaging, concat=False)
        self.convs.append(
            GATv2Conv(hidden_channels * heads, out_channels, heads=1, concat=False, dropout=dropout)
        )

    def forward(self, x: torch.Tensor, edge_index: torch.Tensor) -> torch.Tensor:
        """
        Computes the spatial embeddings for all nodes.
        x: [num_nodes, in_channels]
        edge_index: [2, num_edges]
        """
        for i in range(self.num_layers - 1):
            x = F.dropout(x, p=self.dropout, training=self.training)
            x = self.convs[i](x, edge_index)
            x = F.elu(x)
            
        # Final layer
        x = F.dropout(x, p=self.dropout, training=self.training)
        embeddings = self.convs[-1](x, edge_index)
        
        return embeddings
