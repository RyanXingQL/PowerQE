from basicsr.models.sr_model import SRModel

from .registry import MODEL_REGISTRY


@MODEL_REGISTRY.register()
class QEModel(SRModel):
    """Base QE model for single image quality enhancement."""

    def __init__(self, opt):
        super().__init__(opt)
