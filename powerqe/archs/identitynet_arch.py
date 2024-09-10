from torch import nn as nn
from torch.nn import functional as F

from .registry import ARCH_REGISTRY


@ARCH_REGISTRY.register()
class IdentityNet(nn.Module):
    """Identity network used for testing benchmarks (in tensors). Support up-scaling."""

    def __init__(self, scale=1, upscale_mode="nearest"):
        super(IdentityNet, self).__init__()
        self.scale = scale
        self.upscale_mode = upscale_mode

    def forward(self, x):
        if self.scale != 1:
            x = F.interpolate(x, scale_factor=self.scale, mode=self.upscale_mode)
        return x
