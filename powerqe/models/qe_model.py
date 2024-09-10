from basicsr.models.sr_model import SRModel

from powerqe.archs import build_network

from .registry import MODEL_REGISTRY


@MODEL_REGISTRY.register()
class QEModel(SRModel):
    """Base QE model for single image quality enhancement."""

    def __init__(self, opt):
        super(SRModel, self).__init__(opt)

        # define network
        self.net_g = build_network(opt["network_g"])
        self.net_g = self.model_to_device(self.net_g)
        self.print_network(self.net_g)

        # load pretrained models
        load_path = self.opt["path"].get("pretrain_network_g", None)
        if load_path is not None:
            param_key = self.opt["path"].get("param_key_g", "params")
            self.load_network(
                self.net_g,
                load_path,
                self.opt["path"].get("strict_load_g", True),
                param_key,
            )

        if self.is_train:
            self.init_training_settings()
