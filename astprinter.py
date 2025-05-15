# astprinter.py

import expression as Expr


class ASTPrinter:
    def wrap(self, name, expressions):
        strings = [self.print(expr) for expr in expressions]
        return f"({name} {' '.join(strings)})"

    def print(self, expr: Expr.Expression) -> str:
        match expr:
            case Expr.Binary():
                return self.wrap(expr.operator.lexeme, [expr.left, expr.right])

            case Expr.Grouping():
                return self.wrap("grp", [expr.expression])

            case Expr.Literal():
                return f"{expr.value}"

            case Expr.Unary():
                return self.wrap(expr.operator.lexeme, [expr.right])

            case _:
                raise NotImplementedError
