# expression

from dataclasses import dataclass

from tokens import Token


class Expression:
    pass


# -------------------------------------------------------------------------------
@dataclass
class Binary(Expression):
    operator: Token
    left: Expression
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


@dataclass
class Variable(Expression):
    name: Token


@dataclass
class Assignment(Expression):
    name: Token
    value: Expression


@dataclass
class Logical(Expression):
    operator: Token
    left: Expression
    right: Expression


@dataclass
class Call(Expression):
    callee: Expression
    paren: Token
    args: list[Expression]


@dataclass
class Get(Expression):
    target: Expression
    name: Token


@dataclass
class Set(Expression):
    target: Expression
    name: Token
    value: Expression
