from copy import deepcopy

from basicsr.utils import get_root_logger

from .arcnn_arch import ARCNN
from .cbdnet_arch import CBDNet
from .dcad_arch import DCAD
from .dncnn_arch import DnCNN
from .identitynet_arch import IdentityNet
from .mprnet_arch import MPRNet
from .rbqe_arch import RBQE
from .rdn_arch import RDN
from .registry import ARCH_REGISTRY
from .unet_arch import UNet

__all__ = [
    "ARCNN",
    "CBDNet",
    "DCAD",
    "DnCNN",
    "IdentityNet",
    "MPRNet",
    "RBQE",
    "RDN",
    "build_network",
    "ARCH_REGISTRY",
    "UNet",
]


def build_network(opt):
    opt = deepcopy(opt)
    network_type = opt.pop("type")
    net = ARCH_REGISTRY.get(network_type)(**opt)
    logger = get_root_logger()
    logger.info(f"Network [{net.__class__.__name__}] is created.")
    return net
