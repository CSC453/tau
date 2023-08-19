from typing import Callable, List, Any, Optional

from tau.asts import BinaryOp, IntType

from .tokens import Token
from .compare import assert_equal
from .error import CompileError

# pyright: basic


def test_scanner(
    student: List[Token], expected: List[Token], crash: bool
) -> bool:
    try:
        return student == expected
    except:
        if crash:
            raise
        return False


def run_scanner(input: str) -> List[Token]:
    from scanner import Scanner

    lexer: Scanner = Scanner(input)
    return list(lexer)


def test_generic(student: Any, expected: Any, crash: bool) -> bool:
    try:
        return student == expected
    except:
        if crash:
            raise
        return False


def test_pass(student: Any, expected: Any, crash: bool) -> bool:
    return True


def run_parser(input: str):
    from scanner import Scanner

    lexer: Scanner = Scanner(input)
    from parse import Parser

    psr: Parser = Parser(lexer.tokens)
    tree: Any = psr.parse()
    return None  # need to remove after m5


def test_ast(student: Any, expected: Any, crash: bool) -> bool:
    from .asts import (
        AST,
        Id,
        IntType,
        BoolType,
        VoidType,
        BinaryOp,
        UnaryOp,
        IntLiteral,
        BoolLiteral,
    )

    def ast_checker(std: AST, exp: AST) -> bool:
        assert std.span == exp.span, f"{std.span} != {exp.span}"
        match (exp, std):
            case (Id(), Id()):
                assert exp.token == std.token, f"{exp.token} != {std.token}"
            case (IntType(), IntType()):
                assert exp.token == std.token, f"{exp.token} != {std.token}"
            case (BoolType(), BoolType()):
                assert exp.token == std.token, f"{exp.token} != {std.token}"
            case (VoidType(), VoidType()):
                assert exp.token == std.token, f"{exp.token} != {std.token}"
            case (BinaryOp(), BinaryOp()):
                assert exp.op == std.op, f"{exp.op} != {std.op}"
            case (UnaryOp(), UnaryOp()):
                assert exp.op == std.op, f"{exp.op} != {std.op}"
            case (IntLiteral(), IntLiteral()):
                assert exp.token == std.token, f"{exp.token} != {std.token}"
            case (BoolLiteral(), BoolLiteral()):
                assert exp.token == std.token, f"{exp.token} != {std.token}"
                assert exp.value == std.value, f"{exp.value} != {std.value}"
        return True

    try:
        assert_equal(student, expected, ast_checker)
        return True
    except:
        if crash:
            raise
        return False


def test_binding(student: Any, expected: Any, crash: bool) -> bool:
    from .asts import AST, Id, FuncDecl, CompoundStmt
    from .symbols import Symbol, FuncScope, LocalScope, Scope

    def bindings_checker(std: AST, exp: AST) -> bool:
        student_scope: Optional[Scope] = None
        expected_scope: Optional[Scope] = None
        assert type(std) == type(exp), f"{type(std)} != {type(exp)}"
        match (std, exp):
            case (Id(), Id()):
                assert (
                    std.symbol.name == exp.symbol.name
                ), f"{std.symbol.name} != {exp.symbol.name}"
                student_scope = std.symbol.scope
                expected_scope = exp.symbol.scope
            case (FuncDecl(), FuncDecl()):
                assert isinstance(
                    std.func_scope, FuncScope
                ), f"{type(std.func_scope)} != {type(exp.func_scope)}"
                assert isinstance(
                    exp.func_scope, FuncScope
                ), f"{type(std.func_scope)} != {type(exp.func_scope)}"
                student_scope = std.func_scope
                expected_scope = exp.func_scope
            case (CompoundStmt(), CompoundStmt()):
                assert isinstance(
                    std.local_scope, LocalScope
                ), f"{type(std.local_scope)} != {type(exp.local_scope)}"
                assert isinstance(
                    exp.local_scope, LocalScope
                ), f"{type(std.local_scope)} != {type(exp.local_scope)}"
                student_scope = std.local_scope
                expected_scope = exp.local_scope
            case (_, _):
                pass
        while student_scope and expected_scope:
            assert (
                student_scope.span == expected_scope.span
            ), f"{student_scope.span} != {expected_scope.span}"
            assert type(student_scope) == type(
                expected_scope
            ), f"{type(student_scope)} != {type(expected_scope)}"
            assert set(student_scope.symtab.keys()) == set(
                expected_scope.symtab.keys()
            ), f"{set(student_scope.symtab.keys())} != {set(expected_scope.symtab.keys())}"

            student_scope = student_scope.parent
            expected_scope = expected_scope.parent
        assert student_scope is None, f"{student_scope} != None"
        assert expected_scope is None, f"{expected_scope} != None"
        return True

    try:
        v = test_ast(student, expected, crash)
        assert_equal(student, expected, bindings_checker)
        return v
    except:
        if crash:
            raise
        return False


