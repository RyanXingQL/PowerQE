"""Prepare training patches and make LMDB for multiple datasets.

According to SRLmdbDataset, each line in the meta should be like:
`baboon.png (120,125,3) 1`, which means: 1) image name (with extension):
baboon.png; 2) image shape: (120,125,3); and 3) compression level: 1. Also, it
records the image name without extension as the 'lq_path', which is used in
LmdbBackend as the key to search in the LMDB file. Therefore, keys in LMDB
should be image names without extension.

Each line in the txt file records 1)image name (with extension),
2)image shape, and 3)compression level, separated by a white space.

Source: mmediting/tools/data/super-resolution/div2k
/preprocess_div2k_dataset.py

Copyright (c) OpenMMLab. All rights reserved.

Copyright 2023 RyanXingQL

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

     https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import argparse
import os
import os.path as osp

# import re
import sys
from multiprocessing import Pool

import cv2
import lmdb
import mmcv
import numpy as np


def extract_subimages(opt):
    """Crop images to subimages.

    Args:
        opt (dict): Configuration dict. It contains:
            img_list (list[str]): List of image paths.
            save_folder (str): Path to save folder.
            n_thread (int): Thread number.
    """
    save_folder = opt["save_folder"]
    if not osp.exists(save_folder):
        os.makedirs(save_folder)
        print(f"mkdir {save_folder} ...")
    else:
        print(f"Folder {save_folder} already exists. Exit.")
        sys.exit(1)

    img_list = opt["img_list"]

    prog_bar = mmcv.ProgressBar(len(img_list))
    pool = Pool(opt["n_thread"])
    for path in img_list:
        pool.apply_async(
            worker,
            args=(path, opt),
            callback=lambda _: prog_bar.update(),
            error_callback=lambda err: print(err),
        )
    pool.close()
    pool.join()
    print("\nAll processes done.")


def worker(path, opt):
    """Worker for each process.

    Args:
        path (str): Image path.
        opt (dict): Configuration dict. It contains:
            crop_size (int): Crop size.
            step (int): Step for overlapped sliding window.
            thresh_size (int): Threshold size. Patches whose size is smaller
                than thresh_size will be dropped.
            save_folder (str): Path to save folder.
            compression_level (int): for cv2.IMWRITE_PNG_COMPRESSION.

    Returns:
        process_info (str): Process information displayed in progress bar.
    """
    crop_size = opt["crop_size"]
    step = opt["step"]
    thresh_size = opt["thresh_size"]
    img_name, extension = osp.splitext(osp.basename(path))

    # remove the x2, x3, x4 and x8 in the filename for DIV2K
    # img_name = re.sub('x[2348]', '', img_name)

    img = mmcv.imread(path, flag="unchanged")

    if img.ndim == 2 or img.ndim == 3:
        h, w = img.shape[:2]
    else:
        raise ValueError(f"Image ndim should be 2 or 3, but got {img.ndim}")

    h_space = np.arange(0, h - crop_size + 1, step)
    if h - (h_space[-1] + crop_size) > thresh_size:
        h_space = np.append(h_space, h - crop_size)
    w_space = np.arange(0, w - crop_size + 1, step)
    if w - (w_space[-1] + crop_size) > thresh_size:
        w_space = np.append(w_space, w - crop_size)

    index = 0
    for x in h_space:
        for y in w_space:
            index += 1
            cropped_img = img[x : x + crop_size, y : y + crop_size, ...]
            cv2.imwrite(
                osp.join(opt["save_folder"], f"{img_name}_s{index:03d}.png"),
                cropped_img,
                [cv2.IMWRITE_PNG_COMPRESSION, opt["compression_level"]],
            )
    process_info = f"Processing {img_name} ..."
    return process_info


def make_lmdb_for_datasets(opt):
    """Create lmdb files."""

    folder_path = opt["save_folder"]
    lmdb_path = opt["lmdb_folder"]
    suffix = opt["suffix"]
    img_path_list, keys = prepare_keys(folder_path, suffix=suffix)
    make_lmdb(folder_path, lmdb_path, img_path_list, keys)


def prepare_keys(folder_path, suffix="png"):
    """Prepare image path list and keys.

    Args:
        folder_path (str): Folder path.
        suffix (str)

    Returns:
        list[str]: Image path list.
        list[str]: Key list.
    """
    print("Reading image path list ...")
    img_path_list = list(mmcv.scandir(folder_path, suffix=suffix, recursive=False))
    keys = [img_path.split(f".{suffix}")[0] for img_path in img_path_list]

    return img_path_list, keys


def make_lmdb(
    data_path,
    lmdb_path,
    img_path_list,
    keys,
    batch=5000,
    compress_level=1,
    multiprocessing_read=False,
    n_thread=40,
):
    """Make lmdb.

    Contents of lmdb. The file structure is:
    example.lmdb
    ├── data.mdb
    ├── lock.mdb
    ├── meta_info.txt

    The data.mdb and lock.mdb are standard lmdb files; you can refer to
    https://lmdb.readthedocs.io/en/release/ for more details.

    The meta_info.txt is a specified txt file to record the meta information
    of our datasets. It will be automatically created when preparing
    datasets by our provided dataset tools.
    Each line in the txt file records 1)image name (with extension),
    2)image shape, and 3)compression level, separated by a white space.

    For example, the meta information could be:
    `000_00000000.png (720,1280,3) 1`, which means:
    1) image name (with extension): 000_00000000.png;
    2) image shape: (720,1280,3);
    3) compression level: 1

    We use the image name without extension as the lmdb key.

    If `multiprocessing_read` is True, it will read all the images to memory
    using multiprocessing. Thus, your server needs to have enough memory.

    Args:
        data_path (str): Data path for reading images.
        lmdb_path (str): Lmdb save path.
        img_path_list (str): Image path list.
        keys (str): Used for lmdb keys.
        batch (int): After processing batch images, lmdb commits.
            Default: 5000.
        compress_level (int): Compress level when encoding images. Default: 1.
        multiprocessing_read (bool): Whether to use multiprocessing to read all
            the images to memory. Default: False.
        n_thread (int): For multiprocessing.
    """
    assert len(img_path_list) == len(keys), (
        "img_path_list and keys should have the same length, "
        f"but got {len(img_path_list)} and {len(keys)}"
    )
    print(f"Create lmdb for {data_path}, save to {lmdb_path}...")
    print(f"Total images: {len(img_path_list)}")
    if not lmdb_path.endswith(".lmdb"):
        raise ValueError("lmdb_path must end with '.lmdb'.")
    if osp.exists(lmdb_path):
        print(f"Folder {lmdb_path} already exists. Exit.")
        sys.exit(1)
    else:
        os.makedirs(lmdb_path)

    if multiprocessing_read:
        # read all the images to memory (multiprocessing)
        dataset = {}  # use dict to keep the order for multiprocessing
        shapes = {}
        print(f"Read images with multiprocessing, #thread: {n_thread} ...")
        prog_bar = mmcv.ProgressBar(len(img_path_list))

        def callback(arg):
            """get the image data and update prog_bar."""
            key, dataset[key], shapes[key] = arg
            prog_bar.update()

        pool = Pool(n_thread)
        for path, key in zip(img_path_list, keys):
            pool.apply_async(
                read_img_worker,
                args=(osp.join(data_path, path), key, compress_level),
                callback=callback,
                error_callback=lambda err: print(err),
            )
        pool.close()
        pool.join()
        print(f"\nFinish reading {len(img_path_list)} images.")

    # create lmdb environment
    # obtain data size for one image
    img = mmcv.imread(osp.join(data_path, img_path_list[0]), flag="unchanged")
    _, img_byte = cv2.imencode(
        ".png", img, [cv2.IMWRITE_PNG_COMPRESSION, compress_level]
    )
    data_size_per_img = img_byte.nbytes
    print("Data size per image is: ", data_size_per_img)
    data_size = data_size_per_img * len(img_path_list)
    env = lmdb.open(lmdb_path, map_size=data_size * 10)

    # write data to lmdb
    prog_bar = mmcv.ProgressBar(len(img_path_list))
    txn = env.begin(write=True)
    txt_file = open(osp.join(lmdb_path, "meta_info.txt"), "w")
    for idx, (path, key) in enumerate(zip(img_path_list, keys)):
        prog_bar.update()
        key_byte = key.encode("ascii")
        if multiprocessing_read:
            img_byte = dataset[key]
            h, w, c = shapes[key]
        else:
            _, img_byte, img_shape = read_img_worker(
                osp.join(data_path, path), key, compress_level
            )
            h, w, c = img_shape

        txn.put(key_byte, img_byte)
        # write meta information
        txt_file.write(f"{key}.png ({h},{w},{c}) {compress_level}\n")
        if idx % batch == 0:
            txn.commit()
            txn = env.begin(write=True)
    txn.commit()
    env.close()
    txt_file.close()
    print("\nFinish writing lmdb.")


def read_img_worker(path, key, compress_level):
    """Read image worker.

    Args:
        path (str): Image path.
        key (str): Image key.
        compress_level (int): Compress level when encoding images.

    Returns:
        str: Image key.
        byte: Image byte.
        tuple[int]: Image shape.
    """
    img = mmcv.imread(path, flag="unchanged")
    if img.ndim == 2:
        h, w = img.shape
        c = 1
    else:
        h, w, c = img.shape
    _, img_byte = cv2.imencode(
        ".png", img, [cv2.IMWRITE_PNG_COMPRESSION, compress_level]
    )
    return key, img_byte, (h, w, c)


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Prepare training patches and make LMDB" " for multiple datasets."
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--dataset",
        help="dataset name",
        choices=[
            "div2k",
            "flickr2k",
            "div2k_qf10",
            "div2k_qf20",
            "div2k_qf30",
            "div2k_qf40",
            "div2k_qf50",
            "div2k_qp27",
            "div2k_qp32",
            "div2k_qp42",
            "div2k_qp47",
        ],
        required=True,
    )
    parser.add_argument(
        "--crop-size",
        nargs="?",
        default=128,
        type=int,
        help="cropped size for HR images",
    )
    parser.add_argument(
        "--step", nargs="?", default=64, type=int, help="step size for HR images"
    )
    parser.add_argument(
        "--thresh-size", nargs="?", default=0, help="threshold size for HR images"
    )
    parser.add_argument(
        "--compression-level",
        nargs="?",
        default=3,
        help="compression level when save png images",
    )
    parser.add_argument(
        "--n-thread",
        nargs="?",
        default=8,
        type=int,
        help="thread number when using multiprocessing",
    )
    parser.add_argument(
        "--no-lmdb", action="store_true", help="whether to prepare lmdb files"
    )
    parser.add_argument(
        "--suffix", type=str, default="png", help="image suffix for reading images"
    )
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = parse_args()

    # If LQ scale is N, please decrease 'crop_size', 'step' and 'thresh_size'
    # in opt by N

    if args.dataset == "div2k":
        gt_list = [f"data/div2k/train/{idx:04d}.png" for idx in range(1, 801)]
        lq_list = [
            f"data/div2k_lq/bpg/qp37/train/{idx:04d}.png" for idx in range(1, 801)
        ]
        opts = [
            dict(
                n_thread=args.n_thread,
                compression_level=args.compression_level,
                img_list=gt_list,
                save_folder="tmp/patches/div2k/train",
                lmdb_folder="data/lmdb/div2k/train.lmdb",
                crop_size=args.crop_size,
                step=args.step,
                thresh_size=args.thresh_size,
                suffix=args.suffix,
            ),
            dict(
                n_thread=args.n_thread,
                compression_level=args.compression_level,
                img_list=lq_list,
                save_folder="tmp/patches/div2k_lq/bpg/qp37/train",
                lmdb_folder="data/lmdb/div2k_lq/bpg/qp37/train.lmdb",
                crop_size=args.crop_size,
                step=args.step,
                thresh_size=args.thresh_size,
                suffix=args.suffix,
            ),
        ]

    elif args.dataset == "flickr2k":
        gt_list = [f"data/flickr2k/{idx:06d}.png" for idx in range(1, 1989)]
        lq_list = [f"data/flickr2k_lq/bpg/qp37/{idx:06d}.png" for idx in range(1, 1989)]
        opts = [
            dict(
                n_thread=args.n_thread,
                compression_level=args.compression_level,
                img_list=gt_list,
                save_folder="tmp/patches/flickr2k/train",
                lmdb_folder="data/lmdb/flickr2k/train.lmdb",
                crop_size=args.crop_size,
                step=args.step,
                thresh_size=args.thresh_size,
                suffix=args.suffix,
            ),
            dict(
                n_thread=args.n_thread,
                compression_level=args.compression_level,
                img_list=lq_list,
                save_folder="tmp/patches/flickr2k_lq/bpg/qp37/train",
                lmdb_folder="data/lmdb/flickr2k_lq/bpg/qp37/train.lmdb",
                crop_size=args.crop_size,
                step=args.step,
                thresh_size=args.thresh_size,
                suffix=args.suffix,
            ),
        ]

    elif "div2k_qp" in args.dataset:
        quality = args.dataset.split("div2k_qp")[1]
        lq_list = [
            f"data/div2k_lq/bpg/qp{quality}/train/{idx:04d}.png"
            for idx in range(1, 801)
        ]
        opts = [
            dict(
                n_thread=args.n_thread,
                compression_level=args.compression_level,
                img_list=lq_list,
                save_folder=f"tmp/patches/div2k_lq/bpg/qp{quality}/train",
                lmdb_folder=f"data/lmdb/div2k_lq/bpg/qp{quality}/train.lmdb",
                crop_size=args.crop_size,
                step=args.step,
                thresh_size=args.thresh_size,
                suffix=args.suffix,
            ),
        ]

    elif "div2k_qf" in args.dataset:
        quality = args.dataset.split("div2k_qf")[1]
        lq_list = [
            f"data/div2k_lq/jpeg/qf{quality}/train/{idx:04d}.png"
            for idx in range(1, 801)
        ]
        opts = [
            dict(
                n_thread=args.n_thread,
                compression_level=args.compression_level,
                img_list=lq_list,
                save_folder=f"tmp/patches/div2k_lq/jpeg/qf{quality}/train",
                lmdb_folder=f"data/lmdb/div2k_lq/jpeg/qf{quality}/train.lmdb",
                crop_size=args.crop_size,
                step=args.step,
                thresh_size=args.thresh_size,
                suffix=args.suffix,
            ),
        ]

    for opt in opts:
        # extract subimages
        extract_subimages(opt)

        # make LMDB
        if not args.no_lmdb:
            make_lmdb_for_datasets(opt)
