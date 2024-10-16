# statement

import expression as Expr

from dataclasses import dataclass


class Statement:
    pass


# -------------------------------------------------------------------------------
@dataclass
class Expression(Statement):
    expression: Expr.Expression


@dataclass
class Print(Statement):
    expression: Expr.Expression
