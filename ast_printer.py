import expression as Expr


class sASTPrinter(Expr.Visitor):
    def print(self, expression):
        return expression.accept(self)

    def wrap(self, name, expressions):
        strings = [expr.accept(self) for expr in expressions]
        return f"({name} {" ".join(strings)})"

    def visit_binary(self, expr):
        return self.wrap(expr.operator.lexeme, [expr.left, expr.right])

    def visit_grouping(self, expr):
        return self.wrap("grouping", [expr.expression])

    def visit_literal(self, expr):
        return f"{expr.value}" if expr.value else "nil"

    def visit_unary(self, expr):
        return self.wrap(expr.operator.lexeme, [expr.right])
