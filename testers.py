from typing import Callable, Any, NamedTuple, Optional


from .tokens import Token
from .error import CompileError

# pyright: basic

from .asts import (
    AST,
    AssignStmt,
    CallExpr,
    CallStmt,
    CompoundStmt,
    Id,
    IdExpr,
    IntTypeAST,
    BoolTypeAST,
    PrintStmt,
    ReturnStmt,
    VoidTypeAST,
    BinaryOp,
    UnaryOp,
    IntLiteral,
    BoolLiteral,
    FuncDecl,
    Expr,
    TypeAST,
    Decl,
    Argument,
    VarDecl,
    ParamDecl,
    IfStmt,
    WhileStmt,
    ArrayCell,
    Program,
)
from .symbols import (
    Symbol,
    FuncScope,
    LocalScope,
    Scope,
    SemanticType,
    ArrayType,
    FuncType,
    VoidType,
    IntType,
    BoolType,
)


fields: dict[str, list[tuple[type, list[str]]]] = {
    "ast": [
        (VarDecl, ["id", "type_ast"]),
        (ParamDecl, ["id", "type_ast"]),
        (ArrayType, ["element_type", "size"]),
        (BoolTypeAST, []),
        (IntTypeAST, []),
        (VoidTypeAST, []),
        (PrintStmt, ["expr"]),
        (CompoundStmt, ["decls", "stmts"]),
        (FuncDecl, ["id", "params", "ret_type_ast", "body"]),
        (Argument, ["expr"]),
        (CallExpr, ["fn", "args"]),
        (AssignStmt, ["lhs", "rhs"]),
        (IfStmt, ["expr", "thenStmt", "elseStmt"]),
        (WhileStmt, ["expr", "stmt"]),
        (CallStmt, ["call"]),
        (ReturnStmt, ["expr"]),
        (BinaryOp, ["left", "right"]),
        (UnaryOp, ["expr"]),
        (ArrayCell, ["arr", "idx"]),
        (IntLiteral, []),
        (BoolLiteral, []),
        (IdExpr, ["id"]),
        (Program, ["decls"]),
    ],
    "decorations": [
        (AST, ["span"]),
        (Id, ["token"]),
        (IntTypeAST, ["token"]),
        (BoolTypeAST, ["token"]),
        (VoidTypeAST, ["token"]),
        (BinaryOp, ["op"]),
        (UnaryOp, ["op"]),
        (IntLiteral, ["token"]),
        (BoolLiteral, ["token", "value"]),
        (ArrayType, ["size"]),
    ],
    "binding": [
        (Id, ["symbol"]),
        (Symbol, ["name"]),  # not "scope" because it's a circular reference
        (Scope, ["span", "symtab", "parent"]),
        (FuncScope, []),
        (LocalScope, []),
        (FuncDecl, ["func_scope"]),
        (CompoundStmt, ["local_scope"]),
    ],
    "typecheck": [
        (Id, ["semantic_type"]),
        (Symbol, ["_semantic_type"]),
        (ArrayType, ["element_type"]),
        (FuncType, ["params", "ret"]),
        (Expr, ["semantic_type"]),
        (TypeAST, ["semantic_type"]),
        (Decl, ["semantic_type"]),
        (Argument, ["semantic_type"]),
        (VoidType, []),
        (IntType, []),
        (BoolType, []),
    ],
    "offsets": [
        (Symbol, ["offset"]),
    ],
    "assign": [
        (Expr, ["register"]),
    ],
}


def mk_note(student: Any, expected: Any, name: str) -> str:
    ty = type(expected).__name__
    loc = ""
    if hasattr(expected, "span"):
        loc = f"[{expected.span.start} ⇒ {expected.span.end}]"
    return f"{name:10} {ty:14} {loc}"


