# ASTPrinter

from expression import *


class ASTPrinter:
    def wrap(self, name, expressions):
        strings = [self.print(expr) for expr in expressions]
        return f"({name} {" ".join(strings)})"

    def print(self, expr: Expression) -> str:
        match expr:
            case Binary():
                return self.wrap(expr.operator.lexeme, [expr.left, expr.right])

            case Grouping():
                return self.wrap("grouping", [expr.expression])

            case Literal():
                return f"{expr.value}" if expr.value else "nil"

            case Unary():
                return self.wrap(expr.operator.lexeme, [expr.right])

            case _:
                raise Exception
