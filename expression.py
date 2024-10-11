# expression.py

from tokens import Token

from dataclasses import dataclass


class Expression:
    pass


# -------------------------------------------------------------------------------
@dataclass
class Binary(Expression):
    left: Expression
    operator: Token
    right: Expression


@dataclass
class Grouping(Expression):
    expression: Expression


@dataclass
class Literal(Expression):
    value: object


@dataclass
class Unary(Expression):
    operator: Token
    right: Expression
