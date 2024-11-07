# resolver

import logging
from enum import Enum, auto
from functools import singledispatchmethod
from typing import Any

import expression as Expr
import statement as Stmt
from interpreter import Interpreter
from tokens import Token


class FunctionType(Enum):
    NONE = (auto(),)
    FUNCTION = auto()


class Resolver:
    def __init__(self, interpreter: Interpreter):
        self.interpreter = interpreter
        self.scopes: list[dict[str, bool]] = []
        self.current_fn = FunctionType.NONE
        self.has_error = False
        self.logger = logging.getLogger("Lox.Resolver")

    @singledispatchmethod
    def resolve(self, node: Any) -> None:
        if isinstance(node, list):
            for stmt in node:
                self.resolve(stmt)
        else:
            raise TypeError

    @resolve.register
    def _(self, expression: Expr.Expression) -> None:
        match expression:
            case Expr.Variable(name):
                if self.scopes and self.scopes[-1][name.lexeme] is False:
                    self.error("Can't read local variable in its own initializer")

                    self.resolve_local(expression, name)

            case Expr.Assignment(name, value):
                self.resolve(value)
                self.resolve_local(expression, name)

            case Expr.Binary(_, left, right):
                self.resolve(left)
                self.resolve(right)

            case Expr.Logical(_, left, right):
                self.resolve(left)
                self.resolve(right)

            case Expr.Unary(_, right):
                self.resolve(right)

            case Expr.Call(callee, _, args):
                self.resolve(callee)
                for arg in args:
                    self.resolve(arg)

            case Expr.Grouping(expr):
                self.resolve(expr)

            case Expr.Literal():
                return

            case _:
                raise NotImplemented

    @resolve.register
    def _(self, statement: Stmt.Statement) -> None:
        match statement:
            case Stmt.Block(statements):
                self.begin_scope()
                self.resolve(statements)
                self.end_scope()

            case Stmt.Var(name, initializer):
                self.declare(name)
                if initializer is not None:
                    self.resolve(initializer)

                self.define(name)

            case Stmt.Function(name, _, _):
                self.declare(name)
                self.define(name)
                self.resolve_function(statement, FunctionType.FUNCTION)

            case Stmt.Expression(expr):
                self.resolve(expr)

            case Stmt.If(cond, cons, alt):
                self.resolve(cond)
                self.resolve(cons)

                if alt is not None:
                    self.resolve(alt)

            case Stmt.Print(expr):
                self.resolve(expr)

            case Stmt.Return(token, value):
                if self.current_fn is FunctionType.NONE:
                    self.error(
                        f"Line {token.line}, Can't return from top-level function"
                    )
                if value is not None:
                    self.resolve(value)

            case Stmt.While(cond, body):
                self.resolve(cond)
                self.resolve(body)

            case _:
                raise NotImplemented

    def begin_scope(self):
        self.scopes.append({})

    def end_scope(self):
        self.scopes.pop()

    def declare(self, name: Token):
        if self.scopes:
            scope = self.scopes[-1]
            if name.lexeme in scope:
                self.error(
                    f"Line {name.line}, Already a variable with the name '{name.lexeme}' in scope."
                )

            scope[name.lexeme] = False

    def define(self, name: Token):
        if self.scopes:
            self.scopes[-1][name.lexeme] = True

    def resolve_local(self, expression: Expr.Expression, name: Token):
        for i, scope in enumerate(reversed(self.scopes)):
            if name.lexeme in scope:
                self.interpreter.resolve(expression, i)

    def resolve_function(self, function: Stmt.Function, type: FunctionType):
        enclosing_fn = self.current_fn
        self.current_fn = type

        self.begin_scope()
        for param in function.params:
            self.declare(param)
            self.define(param)

        self.resolve(function.body)
        self.end_scope()

        self.current_fn = enclosing_fn

    def error(self, message: str):
        self.logger.error(message)
        self.has_error = True