def test_typecheck(student: Any, expected: Any, crash: bool) -> bool:
    from .asts import (
        AST,
        Id,
        FuncDecl,
        CompoundStmt,
        VarDecl,
        ParamDecl,
        Expr,
        TypeAST,
        Decl,
    )
    from .symbols import (
        FuncScope,
        LocalScope,
        Scope,
        SemanticType,
        ArrayType,
        FuncType,
    )

    def assert_same_type(student: SemanticType, expected: SemanticType):
        assert type(student) == type(
            expected
        ), f"{type(student)} != {type(expected)}"
        match (student, expected):
            case (ArrayType(), ArrayType()):
                assert_same_type(student.element_type, expected.element_type)
            case (FuncType(), FuncType()):
                assert isinstance(student, FuncType)
                assert_same_type(student.ret, expected.ret)
                assert len(student.params) == len(expected.params)
                for i in range(len(student.params)):
                    assert_same_type(student.params[i], expected.params[i])

    def typecheck_checker(student: AST, expected: AST) -> bool:
        if isinstance(expected, Id):
            assert isinstance(student, Id)
            assert_same_type(student.semantic_type, expected.semantic_type)
            assert_same_type(
                student.symbol.get_type(), expected.symbol.get_type()
            )
        if isinstance(expected, Expr):
            assert isinstance(student, Expr)
            assert_same_type(student.semantic_type, expected.semantic_type)
        if isinstance(expected, TypeAST):
            assert isinstance(student, TypeAST)
            assert_same_type(student.semantic_type, expected.semantic_type)
        if isinstance(expected, Decl):
            assert isinstance(student, Decl)
            assert_same_type(student.semantic_type, expected.semantic_type)
        return True

    try:
        v = test_binding(student, expected, crash)
        assert_equal(student, expected, typecheck_checker)
        return v
    except:
        if crash:
            raise
        return False


def test_offsets(student: Any, expected: Any, crash: bool) -> bool:
    from .asts import (
        AST,
        Id,
    )

    def offset_checker(student: AST, expected: AST) -> bool:
        if isinstance(expected, Id):
            assert isinstance(student, Id)
            assert (
                student.symbol.offset == expected.symbol.offset
            ), f"{student.symbol.offset} != {expected.symbol.offset}"
        return True

    try:
        v = test_typecheck(student, expected, crash)
        assert_equal(student, expected, offset_checker)
        return v
    except:
        if crash:
            raise
        return False


def test_codegen(student: Any, expected: Any, crash: bool) -> bool:
    try:
        v = test_offsets(student, expected, crash)
        return v
    except:
        if crash:
            raise
        return False


def test_errors(student: Any, expected: Any, crash: bool) -> bool:
    return student == expected


def run_ast(input: str) -> Any:
    from scanner import Scanner

    lexer: Scanner = Scanner(input)
    from parse import Parser
    from .asts import Program

    psr: Parser = Parser(lexer.tokens)
    tree: Program = psr.parse()
    return tree


def run_binding(input: str):
    tree = run_ast(input)
    import bindings

    bindings.process(tree)
    return tree


def run_typecheck(input: str):
    tree = run_binding(input)
    import typecheck

    typecheck.process(tree)
    return tree


def run_offsets(input: str):
    tree = run_typecheck(input)
    import offsets

    offsets.process(tree)
    return tree


def Xrun_codegen(input: str):
    tree = run_offsets(input)
    import codegen
    from stack_vm import vm_utils
    from stack_vm.vm_insns import Insn

    insns: List[Insn] = codegen.generate(tree)

    vm_utils.invoke_vm(insns, [], False)
    return tree


def run_codegen(input: str):
    tree = run_offsets(input)
    import assign

    assign.process(tree)

    import reg_gen
    from vm import vm_utils
    from vm.vm_insns import Insn

    insns: List[Insn] = reg_gen.generate(tree)

    vm_utils.invoke_vm(insns, [], False)
    return tree


def run_errors(input: str):
    try:
        tree = run_ast(input)
        import bindings

        bindings.process(tree)
        import typecheck

        typecheck.program(tree)
        import offsets

        offsets.program(tree)
        import codegen

        codegen.generate(tree)
    except CompileError as e:
        return "CompileError"
    except Exception as e:
        return f"Other Error: {e}"
    return "<No error>"
