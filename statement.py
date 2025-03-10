# statement

from dataclasses import dataclass

import expression as Expr
from tokens import Token


class Statement:
    pass


# -------------------------------------------------------------------------------
@dataclass
class Expression(Statement):
    expression: Expr.Expression


@dataclass
class Print(Statement):
    expression: Expr.Expression


@dataclass
class Var(Statement):
    name: Token
    initializer: Expr.Expression | None


@dataclass
class Block(Statement):
    statements: list[Statement]


@dataclass
class If(Statement):
    condition: Expr.Expression
    consequence: Statement
    alternative: Statement | None


@dataclass
class While(Statement):
    condition: Expr.Expression
    body: Statement


@dataclass
class Function(Statement):
    name: Token
    params: list[Token]
    body: list[Statement]


@dataclass
class Return(Statement):
    keyword: Token
    value: Expr.Expression | None


@dataclass
class Class(Statement):
    name: Token
    superclass: Expr.Variable | None
    methods: list[Function]
