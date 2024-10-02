# PowerQE Document

## Install dependency

Chinese users may use mirrors:

```bash
# for Conda: https://mirrors.tuna.tsinghua.edu.cn/help/anaconda

# for PyPI: https://mirrors.tuna.tsinghua.edu.cn/help/pypi/
pip config set global.index-url https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple
```

First, create a Conda environment:

```bash
conda env create -f environment.yml  # create a env called "pqe"
conda activate pqe
```

Next, install PyTorch>=1.7, basicsr, and other dependencies. Here’s the code I use on my server:

```bash
#conda install pytorch==1.13.1 torchvision==0.14.1 torchaudio==0.13.1 pytorch-cuda=11.7 -c pytorch -c nvidia
pip install torch==1.13.1+cu117 torchvision==0.14.1+cu117 torchaudio==0.13.1 --extra-index-url https://download.pytorch.org/whl/cu117

pip install -r requirements.txt

pip install -e basicsr
#python -c "import basicsr; import torch"  # test basicsr and torch
```

## Prepare data

### Raw dataset

#### DIV2K

Source: [homepage](https://data.vision.ee.ethz.ch/cvl/DIV2K).

File tree before compression:

```txt
DIV2K
`-- train
    `-- 0{001,002,...,800}.png
`-- valid
    `-- 0{801,802,...,900}.png
```

### Compress image/video

#### BPG

[Better Portable Graphics (BPG)](https://bellard.org/bpg) is an image format based on the intra-frame encoding of the High Efficiency Video Coding (HEVC) standard.

Please refer to the official site and the [GitHub mirror](https://github.com/mirrorer/libbpg/blob/master/README) for instructions. The following is my personal experience of using libbpg v0.9.8.

##### Build

Clone:

```bash
cd datasets
git clone --depth=1 https://github.com/mirrorer/libbpg.git libbpg
```

Modify `libbpg/Makefile`:

- Comment `USE_X265=y` and uncomment `USE_JCTVC=y`: We want to use JCTVC instead of x265.
- Comment `USE_BPGVIEW=y`: We do not need BPGView.

Build:

```bash
cd datasets/libbpg
make clean
make
```

If any errors occur during the build, install the required dependencies based on the error messages. For example:

```bash
sudo apt-get install libpng-dev
sudo apt-get install libjpeg-dev

# build again
make clean
make
```

Basic usage:

```bash
bpgenc [-q quality] -o <bpg_path> <src_path>  # src image -> bpg
bpgdec -o <tar_path> <bpg_path>  # bpg -> tar image
```

Check `bpgenc -h` and `bpgdec -h` for detailed usage.

##### Example: Compress the DIV2K dataset

Run:

```bash
conda activate pqe
python scripts/data_preparation/compress_img.py --codec BPG --dataset DIV2K
```

Resulting file tree:

```txt
powerqe
`-- datasets
    `-- libbpg
        `-- bpgdec
        `-- bpgenc
    `-- DIV2K
        `-- {train,valid}
            `-- 0{001,002,...,800}.png
        `-- {train,valid}_BPG_QP37
            `-- 0{001,002,...,800}.png
`-- tmp/datasets/DIV2K/{train,valid}_BPG_QP37  # can be deleted after compression
    `-- 0{001,002,...,800}.bpg
```

## Training

```bash
#chmod +x scripts/train.sh

conda activate pqe

#CUDA_VISIBLE_DEVICES=0 scripts/train.sh 1 options/train/ESRGAN/RRDBNet_DIV2K_LMDB_G1.yml --auto_resume
[CUBLAS_WORKSPACE_CONFIG=:4096:8] CUDA_VISIBLE_DEVICES=<gpus> [PORT=<master_port>] scripts/train.sh <num_gpus> <cfg_path> [--auto_resume] [--debug] [--force_yml <key>=<value>]
```

- `auto_resume`: Automatically resume from the latest existing checkpoint.
- `debug`: Validation interval will be set to a short number.
- `force_yml`: Arguments that replaces those in the yml. Examples: `train:ema_decay=0.999`.

## Testing

```bash
#chmod +x scripts/test.sh

conda activate pqe

#CUDA_VISIBLE_DEVICES=0 scripts/test.sh 1 options/test/ESRGAN/RRDBNet_DIV2K_LMDB_G1_latest.yml --force_yml path:pretrain_network_g=experiments/train_ESRGAN_RRDBNet_DIV2K_LMDB_G1/models/net_g_600000.pth
[CUBLAS_WORKSPACE_CONFIG=:4096:8] CUDA_VISIBLE_DEVICES=<gpus> [PORT=<master_port>] scripts/test.sh <num_gpus> <cfg_path> [--force_yml <key>=<value>]
```

- Most models support only single-GPU testing, even when multi-GPU testing is requested.
- `force_yml`: Arguments that replaces those in the yml. Examples: `val:save_img=false` and `path:pretrain_network_g=experiments/train_ESRGAN_RRDBNet_DIV2K_LMDB_G1/models/net_g_600000.pth`.

## Others

### Use LMDB for faster IO

LMDB can be effectively utilized to accelerate IO operations, particularly for storing training patches.

Pros:

- Improved training speed: By working with small patches instead of larger images, the training process can be significantly expedited.
- Reduced CPU and GPU resource usage: Processing smaller patches instead of entire images alleviates the burden on both the CPU and GPU, resulting in lower CPU utilization and reduced GPU memory consumption.
- Universal image format: LMDB allows storing all images, such as PNG, JPG, and others, as PNG format within the LMDB files.
- Consolidated patch storage: All training patches are conveniently packed into a single LMDB file, facilitating organization and access.

Cons:

- Increased memory requirements: Prior to training, the LMDB files need to be loaded into memory, which can result in higher memory usage compared to directly working with images.
- Additional time, computation, and storage for generating LMDB files.
- Fixed cropping method: Once the LMDB file is generated, the cropping method employed for extracting patches from images becomes fixed and cannot be easily modified without regenerating the LMDB file.

Run for the DIV2K dataset:

```bash
conda activate pqe

python scripts/data_preparation/extract_subimages.py --dataset DIV2K

#python scripts/data_preparation/create_lmdb.py --input_folder "tmp/datasets/DIV2K/train_size128_step64_thresh0" --lmdb_path "datasets/DIV2K/train_size128_step64_thresh0.lmdb"
python scripts/data_preparation/create_lmdb.py --input_folder <gt_subimages_folder> --lmdb_path <gt_lmdb_path>
#python scripts/data_preparation/create_lmdb.py --input_folder "tmp/datasets/DIV2K/train_BPG_QP37_size128_step64_thresh0" --lmdb_path "datasets/DIV2K/train_BPG_QP37_size128_step64_thresh0.lmdb"
python scripts/data_preparation/create_lmdb.py --input_folder <lq_subimages_folder> --lmdb_path <lq_lmdb_path>
```

Resulting file tree:

```txt
powerqe
`-- datasets/DIV2K/{train,train_BPG_QP37}_size128_step64_thresh0.lmdb
    `-- data.mdb
    `-- lock.mdb
    `-- meta_info.txt
`-- tmp/datasets/DIV2K/{train,train_BPG_QP37}_size128_step64_thresh0  # can be deleted
    `-- 0001_s001.png
    `-- ...
```

### Use pre-commit hook for code check

Install:

```bash
conda activate pqe
pip install -U pre-commit
pre-commit install
```

On every commit, code check will be conducted automatically. You can also run the code check manually::

```bash
pre-commit run --all
```

### Use BPG on Mac

First install libbpg via homebrew:

```bash
brew install libbpg
#brew list
```

Then replace the `enc_path` and `dec_path` in the script `scripts/data_preparation/compress_img.py`.
