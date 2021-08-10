import torch
import torch.nn as nn
import torch.nn.functional as F
from .graph import Graph
from .gcn import GCN

class HACModel(nn.Module):
    def __init__(self, in_channels, num_class, k_hop, mode):
        super().__init__()
        
        self.in_channels = in_channels
        self.graph = Graph(k_hop=k_hop, mode=mode)
        A_k = torch.tensor(self.graph.A_k,
                           dtype=torch.float32,
                           requires_grad=False)
        self.register_buffer('A_k', A_k)
        
        self.data_bn = nn.BatchNorm2d(in_channels)
        self.gcns = nn.ModuleList((
            GCN(in_channels, 16, k_hop),
            GCN(16, 32, k_hop),
            GCN(32, 64, k_hop),           
        ))
        
        self.edge_importances = nn.ParameterList([
            nn.Parameter(torch.ones(self.A_k.size()))
            for i in self.gcns
        ])
        
        self.fcn = nn.Conv2d(64, num_class, kernel_size=1)
        self.drop_layer = nn.Dropout(p=0.5)
        self.relu = nn.ReLU(inplace=True)

    def forward(self, x):
        x = self.data_bn(x)
        for gcn, importance in zip(self.gcns, self.edge_importances):
            x = gcn(x, self.A_k * importance)
        x = F.avg_pool2d(x, x.size()[2:])
        x = self.drop_layer(x)
        x = self.fcn(x).squeeze()
        #x = self.relu(x)
        return x