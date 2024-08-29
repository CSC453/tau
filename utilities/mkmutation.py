import argparse
import random
import os


def mutate(original: str) -> str:
    index = random.randint(0, len(original) - 1)
    numeral = str(index)
    mutated = (
        original[:index] + f" {numeral} {random.randint(0,1000)} " + original[index:]
    )
    return mutated


def main() -> None:
    args: argparse.Namespace = parse_args()
    input_file: str = args.input
    with open(input_file, "r") as f:
        input = f.read()
    output_file: str = args.output
    if os.path.exists(output_file) and not args.force:
        raise Exception("Output file already exists")
    mutated = mutate(input)
    with open(output_file, "w") as f:
        f.write(mutated)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a mutation file for TAU")
    parser.add_argument("--input", type=str, required=True, help="input file")
    parser.add_argument(
        "--output",
        type=str,
        required=True,
        help="output file",
    )
    parser.add_argument("--force", action="store_true", help="force overwrite")
    return parser.parse_args()


if __name__ == "__main__":
    main()
