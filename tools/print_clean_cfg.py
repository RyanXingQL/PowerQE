import mmcv
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("cfg_path", type=str, help="Path to the cfg file")
parser.add_argument("--out", type=str, help="Path to the output file (optional).")
args = parser.parse_args()

cfg = mmcv.Config.fromfile(args.cfg_path)
print(cfg.pretty_text)

if args.out:
    cfg.dump(args.out)
    print(f"Configuration dumped to {args.out}.")
