import argparse
from basicsr.utils import scandir
from basicsr.utils.lmdb_util import make_lmdb_from_imgs


def prepare_keys_div2k(folder_path):
    """Prepare image path list and keys for DIV2K dataset.

    Args:
        folder_path (str): Folder path.

    Returns:
        list[str]: Image path list.
        list[str]: Key list.
    """
    print("Reading image path list ...")
    img_path_list = sorted(list(scandir(folder_path, suffix="png", recursive=False)))
    keys = [img_path.split(".png")[0] for img_path in sorted(img_path_list)]

    return img_path_list, keys


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dataset",
        type=str,
        required=True,
        choices=["DIV2K"],
    )
    args = parser.parse_args()

    if args.dataset == "DIV2K":
        # HQ images
        folder_path = "tmp/datasets/DIV2K/train_size128_step64_thresh0"
        lmdb_path = "datasets/DIV2K/train_size128_step64_thresh0.lmdb"
        img_path_list, keys = prepare_keys_div2k(folder_path)
        make_lmdb_from_imgs(folder_path, lmdb_path, img_path_list, keys)

        # LQ images
        folder_path = "tmp/datasets/DIV2K/train_BPG_QP37_size128_step64_thresh0"
        lmdb_path = "datasets/DIV2K/train_BPG_QP37_size128_step64_thresh0.lmdb"
        img_path_list, keys = prepare_keys_div2k(folder_path)
        make_lmdb_from_imgs(folder_path, lmdb_path, img_path_list, keys)
