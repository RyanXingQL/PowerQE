from copy import deepcopy

from basicsr.utils import get_root_logger

from .qe_model import QEModel
from .registry import MODEL_REGISTRY

__all__ = ["build_model", "MODEL_REGISTRY", "QEModel"]


def build_model(opt):
    """Build model from options.

    Args:
        opt (dict): Configuration. It must contain:
            model_type (str): Model type.
    """
    opt = deepcopy(opt)
    model = MODEL_REGISTRY.get(opt["model_type"])(opt)
    logger = get_root_logger()
    logger.info(f"Model [{model.__class__.__name__}] is created.")
    return model
