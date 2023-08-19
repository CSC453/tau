from typing import Callable, Optional
from .asts import (
    AST,
    Program,
    FuncDecl,
    Id,
    VarDecl,
    ParamDecl,
    IntType,
    BoolType,
    VoidType,
    ArrayType,
    PrintStmt,
    CompoundStmt,
    CallExpr,
    AssignStmt,
    IfStmt,
    WhileStmt,
    ReturnStmt,
    CallStmt,
    BinaryOp,
    UnaryOp,
    ArrayCell,
    IdExpr,
    IntLiteral,
    BoolLiteral,
)


def assert_equal(
    correct: Optional[AST],
    other: Optional[AST],
    fn: Callable[[AST, AST], bool],
) -> bool:
    assert type(correct) == type(other), f"{type(correct)} != {type(other)}"
    match (correct, other):
        case (Program(), Program()):
            assert len(correct.decls) == len(
                other.decls
            ), f"{len(correct.decls)} != {len(other.decls)}"
            for i in range(len(correct.decls)):
                assert_equal(correct.decls[i], other.decls[i], fn)
            fn(correct, other)
        case (Id(), Id()):
            fn(correct, other)
        case (VarDecl(), VarDecl()):
            assert_equal(correct.id, other.id, fn)
            assert_equal(correct.type_ast, other.type_ast, fn)
            fn(correct, other)
        case (ParamDecl(), ParamDecl()):
            assert_equal(correct.id, other.id, fn)
            assert_equal(correct.type_ast, other.type_ast, fn)
            fn(correct, other)
        case (IntType(), IntType()):
            fn(correct, other)
        case (BoolType(), BoolType()):
            fn(correct, other)
        case (VoidType(), VoidType()):
            fn(correct, other)
        case (ArrayType(), ArrayType()):
            assert (
                correct.size == other.size
            ), f"{correct.size} != {other.size}"
            assert_equal(correct.element_type_ast, other.element_type_ast, fn)
            fn(correct, other)
        case (PrintStmt(), PrintStmt()):
            assert_equal(correct.expr, other.expr, fn)
            fn(correct, other)
        case (CompoundStmt(), CompoundStmt()):
            assert len(correct.decls) == len(
                other.decls
            ), f"{len(correct.decls)} != {len(other.decls)}"
            for i in range(len(correct.decls)):
                assert_equal(correct.decls[i], other.decls[i], fn)
            assert len(correct.stmts) == len(
                other.stmts
            ), f"{len(correct.stmts)} != {len(other.stmts)}"
            for i in range(len(correct.stmts)):
                assert_equal(correct.stmts[i], other.stmts[i], fn)
            fn(correct, other)
        case (CallStmt(), CallStmt()):
            assert_equal(correct.call, other.call, fn)
            fn(correct, other)
        case (FuncDecl(), FuncDecl()):
            assert_equal(correct.id, other.id, fn)
            assert len(correct.params) == len(
                other.params
            ), f"{len(correct.params)} != {len(other.params)}"
            for i in range(len(correct.params)):
                assert_equal(correct.params[i], other.params[i], fn)
            assert_equal(correct.ret_type_ast, other.ret_type_ast, fn)
            assert_equal(correct.body, other.body, fn)
            fn(correct, other)
        case (CallExpr(), CallExpr()):
            assert_equal(correct.fn, other.fn, fn)
            assert len(correct.args) == len(
                other.args
            ), f"{len(correct.args)} != {len(other.args)}"
            for i in range(len(correct.args)):
                assert_equal(correct.args[i], other.args[i], fn)
            fn(correct, other)
        case (AssignStmt(), AssignStmt()):
            assert_equal(correct.lhs, other.lhs, fn)
            assert_equal(correct.rhs, other.rhs, fn)
            fn(correct, other)
        case (IfStmt(), IfStmt()):
            assert_equal(correct.expr, other.expr, fn)
            assert_equal(correct.thenStmt, other.thenStmt, fn)
            assert_equal(correct.elseStmt, other.elseStmt, fn)
            fn(correct, other)
        case (WhileStmt(), WhileStmt()):
            assert_equal(correct.expr, other.expr, fn)
            assert_equal(correct.stmt, other.stmt, fn)
            fn(correct, other)
        case (ReturnStmt(), ReturnStmt()):
            assert_equal(correct.expr, other.expr, fn)
            fn(correct, other)
        case (BinaryOp(), BinaryOp()):
            assert_equal(correct.left, other.left, fn)
            assert_equal(correct.right, other.right, fn)
            fn(correct, other)
        case (UnaryOp(), UnaryOp()):
            assert_equal(correct.expr, other.expr, fn)
            fn(correct, other)
        case (ArrayCell(), ArrayCell()):
            assert_equal(correct.arr, other.arr, fn)
            assert_equal(correct.idx, other.idx, fn)
            fn(correct, other)
        case (IntLiteral(), IntLiteral()):
            fn(correct, other)
        case (BoolLiteral(), BoolLiteral()):
            fn(correct, other)
        case (IdExpr(), IdExpr()):
            assert_equal(correct.id, other.id, fn)
            fn(correct, other)
        case (None, None):
            pass
        case _:  # pragma: no cover
            raise NotImplementedError(
                "Unknown AST node type: " + str(type(correct))
            )

    return True