def test_any(
    student: Any,
    expected: Any,
    crash: bool,
    fields: list[tuple[type, list[str]]],
    name: str,
) -> bool:
    try:
        result: bool
        if type(student) != type(expected):
            e = Exception(f"Expected {type(expected)}, but got {type(student)}")
            note = mk_note(type(student), type(expected), "TYPE")
            e.add_note(note)
            raise e
        if isinstance(student, list):
            test_any(len(student), len(expected), crash, fields, "len()")
            for i in range(len(student)):
                field = f"[{i}]"
                result = test_any(student[i], expected[i], crash, fields, field)
                if not result:
                    return False
            return True
        if isinstance(student, dict):
            test_any(set(student.keys()), set(expected.keys()), crash, fields, "keys()")
            for k in student.keys():
                field = f"[{k}]"
                result = test_any(student[k], expected[k], crash, fields, field)
                if not result:
                    return False
            return True
        count = 0
        for cls, f in fields:
            if isinstance(student, cls):
                count += 1
                for field in f:
                    sfield = getattr(student, field)
                    efield = getattr(expected, field)
                    result = test_any(sfield, efield, crash, fields, field)
                    if not result:
                        return False
    except Exception as d:
        note = mk_note(student, expected, name)
        d.add_note(note)
        raise d
    # except:
    #     if crash:
    #         raise
    #     return False
    if count == 0:  # base case
        if student != expected:
            e = Exception(f"Expected {expected}, but got {student}")
            note = mk_note(student, expected, name)
            e.add_note(note)
            raise e
    return True


def test_scanner(student: list[Token], expected: list[Token], crash: bool) -> bool:
    return test_any(student, expected, crash, [], "tokens")


def run_scanner(input: str) -> list[Token]:
    from scanner import Scanner

    lexer: Scanner = Scanner(input)
    return list(lexer)


def test_generic(student: Any, expected: Any, crash: bool) -> bool:
    return test_any(student, expected, crash, [], "generic")


def test_pass(student: Any, expected: Any, crash: bool) -> bool:
    return True


def run_parser(input: str):
    from scanner import Scanner

    lexer: Scanner = Scanner(input)
    from parse import Parser

    psr: Parser = Parser(lexer)
    tree: Any = psr.parse()
    return None  # need to remove after m5


def test_ast(student: Any, expected: Any, crash: bool) -> bool:
    return test_any(
        student, expected, crash, fields["ast"] + fields["decorations"], "ast"
    )


def test_binding(student: Any, expected: Any, crash: bool) -> bool:
    return test_any(
        student,
        expected,
        crash,
        fields["ast"] + fields["decorations"] + fields["binding"],
        "ast",
    )


def test_typecheck(student: Any, expected: Any, crash: bool) -> bool:
    return test_any(
        student,
        expected,
        crash,
        fields["ast"] + fields["decorations"] + fields["binding"] + fields["typecheck"],
        "ast",
    )


def test_offsets(student: Any, expected: Any, crash: bool) -> bool:
    return test_any(
        student,
        expected,
        crash,
        fields["ast"]
        + fields["decorations"]
        + fields["binding"]
        + fields["typecheck"]
        + fields["offsets"],
        "ast",
    )


def test_assign(student: Any, expected: Any, crash: bool) -> bool:
    return test_any(
        student,
        expected,
        crash,
        fields["ast"]
        + fields["decorations"]
        + fields["binding"]
        + fields["typecheck"]
        + fields["offsets"]
        + fields["assign"],
        "ast",
    )


def test_codegen(student: Any, expected: Any, crash: bool) -> bool:
    return test_assign(student, expected, crash)


def test_codegen_flow(student: Any, expected: Any, crash: bool) -> bool:
    try:
        v = test_assign(student, expected, crash)
        # test_flow(student, expected, crash)
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

    psr: Parser = Parser(lexer)
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


def run_assign(input: str):
    tree = run_offsets(input)
    import assign

    assign.process(tree)
    return tree


def run_codegen(input: str):
    tree = run_assign(input)
    import assign

    assign.process(tree)

    import codegen
    from vm import vm_utils
    from vm.vm_insns import Insn

    insns: list[Insn] = codegen.process(tree)

    vm_utils.invoke_vm(insns, [], False)
    return tree


def run_errors(input: str):
    try:
        tree = run_ast(input)
        import bindings

        bindings.process(tree)
        import typecheck

        typecheck.process(tree)
        import offsets

        offsets.process(tree)
        import codegen

        codegen.process(tree)
    except CompileError as e:
        return "CompileError"
    except Exception as e:
        return f"Other Error: {e}"
    return "<No error>"
