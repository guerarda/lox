# interpreter

import expression as Expr
import statement as Stmt
from formatter import Formatter
from tokens import Token

import logging


class InterpreterError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message


class InterpreterTokenError(InterpreterError):
    def __init__(self, token, message):
        super().__init__(message)
        self.token = token
        self.message = message

    def __str__(self):
        return f"line {self.token.line + 1}, {self.message}"


class InterpreterExpressionError(InterpreterError):
    def __init__(self, expression: Expr.Expression, message: str):
        super().__init__(message)
        self.expression = expression
        self.message = message

    def __str__(self):
        return f"{self.message} '{self.expression}'"


class InterpreterStatementError(InterpreterError):
    def __init__(self, statement: Stmt.Statement, message: str):
        super().__init__(message)
        self.statement = statement
        self.message = message

    def __str__(self):
        print(Formatter().format_stmt(self.statement))
        return f"{self.message} '{Formatter().format_stmt(self.statement)}'"


class Interpreter:
    def __init__(self, context=None):
        self.context = context
        self.logger = logging.getLogger("Lox.Interpreter")

    def interpret(self, statements: list[Stmt.Statement]):
        try:
            self.execute_statements(statements)

        except InterpreterError as e:
            self.logger.error(e)
            if self.context:
                self.context.has_runtime_error = True

    # Private functions
    def is_truthy(self, obj) -> bool:
        match obj:
            case None:
                return False

            case bool():
                return obj

            case _:
                return True

    def is_equal(self, left, right) -> bool:
        return left == right

    def check_number_operand(self, operator: Token, operand):
        if not isinstance(operand, float):
            raise InterpreterTokenError(operator, "Operand must be a number")

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

    def evaluate(self, expression: Expr.Expression):
        match expression:
            case Expr.Literal():
                return expression.value

            case Expr.Unary(Token(Token.Type.BANG), right):
                return not self.is_truthy(self.evaluate(right))

            case Expr.Unary(Token(Token.Type.MINUS), right):
                rv = self.evaluate(right)
                self.check_number_operand(expression.operator, rv)
                return -float(rv)

            case Expr.Binary(Token(Token.Type.MINUS), left, right):
                lv = self.evaluate(left)
                self.check_number_operand(expression.operator, lv)

                rv = self.evaluate(right)
                self.check_number_operand(expression.operator, rv)

                return float(lv) - float(rv)

            case Expr.Binary(Token(Token.Type.PLUS), left, right):
                lv = self.evaluate(left)
                self.check_number_operand(expression.operator, lv)

                rv = self.evaluate(right)
                self.check_number_operand(expression.operator, rv)

                return float(lv) + float(rv)

            case Expr.Binary(Token(Token.Type.STAR), left, right):
                lv = self.evaluate(left)
                self.check_number_operand(expression.operator, lv)

                rv = self.evaluate(right)
                self.check_number_operand(expression.operator, rv)

                return float(lv) * float(rv)

            case Expr.Binary(Token(Token.Type.SLASH), left, right):

                lv = self.evaluate(left)
                self.check_number_operand(expression.operator, lv)

                rv = self.evaluate(right)
                self.check_number_operand(expression.operator, rv)

                if rv == 0.0:
                    raise InterpreterTokenError(expression.operator, "Division by zero")

                return float(lv) / float(rv)

            case Expr.Binary(Token(Token.Type.GREATER), left, right):
                lv = self.evaluate(left)
                self.check_number_operand(expression.operator, lv)

                rv = self.evaluate(right)
                self.check_number_operand(expression.operator, rv)

                return float(lv) > float(rv)

            case Expr.Binary(Token(Token.Type.GREATER_EQUAL), left, right):
                lv = self.evaluate(left)
                self.check_number_operand(expression.operator, lv)

                rv = self.evaluate(right)
                self.check_number_operand(expression.operator, rv)

                return float(lv) >= float(rv)

            case Expr.Binary(Token(Token.Type.LESS), left, right):
                lv = self.evaluate(left)
                self.check_number_operand(expression.operator, lv)

                rv = self.evaluate(right)
                self.check_number_operand(expression.operator, rv)

                return float(lv) < float(rv)

            case Expr.Binary(Token(Token.Type.LESS_EQUAL), left, right):
                lv = self.evaluate(left)
                self.check_number_operand(expression.operator, lv)

                rv = self.evaluate(right)
                self.check_number_operand(expression.operator, rv)

                return float(lv) <= float(rv)

            case Expr.Binary(Token(Token.Type.EQUAL_EQUAL), left, right):
                return self.is_equal(left, right)

            case Expr.Binary(Token(Token.Type.BANG_EQUAL), left, right):
                return not self.is_equal(left, right)

            case Expr.Grouping(expr):
                return self.evaluate(expr)

            case _:
                raise InterpreterExpressionError(
                    expression, "Could not evaluate Expression"
                )

    def execute(self, statement: Stmt.Statement):
        match statement:
            case Stmt.Print(expr):
                print(self.stringify(self.evaluate(expr)))

            case Stmt.Expression(expr):
                self.evaluate(expr)

            case _:
                raise InterpreterStatementError(
                    statement, "Could not execute Statement"
                )

    def execute_statements(self, statements: list[Stmt.Statement]):
        for stmt in statements:
            self.execute(stmt)


if __name__ == "__main__":
    Interpreter().interpret([Stmt.Print(Expr.Literal(2.0))])
