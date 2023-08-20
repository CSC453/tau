from argparse import Namespace, ArgumentParser
from typing import Callable, TypeAlias, Any
import hashlib

# import pprint

from tomlkit import dumps  # type: ignore
import tomllib

from parse import ParseErrorException
from tau.asts import AST
from tau.error import CompileError
from tau.utilities import dump_fields, visitor

import scanner
from tau.asts import Program
import parse
import bindings
import typecheck
import offsets
import assign
import codegen
from vm.vm_insns import Insn

Container: TypeAlias = dict[str, Any]


def do_tree(ast: AST) -> list[dict[str, str]]:
    dmp: Callable[[AST], None]
    found: list[dict[str, str]]
    dmp, found = dump_fields.mk_fn()
    v = visitor.Visitor(dmp)
    v.AST(ast)
    return found


def match(pattern: Container, subject: Container) -> bool:
    if "error" in pattern:
        if "error" not in subject:
            return False
        if pattern["error"] != subject["error"] and pattern["error"] != "*":
            return False
    if "pragmas" in pattern:
        if "pragmas" not in subject:
            return False
        if not all(p in subject["pragmas"] for p in pattern["pragmas"]):
            return False
    if "tokens" in pattern:
        if "tokens" not in subject:
            return False
        if not any(t in subject["tokens"] for t in pattern["tokens"]):
            return False
    if "nodes" in pattern:
        if "nodes" not in subject:
            return False
        snodes: list[dict[str, str]] = subject["nodes"]
        pnodes: list[dict[str, str]] = pattern["nodes"]
        p: dict[str, str]
        for p in pnodes:
            if not any(
                all(k in d and p[k] == d[k] for k in p) for d in snodes
            ):
                return False
    return True


def keep(pattern: Container, container: Container) -> bool:
    # pprint.pprint(pattern)
    # pprint.pprint(container)
    if "require" in pattern:
        for require in pattern["require"]:
            if not match(require, container):
                return False
    if "exclude" in pattern:
        for exclude in pattern["exclude"]:
            if match(exclude, container):
                return False
    return True


def process(patternname: str, fnames: list[str], verify: bool) -> None:
    with open(patternname, "rb") as f:
        pattern: Container = tomllib.load(f)
    for fname in fnames:
        with open(fname, "rb") as f:
            container: Container = tomllib.load(f)
        if verify:
            if "source" not in container:
                print(f"{fname} has no source")
                continue
            if "hash" not in container:
                print(f"{fname} has no hash")
                continue
            name = container["source"]
            with open(name) as f:
                source = f.read()
                import hashlib

                hash = hashlib.sha256(source.encode("utf-8")).hexdigest()
                if hash != container["hash"]:
                    print(f"{fname} does not match hash")
                    continue
        if keep(pattern, container):
            print(container["source"])


def main() -> None:
    args: Namespace = get_args()

    match args.command:
        case "match":
            patternname = args.pattern
            files = args.files
            process(patternname, files, args.verify)
        case "characterize":
            fname: str = args.file[0]
            outname: str = args.output
            characterize(fname, outname)
        case _:
            assert False, f"unknown command {args.command}"


def characterize(fname: str, outname: str):
    input: str
    with open(fname) as f:
        input = f.read()

    hash = hashlib.sha256(input.encode("utf-8")).hexdigest()
    container: Container = {
        "source": fname,
        "hash": hash,
    }

    lines = input.split("\n")
    pragmas: set[str] = set()
    for line in lines:
        line = line.strip()
        if line.startswith("//PRAGMA:"):
            pragma = line[9:].strip()
            pragmas.add(pragma)

    if pragmas:
        container["pragmas"] = list(pragmas)

    try:
        lexer = scanner.Scanner(input)
        container["tokens"] = list(set(t.kind for t in lexer.tokens))

        psr = parse.Parser(lexer)
        tree: Program = psr.parse()
        container["nodes"] = do_tree(tree)

        bindings.process(tree)
        container["nodes"] = do_tree(tree)

        typecheck.process(tree)
        container["nodes"] = do_tree(tree)

        offsets.process(tree)
        container["nodes"] = do_tree(tree)

        assign.process(tree)
        container["nodes"] = do_tree(tree)

        _: list[Insn] = codegen.process(tree)

    except CompileError as e:
        container["error"] = str(e.__class__.__name__)
    except ParseErrorException as e:
        container["error"] = str(e.__class__.__name__)

    with open(outname, "w") as f:
        print(dumps(container), file=f) # type: ignore


def get_args() -> Namespace:
    ap: ArgumentParser = ArgumentParser(description="Compile Tau files")
    # create subparsers
    command = ap.add_subparsers(dest="command", required=True)
    characterize = command.add_parser(
        "characterize", help="characterize source file"
    )
    characterize.add_argument("file", nargs=1, help="source file")
    characterize.add_argument(
        "--output", type=str, required=True, help="output file"
    )
    match = command.add_parser(
        "match", help="match pattern TOML to characterized TOML files"
    )
    match.add_argument(
        "--pattern", type=str, required=True, help="pattern file"
    )
    match.add_argument("files", nargs="*", help="source file TOMLs")
    match.add_argument(
        "--verify", action="store_true", help="verify files match hashes"
    )

    return ap.parse_args()


if __name__ == "__main__":
    main()
