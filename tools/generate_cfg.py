# python generate_cfg.py original_config.py new_config.py "qp37:qp27" "old_string:new_string"
import argparse


def replace_strings_in_file(input_file, output_file, replacements):
    with open(input_file, "r", encoding="utf-8") as file:
        file_data = file.read()

    for old_str, new_str in replacements:
        file_data = file_data.replace(old_str, new_str)

    with open(output_file, "w", encoding="utf-8") as file:
        file.write(file_data)
    print(f"{output_file} generated.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Replace strings in a file.")
    parser.add_argument("input_file", help="Path to the input file.")
    parser.add_argument("output_file", help="Path to the output file.")
    parser.add_argument(
        "replacements", nargs="+", help="String replacements in the format 'old:new'."
    )

    args = parser.parse_args()

    replacements = [tuple(rep.split(":")) for rep in args.replacements]

    replace_strings_in_file(args.input_file, args.output_file, replacements)
