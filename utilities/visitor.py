# pyright: reportUnboundVariable=none, reportUnusedFunction=none
from typing import Callable
from dataclasses import dataclass

from tau import asts


@dataclass
class Visitor:
    fn: Callable[[asts.AST], None]

    def AST(self, ast: asts.AST) -> None:
        match ast:
            case asts.Argument():
                self.Argument(ast)
            case asts.Id():
                self.Id(ast)
            case asts.Program():
                self.Program(ast)
            case asts.Decl():
                self.Decl(ast)
            case asts.Expr():
                self.Expr(ast)
            case asts.Stmt():
                self.Stmt(ast)
            case asts.TypeAST():
                self.TypeAST(ast)
            case _:
                raise NotImplementedError(f"Unknown type {ast}")

    def Argument(self, ast: asts.Argument) -> None:
        self.fn(ast)
        self.Expr(ast.expr)

    def Id(self, ast: asts.Id) -> None:
        self.fn(ast)

    def Program(self, ast: asts.Program) -> None:
        self.fn(ast)
        for decl in ast.decls:
            self.FuncDecl(decl)

    def Decl(self, ast: asts.Decl) -> None:
        match ast:
            case asts.FuncDecl():
                self.FuncDecl(ast)
            case asts.ParamDecl():
                self.ParamDecl(ast)
            case asts.VarDecl():
                self.VarDecl(ast)
            case _:
                raise NotImplementedError(f"Unknown type {ast}")

    def FuncDecl(self, ast: asts.FuncDecl) -> None:
        self.fn(ast)
        self.Id(ast.id)
        for param in ast.params:
            self.ParamDecl(param)
        self.TypeAST(ast.ret_type_ast)
        self.CompoundStmt(ast.body)

    def ParamDecl(self, ast: asts.ParamDecl) -> None:
        self.fn(ast)
        self.Id(ast.id)
        self.TypeAST(ast.type_ast)

    def VarDecl(self, ast: asts.VarDecl) -> None:
        self.fn(ast)
        self.Id(ast.id)
        self.TypeAST(ast.type_ast)

    def Expr(self, ast: asts.Expr) -> None:
        match ast:
            case asts.ArrayCell():
                self.ArrayCell(ast)
            case asts.BinaryOp():
                self.BinaryOp(ast)
            case asts.BoolLiteral():
                self.BoolLiteral(ast)
            case asts.CallExpr():
                self.CallExpr(ast)
            case asts.IdExpr():
                self.IdExpr(ast)
            case asts.IntLiteral():
                self.IntLiteral(ast)
            case asts.UnaryOp():
                self.UnaryOp(ast)
            case _:
                raise NotImplementedError(f"Unknown type {ast}")

    def ArrayCell(self, ast: asts.ArrayCell) -> None:
        self.fn(ast)
        self.Expr(ast.arr)
        self.Expr(ast.idx)

    def BinaryOp(self, ast: asts.BinaryOp) -> None:
        self.fn(ast)
        self.Expr(ast.left)
        self.Expr(ast.right)

    def BoolLiteral(self, ast: asts.BoolLiteral) -> None:
        self.fn(ast)

    def CallExpr(self, ast: asts.CallExpr) -> None:
        self.fn(ast)
        self.Expr(ast.fn)
        for arg in ast.args:
            self.Argument(arg)

    def IdExpr(self, ast: asts.IdExpr) -> None:
        self.fn(ast)
        self.Id(ast.id)

    def IntLiteral(self, ast: asts.IntLiteral) -> None:
        self.fn(ast)

    def UnaryOp(self, ast: asts.UnaryOp) -> None:
        self.fn(ast)
        self.Expr(ast.expr)

    def Stmt(self, ast: asts.Stmt) -> None:
        match ast:
            case asts.AssignStmt():
                self.AssignStmt(ast)
            case asts.CallStmt():
                self.CallStmt(ast)
            case asts.CompoundStmt():
                self.CompoundStmt(ast)
            case asts.IfStmt():
                self.IfStmt(ast)
            case asts.PrintStmt():
                self.PrintStmt(ast)
            case asts.ReturnStmt():
                self.ReturnStmt(ast)
            case asts.WhileStmt():
                self.WhileStmt(ast)
            case _:
                raise NotImplementedError(f"Unknown type {ast}")

    def AssignStmt(self, ast: asts.AssignStmt) -> None:
        self.fn(ast)
        self.Expr(ast.lhs)
        self.Expr(ast.rhs)

    def CallStmt(self, ast: asts.CallStmt) -> None:
        self.fn(ast)
        self.CallExpr(ast.call)

    def CompoundStmt(self, ast: asts.CompoundStmt) -> None:
        self.fn(ast)
        for decl in ast.decls:
            self.VarDecl(decl)
        for stmt in ast.stmts:
            self.Stmt(stmt)

    def IfStmt(self, ast: asts.IfStmt) -> None:
        self.fn(ast)
        self.Expr(ast.expr)
        self.CompoundStmt(ast.thenStmt)
        if ast.elseStmt:
            self.CompoundStmt(ast.elseStmt)

    def PrintStmt(self, ast: asts.PrintStmt) -> None:
        self.fn(ast)
        self.Expr(ast.expr)

    def ReturnStmt(self, ast: asts.ReturnStmt) -> None:
        self.fn(ast)
        if ast.expr:
            self.Expr(ast.expr)

    def WhileStmt(self, ast: asts.WhileStmt) -> None:
        self.fn(ast)
        self.Expr(ast.expr)
        self.CompoundStmt(ast.stmt)

    def TypeAST(self, ast: asts.TypeAST) -> None:
        match ast:
            case asts.ArrayTypeAST():
                self.ArrayType(ast)
            case asts.BoolTypeAST():
                self.BoolType(ast)
            case asts.IntTypeAST():
                self.IntType(ast)
            case asts.VoidTypeAST():
                self.VoidType(ast)
            case _:
                raise NotImplementedError(f"Unknown type {ast}")

    def ArrayType(self, ast: asts.ArrayTypeAST) -> None:
        self.fn(ast)
        self.TypeAST(ast.element_type_ast)

    def BoolType(self, ast: asts.BoolTypeAST) -> None:
        self.fn(ast)

    def IntType(self, ast: asts.IntTypeAST) -> None:
        self.fn(ast)

    def VoidType(self, ast: asts.VoidTypeAST) -> None:
        self.fn(ast)
