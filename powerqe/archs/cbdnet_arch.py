import torch
from torch import nn as nn

from .unet_arch import UNet
from .registry import ARCH_REGISTRY


@ARCH_REGISTRY.register()
class CBDNet(nn.Module):
    """CBDNet network structure.

    Args:
        io_channels (int): Number of I/O channels.
        estimate_channels (int): Channel number of the features in the estimation module.
        nlevel_denoise (int): Level number of UNet for denoising.
        nf_base_denoise (int): Base channel number of the features in the denoising module.
        nf_gr_denoise (int): Growth rate of the channel number in the denoising module.
        nl_base_denoise (int): Base convolution layer number in the denoising module.
        nl_gr_denoise (int): Growth rate of the convolution layer number in the denoising module.
        down_denoise (str): Downsampling method in the denoising module.
        up_denoise (str): Upsampling method in the denoising module.
        reduce_denoise (str): Reduction method for the guidance/feature maps in the denoising module.
    """

    def __init__(
        self,
        io_channels=3,
        estimate_channels=32,
        nlevel_denoise=3,
        nf_base_denoise=64,
        nf_gr_denoise=2,
        nl_base_denoise=1,
        nl_gr_denoise=2,
        down_denoise="avepool2d",
        up_denoise="transpose2d",
        reduce_denoise="add",
    ):
        super().__init__()

        estimate_list = nn.ModuleList(
            [
                nn.Conv2d(
                    in_channels=io_channels,
                    out_channels=estimate_channels,
                    kernel_size=3,
                    padding=3 // 2,
                ),
                nn.ReLU(inplace=True),
            ]
        )
        for _ in range(3):
            estimate_list += nn.ModuleList(
                [
                    nn.Conv2d(
                        in_channels=estimate_channels,
                        out_channels=estimate_channels,
                        kernel_size=3,
                        padding=3 // 2,
                    ),
                    nn.ReLU(inplace=True),
                ]
            )
        estimate_list += nn.ModuleList(
            [
                nn.Conv2d(estimate_channels, io_channels, 3, padding=3 // 2),
                nn.ReLU(inplace=True),
            ]
        )
        self.estimate = nn.Sequential(*estimate_list)

        self.denoise = UNet(
            nf_in=io_channels * 2,
            nf_out=io_channels,
            nlevel=nlevel_denoise,
            nf_base=nf_base_denoise,
            nf_gr=nf_gr_denoise,
            nl_base=nl_base_denoise,
            nl_gr=nl_gr_denoise,
            down=down_denoise,
            up=up_denoise,
            reduce=reduce_denoise,
            residual=False,
        )

    def forward(self, x):
        """
        Args:
            x (Tensor): Input tensor with the shape of (N, C, H, W).

        Returns:
            Tensor
        """
        estimated_noise_map = self.estimate(x)
        res = self.denoise(torch.cat([x, estimated_noise_map], dim=1))
        out = res + x
        return out
