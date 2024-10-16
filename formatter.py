# formatter

import expression as Expr
import statement as Stmt

from context import Context
from parser import Parser
from scanner import Scanner


class Formatter:
    def __init__(self, indent=4):
        self.indent = indent

    def format(self, statements: list[Stmt.Statement]) -> str:
        lines = []
        for stmt in statements:
            lines.append(self.format_stmt(stmt))
        return "\n".join(lines)

    def stringify(self, value):
        match value:
            case True:
                return "true"
            case False:
                return "false"

            case None:
                return "nil"

            case _:
                return value

    def format_stmt(self, statement: Stmt.Statement) -> str:
        match statement:
            case Stmt.Print(expr):
                return f"print {self.format_expr(expr)};"

            case Stmt.Expression(expr):
                return f"{self.format_expr(expr)};"

            case Stmt.Var(name, initializer):
                return (
                    f"var {name.lexeme};"
                    if initializer is None
                    else f"var {name} = {self.format_expr(initializer)}"
                )

            case _:
                raise NotImplementedError

    def format_expr(self, expression: Expr.Expression) -> str:
        match expression:
            case Expr.Binary(op, left, right):
                return f"{self.format_expr(left)} {op.lexeme} {self.format_expr(right)}"

            case Expr.Grouping(expr):
                return f"({self.format_expr(expr)})"

            case Expr.Literal(value):
                return f"{self.stringify(value)}"

            case Expr.Unary(op, right):
                return f"{op.lexeme}{self.format_expr(right)}"

            case _:
                raise NotImplementedError


if __name__ == "__main__":
    src = "print (   123.0000 == (100+ 23))!=false;"

    context = Context(src)
    scanner = Scanner(context)
    context.tokens = scanner.scan_tokens()

    parser = Parser(context)
    stmts = parser.parse()

    assert stmts is not None
    print(Formatter().format(stmts))
