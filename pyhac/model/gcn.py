import torch
import torch.nn as nn
import torch.nn.functional as F

class GCN(nn.Module):
    def __init__(self, in_channels, out_channels, k_hop):
        super().__init__()
        
        self.conv = nn.Conv2d(in_channels,
                              out_channels * k_hop,
                              kernel_size=(1, 1),
                              padding=(0, 0),
                              stride=(1, 1))
        
        if in_channels == out_channels:
            self.residual = lambda x: x

        else:
            self.residual = nn.Sequential(
                nn.Conv2d(
                    in_channels,
                    out_channels,
                    kernel_size=1,
                    stride=(1, 1)),
                nn.BatchNorm2d(out_channels),
            )
        
    def forward(self, x, A_k):
        
        res = self.residual(x)
        
        B, F, J, T = x.size()
        
        K = A_k.size()[0]
        
        x = self.conv(x)
        B, KC, J, T = x.size()
        
        x = x.view(B, K, KC // K, J, T)
        output = torch.einsum('bkcjt,kji->bcit', (x, A_k)).contiguous() + res
        
        return output