# interpreted

import expression as Expression
from context import Context
from tokens import Token


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
        return f"[Line {self.token.line}] Error: {self.message}"


class InterpreterExpressionError(InterpreterError):
    def __init__(self, expression, message):
        super().__init__(message)
        self.expression = expression
        self.message = message

    def __str__(self):
        return f"Error: {self.message} '{self.expression}'"


class Interpreter:
    def __init__(self, context=None):
        self.context = context

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

    def interpret(self, expression: Expression.Expression):
        try:
            value = self.evaluate(expression)
            print(self.stringify(value))

        except InterpreterError as e:
            print(e)

            if self.context:
                self.context.has_runtime_error = True

    def evaluate(self, expression: Expression.Expression):
        match expression:
            case Expression.Literal():
                return expression.value

            case Expression.Unary(Token(Token.Type.BANG), right):
                return not self.is_truthy(self.evaluate(right))

            case Expression.Unary(Token(Token.Type.MINUS), right):
                rv = self.evaluate(right)
                self.check_number_operand(expression.operator, rv)
                return -float(rv)

            case Expression.Binary(Token(Token.Type.MINUS), left, right):
                lv = self.evaluate(left)
                self.check_number_operand(expression.operator, lv)

                rv = self.evaluate(right)
                self.check_number_operand(expression.operator, rv)

                return float(lv) - float(rv)

            case Expression.Binary(Token(Token.Type.PLUS), left, right):
                lv = self.evaluate(left)
                self.check_number_operand(expression.operator, lv)

                rv = self.evaluate(right)
                self.check_number_operand(expression.operator, rv)

                return float(lv) + float(rv)

            case Expression.Binary(Token(Token.Type.STAR), left, right):
                lv = self.evaluate(left)
                self.check_number_operand(expression.operator, lv)

                rv = self.evaluate(right)
                self.check_number_operand(expression.operator, rv)

                return float(lv) * float(rv)

            case Expression.Binary(Token(Token.Type.SLASH), left, right):

                lv = self.evaluate(left)
                self.check_number_operand(expression.operator, lv)

                rv = self.evaluate(right)
                self.check_number_operand(expression.operator, rv)

                if rv == 0.0:
                    raise InterpreterTokenError(expression.operator, "Division by zero")

                return float(lv) / float(rv)

            case Expression.Binary(Token(Token.Type.GREATER), left, right):
                lv = self.evaluate(left)
                self.check_number_operand(expression.operator, lv)

                rv = self.evaluate(right)
                self.check_number_operand(expression.operator, rv)

                return float(lv) > float(rv)

            case Expression.Binary(Token(Token.Type.GREATER_EQUAL), left, right):
                lv = self.evaluate(left)
                self.check_number_operand(expression.operator, lv)

                rv = self.evaluate(right)
                self.check_number_operand(expression.operator, rv)

                return float(lv) >= float(rv)

            case Expression.Binary(Token(Token.Type.LESS), left, right):
                lv = self.evaluate(left)
                self.check_number_operand(expression.operator, lv)

                rv = self.evaluate(right)
                self.check_number_operand(expression.operator, rv)

                return float(lv) < float(rv)

            case Expression.Binary(Token(Token.Type.LESS_EQUAL), left, right):
                lv = self.evaluate(left)
                self.check_number_operand(expression.operator, lv)

                rv = self.evaluate(right)
                self.check_number_operand(expression.operator, rv)

                return float(lv) <= float(rv)

            case Expression.Binary(Token(Token.Type.EQUAL_EQUAL), left, right):
                return self.is_equal(left, right)

            case Expression.Binary(Token(Token.Type.BANG_EQUAL), left, right):
                return not self.is_equal(left, right)

            case Expression.Grouping(expr):
                return self.evaluate(expr)

            case _:
                raise InterpreterExpressionError(
                    expression, "Couldn't not evaluate Expression"
                )


if __name__ == "__main__":
    Interpreter().interpret(
        Expression.Unary(Token.MINUS(), Expression.Literal(value=2.0))
    )
    Interpreter().interpret(
        Expression.Binary(
            Token.MINUS(),
            Expression.Literal(value=3.0),
            Expression.Literal(value=2.0),
        )
    )
