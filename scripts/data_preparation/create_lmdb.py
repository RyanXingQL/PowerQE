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
        "--input_folder",
        type=str,
        required=True,
    )
    parser.add_argument(
        "--lmdb_path",
        type=str,
        required=True,
    )
    args = parser.parse_args()

    img_path_list, keys = prepare_keys_div2k(args.input_folder)
    make_lmdb_from_imgs(args.input_folder, args.lmdb_path, img_path_list, keys)
