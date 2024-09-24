from copy import deepcopy

from basicsr.utils import get_root_logger

from .identitynet_arch import IdentityNet
from .registry import ARCH_REGISTRY
from .cbdnet_arch import CBDNet
from .unet_arch import UNet

__all__ = ["build_network", "ARCH_REGISTRY", "IdentityNet", "CBDNet", "UNet"]


def build_network(opt):
    opt = deepcopy(opt)
    network_type = opt.pop("type")
    net = ARCH_REGISTRY.get(network_type)(**opt)
    logger = get_root_logger()
    logger.info(f"Network [{net.__class__.__name__}] is created.")
    return net
