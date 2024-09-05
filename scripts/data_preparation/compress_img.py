"""Compress image datasets.

Annotation files may also created for those datasets without splits. According
to SRAnnotationDataset, each line in the annotation file contains the image
names and image shape (usually for gt), separated by a white space. For
instance: "0001_s001.png (480,480,3).

Copyright 2023 RyanXingQL

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License. You may obtain a copy of the
License at
https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import argparse
import multiprocessing as mp
import os
import os.path as osp

import cv2
from tqdm import tqdm


def run_cmd(cmd):
    os.system(cmd)


def opencv_write_jpeg(src_path, quality, tar_path):
    img = cv2.imread(src_path)
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]  # 0-100
    _, jpeg_data = cv2.imencode(".jpg", img, encode_param)
    comp_img = cv2.imdecode(jpeg_data, cv2.IMREAD_COLOR)
    cv2.imwrite(tar_path, comp_img)


def parse_args():
    parser = argparse.ArgumentParser(description="Compress image dataset.")
    parser.add_argument("--codec", type=str, required=True, choices=["BPG", "JPEG"])
    parser.add_argument(
        "--dataset", type=str, required=True, choices=["DIV2K", "Flickr2K"]
    )
    parser.add_argument("--max-npro", type=int, default=16)
    parser.add_argument("--quality", type=int, default=37)
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = parse_args()

    if args.codec == "BPG":
        enc_path = osp.abspath("datasets/libbpg/bpgenc")
        dec_path = osp.abspath("datasets/libbpg/bpgdec")
        paths = []

        if args.dataset == "DIV2K":
            src_root = osp.abspath("datasets/DIV2K")
            tmp_root = osp.abspath("tmp/datasets/DIV2K")
            tar_root = osp.abspath("datasets/DIV2K")

            # training set
            src_dir = osp.join(src_root, "train")
            tmp_dir = osp.join(tmp_root, f"train_BPG_QP{args.quality}")
            tar_dir = osp.join(tar_root, f"train_BPG_QP{args.quality}")
            os.makedirs(tmp_dir)
            os.makedirs(tar_dir)

            for idx in range(1, 801):
                paths.append(
                    dict(
                        src=osp.join(src_dir, f"{idx:04d}.png"),
                        bpg=osp.join(tmp_dir, f"{idx:04d}.bpg"),
                        tar=osp.join(tar_dir, f"{idx:04d}.png"),
                    )
                )

            # validation set
            src_dir = osp.join(src_root, "valid")
            tmp_dir = osp.join(tmp_root, f"valid_BPG_QP{args.quality}")
            tar_dir = osp.join(tar_root, f"valid_BPG_QP{args.quality}")
            os.makedirs(tmp_dir)
            os.makedirs(tar_dir)

            for idx in range(801, 901):
                paths.append(
                    dict(
                        src=osp.join(src_dir, f"{idx:04d}.png"),
                        bpg=osp.join(tmp_dir, f"{idx:04d}.bpg"),
                        tar=osp.join(tar_dir, f"{idx:04d}.png"),
                    )
                )

        if args.dataset == "Flickr2K":
            src_dir = osp.abspath("datasets/Flickr2K")
            tmp_dir = osp.abspath(f"tmp/datasets/Flickr2K/BPG_QP{args.quality}")
            tar_dir = osp.abspath(f"datasets/Flickr2K/BPG_QP{args.quality}")
            os.makedirs(tmp_dir)
            os.makedirs(tar_dir)

            for idx in range(1, 2651):
                paths.append(
                    dict(
                        src=osp.join(src_dir, f"{idx:06d}.png"),
                        bpg=osp.join(tmp_dir, f"{idx:06d}.bpg"),
                        tar=osp.join(tar_dir, f"{idx:06d}.png"),
                    )
                )

            # create meta
            # with open(osp.join(src_dir, "train.txt"), "w") as file:
            #     for idx in tqdm(range(1, 1989), ncols=0):
            #         img_name = f"{idx:06d}.png"
            #         gt_path = osp.join(src_dir, img_name)
            #         gt = cv2.imread(gt_path)
            #         h, w, c = gt.shape
            #         line = f"{img_name} ({h},{w},{c})\n"
            #         file.write(line)
            #
            # with open(osp.join(src_dir, "test.txt"), "w") as file:
            #     for idx in tqdm(range(1989, 2651), ncols=0):
            #         img_name = f"{idx:06d}.png"
            #         gt_path = osp.join(src_dir, img_name)
            #         gt = cv2.imread(gt_path)
            #         h, w, c = gt.shape
            #         line = f"{img_name} ({h},{w},{c})\n"
            #         file.write(line)

        # Compression
        pool = mp.Pool(processes=args.max_npro)
        pbar = tqdm(total=len(paths), ncols=0)
        for path in paths:
            enc_cmd = f'{enc_path} -o {path["bpg"]} -q {args.quality}' f' {path["src"]}'
            dec_cmd = f'{dec_path} -o {path["tar"]} {path["bpg"]}'
            cmd = f"{enc_cmd} && {dec_cmd}"
            pool.apply_async(
                func=run_cmd,
                args=(cmd,),
                callback=lambda _: pbar.update(),
                error_callback=lambda err: print(err),
            )
        pool.close()
        pool.join()
        pbar.close()

    elif args.codec == "JPEG":
        paths = []

        if args.dataset == "DIV2K":
            src_root = osp.abspath("datasets/DIV2K")
            tar_root = osp.abspath("datasets/DIV2K")

            # training set
            src_dir = osp.join(src_root, "train")
            tar_dir = osp.join(tar_root, f"train_JPEG_QF{args.quality}")
            os.makedirs(tar_dir)

            for idx in range(1, 801):
                paths.append(
                    dict(
                        src=osp.join(src_dir, f"{idx:04d}.png"),
                        tar=osp.join(tar_dir, f"{idx:04d}.png"),
                    )
                )

            # validation set
            src_dir = osp.join(src_root, "valid")
            tar_dir = osp.join(tar_root, f"valid_JPEG_QF{args.quality}")
            os.makedirs(tar_dir)

            for idx in range(801, 901):
                paths.append(
                    dict(
                        src=osp.join(src_dir, f"{idx:04d}.png"),
                        tar=osp.join(tar_dir, f"{idx:04d}.png"),
                    )
                )

        if args.dataset == "Flickr2K":
            src_dir = osp.abspath("datasets/Flickr2K")
            tar_dir = osp.abspath(f"datasets/Flickr2K_JPEG_QF{args.quality}")
            os.makedirs(tar_dir)

            for idx in range(1, 2651):
                paths.append(
                    dict(
                        src=osp.join(src_dir, f"{idx:06d}.png"),
                        tar=osp.join(tar_dir, f"{idx:06d}.png"),
                    )
                )

            # create meta
            # with open(osp.join(src_dir, "train.txt"), "w") as file:
            #     for idx in tqdm(range(1, 1989), ncols=0):
            #         img_name = f"{idx:06d}.png"
            #         gt_path = osp.join(src_dir, img_name)
            #         gt = cv2.imread(gt_path)
            #         h, w, c = gt.shape
            #         line = f"{img_name} ({h},{w},{c})\n"
            #         file.write(line)
            #
            # with open(osp.join(src_dir, "test.txt"), "w") as file:
            #     for idx in tqdm(range(1989, 2651), ncols=0):
            #         img_name = f"{idx:06d}.png"
            #         gt_path = osp.join(src_dir, img_name)
            #         gt = cv2.imread(gt_path)
            #         h, w, c = gt.shape
            #         line = f"{img_name} ({h},{w},{c})\n"
            #         file.write(line)

        # Compression
        pool = mp.Pool(processes=args.max_npro)
        pbar = tqdm(total=len(paths), ncols=0)
        for path in paths:
            pool.apply_async(
                func=opencv_write_jpeg,
                args=(
                    path["src"],
                    args.quality,
                    path["tar"],
                ),
                callback=lambda _: pbar.update(),
                error_callback=lambda err: print(err),
            )
        pool.close()
        pool.join()
        pbar.close()
