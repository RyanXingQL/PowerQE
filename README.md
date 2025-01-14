# PowerQE

This repository supports some quality enhancement approaches for compressed image/video based on PyTorch and MMEditing.

Image approaches:

- [MPRNet @ CVPR'21](https://github.com/swz30/MPRNet): Multi-stage structure.
- [RBQE @ ECCV'20](https://github.com/ryanxingql/rbqe): Multi-exit structure and early-exit mechanism.
- [CBDNet @ CVPR'19](https://github.com/GuoShi28/CBDNet): Noise estimation. Originally for image denoising.
- [ESRGAN @ ECCVW'18](https://github.com/xinntao/ESRGAN): Relativistic discriminator. Originally for image super resolution. PIRM'18 winner.
- [RDN @ CVPR'18](https://github.com/yulunzhang/RDN): Residual dense network. Originally for image super resolution.
- [DnCNN @ TIP'17](https://github.com/cszn/DnCNN): Pioneer of CNN-based image denoising.
- [DCAD @ DCC'17](https://ieeexplore.ieee.org/abstract/document/7923714): Pioneer of HEVC compression artifacts reduction.
- [U-Net @ MICCAI'15](https://arxiv.org/abs/1505.04597): Multi-scale structure. Originally for biomedical image processing.
- [AR-CNN @ ICCV'15](https://arxiv.org/abs/1504.06993): Pioneer of CNN-based image compression artifacts reduction.

Video approaches:

- [ProVQE @ CVPRW'22](https://github.com/ryanxingql/winner-ntire22-vqe): Key-frame propagation. NTIRE'22 winner.
- [BasicVSR++ @ CVPR'22](https://github.com/ckkelvinchan/BasicVSR_PlusPlus): Flow-guided deformable alignment. Originally for video super resolution. NTIRE'21 winner.
- [STDF @ AAAI'20](https://github.com/ryanxingql/stdf-pytorch): Deformable alignment.
- [MFQEv2 @ TPAMI'19](https://github.com/ryanxingql/mfqev2.0): Key-frame alignment.
- [EDVR @ CVPR'19](https://github.com/xinntao/EDVR): Deformable alignment. Originally for video super resolution. NTIRE'19 winner.

Content:

- [PowerQE](#powerqe)
  - [Install dependency](#install-dependency)
  - [Prepare data](#prepare-data)
  - [Training](#training)
  - [Testing](#testing)
  - [Changelog](#changelog)

Resources:

- [Document](docs/v3.md)
- [Pretrained models](https://www.dropbox.com/sh/3mzzprf7ulv6fcf/AAAy5sp3nODU07sTN-qSgnNRa?dl=0)
- [Benchmark results](docs/benchmark_results/README.md)

## Install dependency

MMEditing is a submodule of PowerQE. One can easily upgrade the MMEditing, and add their models to PowerQE without modifying the MMEditing repository. One should clone PowerQE along with MMEditing like this:

```bash
git clone --depth 1 --recurse-submodules --shallow-submodules\
 https://github.com/ryanxingql/powerqe.git
```

Install dependency:

- `environment.yml`
- PyTorch v1 + MMCV v1 + MMEditing v0

Please refer to the document for [detailed installation](docs/v3.md#install-dependency).

## Prepare data

```bash
mkdir data
```

Place your data like this:

```txt
powerqe/data
`-- {div2k,div2k_lq/bpg/qp37}
    `-- train
    `   `-- 0{001,002,...,800}.png
    `-- valid
        `-- 0{801,802,...,900}.png
```

Please refer to the document for [detailed preparation](docs/v3.md#prepare-data).

## Training

```bash
#chmod +x tools/dist_train.sh  # for the first time

conda activate pqe &&\
 CUDA_VISIBLE_DEVICES=0\
 PORT=29500\
 tools/dist_train.sh\
 configs/<config>.py\
 1\
 <optional-options>
```

- Activate environment.
- Use GPU 0.
- Use port 29500 for communication.
- Training script.
- Configuration.
- Use one GPU.
- Optional options.

Optional options:

- `--resume-from <ckp>.pth`: To resume the training status (model weights, number of iterations, optimizer status, etc.) from a checkpoint file.

## Testing

```bash
#chmod +x tools/dist_test.sh  # for the first time

conda activate pqe &&\
 CUDA_VISIBLE_DEVICES=0\
 PORT=29510\
 tools/dist_test.sh\
 configs/<config>.py\
 work_dirs/<ckp>.pth\
 1\
 <optional-options>
```

- Activate environment.
- Use GPU 0.
- Use port 29510 for communication.
- Test script.
- Configuration.
- Checkpoint.
- Use one GPU.
- Optional options.

Optional options:

- `--save-path <save-folder>`: To save output images.

## Changelog

| Version                                                       | PyTorch | MMEditing | Video approaches |
| ------------------------------------------------------------- | ------- | --------- | ---------------- |
| V3                                                            | V1      | V0        | Supported        |
| [V2](https://github.com/ryanxingql/powerqe/releases/tag/v2.0) | V1      | V0        | N/A              |
| [V1](https://github.com/ryanxingql/powerqe/releases/tag/v1.0) | V1      | V0        | N/A              |
