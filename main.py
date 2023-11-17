from argparse import Namespace, ArgumentParser
from typing import List
import sys

# from tau import vm
from vm import vm_utils
from vm.vm_insns import Insn
from .compile import compile
from .error import *
import parse


def main() -> None:
    args: Namespace = get_args()
    fname: str = args.file
    input: str
    with open(fname) as f:
        input = f.read()
    verbose: bool = args.verbose
    insns: List[Insn]

    try:
        _, _, _, insns = compile(input)
        if args.asm:
            vm_utils.dump_insns(insns)
        else:
            vm_utils.invoke_vm(insns, args.args, verbose)
    except parse.ParseErrorException as e:
        print(e, file=sys.stderr)
        if verbose:
            raise
        sys.exit(1)
    except CompileError as e:
        print(e, file=sys.stderr)
        if verbose:
            raise
        sys.exit(1)


def get_args() -> Namespace:
    ap: ArgumentParser = ArgumentParser(description="Compile Tau files")
    ap.add_argument("--file", required=True, help="source file")
    ap.add_argument("--verbose", action="store_true", help="verbose interpretation")
    ap.add_argument("--asm", action="store_true", help="(only) generate asm")
    ap.add_argument(
        "args", nargs="*", help="Arguments to pass to the program as integers"
    )
    return ap.parse_args()


if __name__ == "__main__":
    main()
