# analyzer

import logging
from enum import Enum, auto

import expression as Expr
import statement as Stmt
from errors import LoxError
from tokens import Token


class FunctionType(Enum):
    NONE = (auto(),)
    FUNCTION = (auto(),)
    METHOD = (auto(),)
    INITIALIZER = auto()


class ClassType(Enum):
    NONE = (auto(),)
    CLASS = auto()


class AnalyzerError(LoxError):
    def __init__(self, token: Token, message: str):
        super().__init__(message)
        self.token = token
        self.message = message

    def __str__(self):
        return (
            f"{self.token.line + 1} | Error at '{self.token.lexeme}': {self.message}."
        )


class Analyzer:
    def __init__(self):
        self.scopes: list[dict[str, bool]] = []
        self.functions: list[FunctionType] = [FunctionType.NONE]
        self.classes: list[ClassType] = [ClassType.NONE]
        self.logger = logging.getLogger("Lox.Analyzer")

    def analyze(self, statements: list[Stmt.Statement]):
        try:
            self.analyze_list(statements)
        except LoxError as e:
            self.logger.error(e)
            raise e

    def analyze_list(self, statements: list[Stmt.Statement]):
        for stmt in statements:
            self.analyze_one(stmt)

    def analyze_one(self, stmt_or_expr: Stmt.Statement | Expr.Expression):
        match stmt_or_expr:
            case Stmt.Block(stmts):
                self.begin_scope()
                self.analyze(stmts)
                self.end_scope()

            case Stmt.Var(name, initializer):
                self.declare(name)
                if initializer:
                    self.analyze_one(initializer)
                self.define(name)

            case Stmt.Function(name, _, _):
                self.declare(name)
                self.define(name)
                self.analyze_function(stmt_or_expr, FunctionType.FUNCTION)

            case Stmt.Class(name, superclass, methods):
                self.classes.append(ClassType.CLASS)

                self.declare(name)
                self.define(name)

                if superclass:
                    if name.lexeme == superclass.name.lexeme:
                        raise AnalyzerError(
                            superclass.name, "A class can't inherit from itself"
                        )
                    self.analyze_one(superclass)

                self.begin_scope()

                self.scopes[-1]["this"] = True
                for m in methods:
                    fntype = (
                        FunctionType.INITIALIZER
                        if m.name.lexeme == "init"
                        else FunctionType.METHOD
                    )
                    self.analyze_function(m, fntype)

                self.end_scope()
                self.classes.pop()

            case Stmt.Expression(expr):
                self.analyze_one(expr)

            case Stmt.If(cond, cons, alt):
                self.analyze_one(cond)
                self.analyze_one(cons)
                if alt:
                    self.analyze_one(alt)

            case Stmt.Print(expr):
                self.analyze_one(expr)

            case Stmt.Return(keyword, value):
                if self.functions[-1] == FunctionType.NONE:
                    raise AnalyzerError(keyword, "Can't return from top-level code")

                if value:
                    if self.functions[-1] == FunctionType.INITIALIZER:
                        raise AnalyzerError(
                            keyword, "Can't return a value from an initializer"
                        )

                    self.analyze_one(value)

            case Stmt.While(cond, body):
                self.analyze_one(cond)
                self.analyze_one(body)

            case Expr.Variable(name):
                if self.scopes:
                    scope = self.scopes[-1]
                    if not scope.get(name.lexeme, True):
                        raise AnalyzerError(
                            name, "Can't read local variable in its own initializer"
                        )

            case Expr.Assignment(name, value):
                self.analyze_one(value)

            case Expr.Binary(_, left, right):
                self.analyze_one(left)
                self.analyze_one(right)

            case Expr.Call(callee, _, args):
                self.analyze_one(callee)
                for arg in args:
                    self.analyze_one(arg)

            case Expr.Set(target, _, value):
                self.analyze_one(value)
                self.analyze_one(target)

            case Expr.Get(target):
                self.analyze_one(target)

            case Expr.Grouping(expr):
                self.analyze_one(expr)

            case Expr.Literal():
                return

            case Expr.Logical(_, left, right):
                self.analyze_one(left)
                self.analyze_one(right)

            case Expr.Unary(_, expr):
                self.analyze_one(expr)

            case Expr.This(keyword):
                if self.classes[-1] == ClassType.NONE:
                    raise AnalyzerError(keyword, "Can't use 'this' outside of a class")
                return

            case _:
                raise NotImplementedError

    def analyze_function(self, stmt: Stmt.Function, fntype: FunctionType):
        self.functions.append(fntype)
        self.begin_scope()
        for param in stmt.params:
            self.declare(param)
            self.define(param)

        self.analyze_list(stmt.body)
        self.end_scope()
        self.functions.pop()

    def begin_scope(self):
        self.scopes.append({})

    def end_scope(self):
        self.scopes.pop()

    def declare(self, name: Token):
        if not self.scopes:
            return

        scope = self.scopes[-1]
        if name.lexeme in scope:
            raise AnalyzerError(name, "Already a variable with this name in this scope")
        scope[name.lexeme] = False

    def define(self, name: Token):
        if not self.scopes:
            return

        scope = self.scopes[-1]
        if name.lexeme in scope:
            scope[name.lexeme] = True
