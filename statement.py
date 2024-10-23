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
