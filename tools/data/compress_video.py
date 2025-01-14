"""Copyright 2023 RyanXingQL.

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
from glob import glob

import cv2
import numpy as np


def write_planar(img, planar_path):
    """Write planar.

    img: list of (h, w) array; each list item represents a channel.
    """
    planar_file = open(planar_path, "wb")
    for cha in img:
        h, w = cha.shape
        for ih in range(h):
            for iw in range(w):
                planar_file.write(cha[ih, iw])
    planar_file.close()


def read_planar(planar_path, fmt=((1080, 1920), (1080, 1920), (1080, 1920))):
    """Read planar.

    fmt: tuple of (h, w) tuple; each tuple item represents a channel.

    https://numpy.org/doc/stable/reference/generated/numpy.fromfile.html
    """
    planar_file = np.fromfile(planar_path, dtype=np.uint8)
    img = []
    accum = 0
    for res in fmt:
        h, w = res
        cha = planar_file[accum : (accum + h * w)].reshape(h, w)
        img.append(cha)
        accum += h * w
    return img


def write_ycbcr420(src_paths, tar_path, wdt, hgt):
    ycbcr420 = []
    for src_path in src_paths:
        bgr = cv2.imread(src_path)

        _hgt, _wdt = bgr.shape[:2]
        assert _hgt == hgt and _wdt == wdt

        ycrcb = cv2.cvtColor(bgr, cv2.COLOR_BGR2YCrCb)
        cr_sub = cv2.resize(
            ycrcb[..., 1], (wdt // 2, hgt // 2), interpolation=cv2.INTER_AREA
        )
        cb_sub = cv2.resize(
            ycrcb[..., 2], (wdt // 2, hgt // 2), interpolation=cv2.INTER_AREA
        )
        ycbcr420.append(ycrcb[..., 0])
        ycbcr420.append(cb_sub)  # cb before cr
        ycbcr420.append(cr_sub)
    write_planar(ycbcr420, tar_path)
    return tar_path


def read_ycbcr420(src_path, tar_paths, wdt, hgt, nfrms, print_dir):
    ycbcr420_nfrms = read_planar(
        src_path, fmt=((hgt, wdt), (hgt // 2, wdt // 2), (hgt // 2, wdt // 2)) * nfrms
    )
    for idx, tar_path in enumerate(tar_paths):
        ycrcb = np.empty((hgt, wdt, 3), np.uint8)
        ycrcb[..., 0] = ycbcr420_nfrms[3 * idx]
        ycrcb[..., 1] = cv2.resize(
            ycbcr420_nfrms[3 * idx + 2], (wdt, hgt), interpolation=cv2.INTER_CUBIC
        )
        ycrcb[..., 2] = cv2.resize(
            ycbcr420_nfrms[3 * idx + 1], (wdt, hgt), interpolation=cv2.INTER_CUBIC
        )
        bgr = cv2.cvtColor(ycrcb, cv2.COLOR_YCrCb2BGR)
        cv2.imwrite(tar_path, bgr)
    return print_dir


def run_cmd(cmd):
    os.system(cmd)
    return cmd


def img2planar(vids):
    """According to the HM manual, HM accepts videos in raw 4:2:0 planar format
    (Y'CbCr)."""
    pool = mp.Pool(processes=args.max_nprocs)

    for vid in vids:
        pool.apply_async(
            func=write_ycbcr420,
            args=(vid["src_paths"], vid["planar_path"], vid["wdt"], vid["hgt"]),
            callback=lambda x: print(x),
            error_callback=lambda err: print(err),
        )

    pool.close()
    pool.join()


def compress_planar(vids):
    pool = mp.Pool(processes=args.max_nprocs)

    for vid in vids:
        enc_cmd = (
            f'{enc_path} -i {vid["planar_path"]} -c {cfg_path}'
            f' -b {vid["bit_path"]} -o {vid["comp_planar_path"]}'
        )
        if vid["wdt"] % 8 != 0 or vid["hgt"] % 8 != 0:
            enc_cmd += " --ConformanceWindowMode=1"
        enc_cmd += (
            f" -q {args.qp} --Level=3.1 -fr 30"
            f' -wdt {vid["wdt"]} -hgt {vid["hgt"]} -f {vid["nfrms"]}'
            f' > {vid["log_path"]}'
        )

        pool.apply_async(
            func=run_cmd,
            args=(enc_cmd,),
            callback=lambda x: print(x),
            error_callback=lambda err: print(err),
        )

    pool.close()
    pool.join()


def planar2img(vids):
    pool = mp.Pool(processes=args.max_nprocs)

    for vid in vids:
        _dir = osp.dirname(vid["tar_paths"][0])
        os.makedirs(_dir)

        pool.apply_async(
            func=read_ycbcr420,
            args=(
                vid["comp_planar_path"],
                vid["tar_paths"],
                vid["wdt"],
                vid["hgt"],
                vid["nfrms"],
                _dir,
            ),
            callback=lambda x: print(x),
            error_callback=lambda err: print(err),
        )

    pool.close()
    pool.join()


def planar2img_mfqev2(vids):
    pool = mp.Pool(processes=args.max_nprocs)

    for vid in vids:
        _dir = osp.dirname(vid["src_paths"][0])
        os.makedirs(_dir)

        pool.apply_async(
            func=read_ycbcr420,
            args=(
                vid["planar_path"],
                vid["src_paths"],
                vid["wdt"],
                vid["hgt"],
                vid["nfrms"],
                _dir,
            ),
            callback=lambda x: print(x),
            error_callback=lambda err: print(err),
        )

    pool.close()
    pool.join()


def parse_args():
    parser = argparse.ArgumentParser(description="Compress video dataset.")
    parser.add_argument("--max-nprocs", type=int, default=16)
    parser.add_argument(
        "--dataset",
        type=str,
        required=True,
        choices=["vimeo-triplet", "vimeo-septuplet", "mfqev2"],
    )
    parser.add_argument("--qp", type=int, default=37)
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = parse_args()

    hm_dir = "data/hm18.0"
    enc_path = osp.join(hm_dir, "bin/TAppEncoderStatic")
    cfg_path = osp.join(hm_dir, "cfg/encoder_lowdelay_P_main.cfg")

    # Record video information
    if args.dataset == "vimeo-triplet":
        src_root = "data/vimeo_triplet/sequences"

        planar_root = "tmp/vimeo_triplet_planar"
        skip_planar = False
        if osp.exists(planar_root):
            skip_planar = (
                input(f"{planar_root} exists. Skip generating planar? (y/n) ") == "y"
            )
            assert (
                skip_planar
            ), f"Please remove the existing planar directory {planar_root}."

        subdirs = glob(os.path.join(src_root, "*/"))
        subdirs = [subdir.split("/")[-2] for subdir in subdirs]

        vids = []
        for subdir in subdirs:
            src_dir = osp.join(src_root, subdir)
            planar_dir = osp.join(planar_root, subdir)
            bit_dir = osp.join(f"tmp/vimeo_triplet_bit/hm18.0/ldp/qp{args.qp}", subdir)
            log_dir = bit_dir
            comp_planar_dir = osp.join(
                f"tmp/vimeo_triplet_comp_planar/hm18.0/ldp/qp{args.qp}", subdir
            )
            tar_dir = osp.join(f"data/vimeo_triplet_lq/hm18.0/ldp/qp{args.qp}", subdir)

            if not skip_planar:
                os.makedirs(planar_dir)
            os.makedirs(bit_dir)
            # os.makedirs(log_dir)
            os.makedirs(comp_planar_dir)

            vid_names = glob(os.path.join(src_dir, "*/"))
            vid_names = [vid_name.split("/")[-2] for vid_name in vid_names]

            for vid_name in vid_names:
                wdt = 448
                hgt = 256
                nfrms = 3
                src_paths = [
                    osp.join(src_dir, vid_name, f"im{idx_img}.png")
                    for idx_img in range(1, 4)
                ]
                planar_path = osp.join(planar_dir, vid_name + ".yuv")
                bit_path = osp.join(bit_dir, vid_name + ".bin")
                log_path = osp.join(log_dir, vid_name + ".log")
                comp_planar_path = osp.join(comp_planar_dir, vid_name + ".yuv")
                tar_paths = [
                    osp.join(tar_dir, vid_name, f"im{idx_img}.png")
                    for idx_img in range(1, 4)
                ]

                vids.append(
                    dict(
                        wdt=wdt,
                        hgt=hgt,
                        nfrms=nfrms,
                        src_paths=src_paths,
                        planar_path=planar_path,
                        bit_path=bit_path,
                        log_path=log_path,
                        comp_planar_path=comp_planar_path,
                        tar_paths=tar_paths,
                    )
                )

    if args.dataset == "vimeo-septuplet":
        src_root = "data/vimeo_septuplet/sequences"

        planar_root = "tmp/vimeo_septuplet_planar"
        skip_planar = False
        if osp.exists(planar_root):
            skip_planar = (
                input(f"{planar_root} exists. Skip generating planar? (y/n) ") == "y"
            )
            assert (
                skip_planar
            ), f"Please remove the existing planar directory {planar_root}."

        subdirs = glob(os.path.join(src_root, "*/"))
        subdirs = [subdir.split("/")[-2] for subdir in subdirs]

        vids = []
        for subdir in subdirs:
            src_dir = osp.join(src_root, subdir)
            planar_dir = osp.join(planar_root, subdir)
            bit_dir = osp.join(
                f"tmp/vimeo_septuplet_bit/hm18.0/ldp/qp{args.qp}", subdir
            )
            log_dir = bit_dir
            comp_planar_dir = osp.join(
                f"tmp/vimeo_septuplet_comp_planar/hm18.0/ldp/qp{args.qp}", subdir
            )
            tar_dir = osp.join(
                f"data/vimeo_septuplet_lq/hm18.0/ldp/qp{args.qp}", subdir
            )

            if not skip_planar:
                os.makedirs(planar_dir)
            os.makedirs(bit_dir)
            # os.makedirs(log_dir)
            os.makedirs(comp_planar_dir)

            vid_names = glob(os.path.join(src_dir, "*/"))
            vid_names = [vid_name.split("/")[-2] for vid_name in vid_names]

            for vid_name in vid_names:
                wdt = 448
                hgt = 256
                nfrms = 7
                src_paths = [
                    osp.join(src_dir, vid_name, f"im{idx_img}.png")
                    for idx_img in range(1, 8)
                ]
                planar_path = osp.join(planar_dir, vid_name + ".yuv")
                bit_path = osp.join(bit_dir, vid_name + ".bin")
                log_path = osp.join(log_dir, vid_name + ".log")
                comp_planar_path = osp.join(comp_planar_dir, vid_name + ".yuv")
                tar_paths = [
                    osp.join(tar_dir, vid_name, f"im{idx_img}.png")
                    for idx_img in range(1, 8)
                ]

                vids.append(
                    dict(
                        wdt=wdt,
                        hgt=hgt,
                        nfrms=nfrms,
                        src_paths=src_paths,
                        planar_path=planar_path,
                        bit_path=bit_path,
                        log_path=log_path,
                        comp_planar_path=comp_planar_path,
                        tar_paths=tar_paths,
                    )
                )

    if args.dataset == "mfqev2":
        src_root = "data/mfqev2"
        skip_gt = False
        if osp.exists(src_root):
            skip_gt = input(f"{src_root} exists. Skip generating GT? (y/n) ") == "y"
            assert skip_gt, f"Please remove the existing GT directory {src_root}."

        vids = []
        for subdir in ["train", "test"]:
            src_dir = osp.join("data/mfqev2", subdir)
            planar_dir = osp.join("data/mfqev2_planar", subdir)
            bit_dir = osp.join(f"tmp/mfqev2_bit/hm18.0/ldp/qp{args.qp}", subdir)
            log_dir = bit_dir
            comp_planar_dir = osp.join(
                f"tmp/mfqev2_comp_planar/hm18.0/ldp/qp{args.qp}", subdir
            )
            tar_dir = osp.join(f"data/mfqev2_lq/hm18.0/ldp/qp{args.qp}", subdir)

            os.makedirs(bit_dir)
            # os.makedirs(log_dir)
            os.makedirs(comp_planar_dir)

            planar_paths = glob(os.path.join(planar_dir, "*.yuv"))
            for planar_path in planar_paths:
                vid_name = planar_path.split("/")[-1].split(".")[0]
                res, nfrms = vid_name.split("_")[-2:]
                wdt, hgt = res.split("x")
                wdt, hgt, nfrms = int(wdt), int(hgt), int(nfrms)
                if subdir == "train" and (wdt < 256 or hgt < 256):
                    continue
                if subdir == "test" and wdt > 1920:
                    continue
                nfrms = 300 if nfrms > 300 else nfrms

                bit_path = osp.join(bit_dir, vid_name + ".bin")
                log_path = osp.join(log_dir, vid_name + ".log")
                comp_planar_path = osp.join(comp_planar_dir, vid_name + ".yuv")
                # Use '{idx_img:04d}' instead of '{idx_img}'
                # because sorted is commonly used
                # and '10.png' is ahead of '2.png'
                # but '10.png' is behind '02.png'
                tar_paths = [
                    osp.join(tar_dir, vid_name, f"{idx_img:04d}.png")
                    for idx_img in range(1, nfrms + 1)
                ]
                src_paths = [
                    osp.join(src_dir, vid_name, f"{idx_img:04d}.png")
                    for idx_img in range(1, nfrms + 1)
                ]

                vids.append(
                    dict(
                        wdt=wdt,
                        hgt=hgt,
                        nfrms=nfrms,
                        src_paths=src_paths,
                        planar_path=planar_path,
                        bit_path=bit_path,
                        log_path=log_path,
                        comp_planar_path=comp_planar_path,
                        tar_paths=tar_paths,
                    )
                )

    # Img -> Planar
    if args.dataset != "mfqev2" and (not skip_planar):
        img2planar(vids)

    # Compress planar
    compress_planar(vids)

    # Planar -> Img
    planar2img(vids)

    # Planar -> Img for GT
    if args.dataset == "mfqev2" and (not skip_gt):
        planar2img_mfqev2(vids)
