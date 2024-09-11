from copy import deepcopy


from basicsr.utils import get_root_logger

from .registry import LOSS_REGISTRY

__all__ = ["build_loss", "LOSS_REGISTRY"]


def build_loss(opt):
    """Build loss from options.

    Args:
        opt (dict): Configuration. It must contain:
            type (str): Model type.
    """
    opt = deepcopy(opt)
    loss_type = opt.pop("type")
    loss = LOSS_REGISTRY.get(loss_type)(**opt)
    logger = get_root_logger()
    logger.info(f"Loss [{loss.__class__.__name__}] is created.")
    return loss
