# from tau import vm
import scanner
from .asts import Program
import parse
import bindings
import typecheck
import offsets
import assign
import codegen
from vm.vm_insns import Insn


def compile(
    input: str,
) -> tuple[scanner.Scanner, parse.Parser, Program, list[Insn]]:
    lexer = scanner.Scanner(input)
    psr = parse.Parser(lexer)
    tree: Program = psr.parse()
    bindings.process(tree)
    typecheck.process(tree)
    offsets.process(tree)
    assign.process(tree)
    insns = codegen.process(tree)
    return lexer, psr, tree, insns
