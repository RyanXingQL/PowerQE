"""A multi-thread tool to crop large images to sub-images for faster IO."""

import argparse
import cv2
import numpy as np
import os
import sys
from multiprocessing import Pool
from os import path as osp
from tqdm import tqdm

from basicsr.utils import scandir


def worker(path):
    """Worker for each process.

    Args:
        path (str): Image path.

    Returns:
        process_info (str): Process information displayed in progress bar.
    """
    img_name, extension = osp.splitext(osp.basename(path))
    img = cv2.imread(path, cv2.IMREAD_UNCHANGED)

    h, w = img.shape[0:2]
    h_space = np.arange(0, h - args.crop_size + 1, args.step)  # starting h coordinates
    if h - (h_space[-1] + args.crop_size) > args.thresh_size:
        h_space = np.append(h_space, h - args.crop_size)
    w_space = np.arange(0, w - args.crop_size + 1, args.step)
    if w - (w_space[-1] + args.crop_size) > args.thresh_size:
        w_space = np.append(w_space, w - args.crop_size)

    index = 0
    for x in h_space:
        for y in w_space:
            index += 1
            assert index < 10000
            cropped_img = img[x:x + args.crop_size, y:y + args.crop_size, ...]
            cropped_img = np.ascontiguousarray(cropped_img)
            cv2.imwrite(
                osp.join(args.save_folder, f'{img_name}_s{index:04d}{extension}'),
                cropped_img,
                [cv2.IMWRITE_PNG_COMPRESSION, args.compression_level],
            )
    process_info = f'Processing {img_name} ...'
    return process_info


def extract_subimages(allow_exist=False):
    """Crop images to subimages."""
    if not osp.exists(args.save_folder):
        os.makedirs(args.save_folder)
        print(f'mkdir {args.save_folder} ...')
    else:
        print(f'Folder {args.save_folder} already exists.')
        if not allow_exist:
            sys.exit(1)

    img_list = list(scandir(args.input_folder, full_path=True))
    if allow_exist:
        # make sure that images between input_folder and save_folder have different names
        for path in img_list:
            to_save_img_path = osp.join(args.save_folder, osp.basename(path))
            assert not osp.exists(to_save_img_path), f'{to_save_img_path} already exists.'

    pbar = tqdm(total=len(img_list), unit='image', desc='Extract', ncols=0)
    pool = Pool(args.n_thread)
    for path in img_list:
        pool.apply_async(worker, args=(path, ), callback=lambda arg: pbar.update(1))
    pool.close()
    pool.join()
    pbar.close()
    print('All processes done.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-folder', type=str, required=True, default='datasets/DIV2K/train')
    parser.add_argument('--save-folder', type=str, required=True, default='tmp/datasets/DIV2K/train')
    parser.add_argument('--n-thread', type=int, default=20, help='Thread number')
    parser.add_argument(
        '--compression_level',
        type=int,
        default=3,
        help=('CV_IMWRITE_PNG_COMPRESSION from 0 to 9. '
              'A higher value means a smaller size and longer compression time. '
              'Use 0 for faster CPU decompression. Default: 3, same in cv2.'),
    )
    parser.add_argument('--crop-size', type=int, default=128, help='Crop size')
    parser.add_argument('--step', type=int, default=64, help='Step for overlapped sliding window')
    parser.add_argument(
        '--thresh_size',
        type=int,
        default=0,
        help=('Threshold size. If the remaining portion at the edge of the image is smaller than thresh_size, '
              'that portion will be discarded and not included as a patch.'),
    )
    parser.add_argument('--add-suffix', action='store_false', help='Add suffix to save folder')
    parser.add_argument('--allow-exist', action='store_true', help='Add sub-images to existed folder')
    args = parser.parse_args()

    if args.add_suffix:
        args.save_folder = f'{args.save_folder}_size{args.crop_size}_step{args.step}_thresh{args.thresh_size}'
    extract_subimages(allow_exist=args.allow_exist)
