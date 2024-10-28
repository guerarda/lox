# interpreter

import logging
from formatter import Formatter

import expression as Expr
import statement as Stmt
from environment import Environment
from errors import LoxError
from loxcallable import LoxCallable, Return
from loxfunction import LoxFunction
from tokens import Token


class InterpreterError(LoxError):
    pass


class InterpreterTokenError(InterpreterError):
    def __init__(self, token: Token, message: str):
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
    def __init__(self, environment: Environment | None = None):
        self.environment = environment if environment is not None else Environment()
        self.logger = logging.getLogger("Lox.Interpreter")

    def interpret(self, statements: list[Stmt.Statement]):
        try:
            self.execute_statements(statements)

        except LoxError as e:
            self.logger.error(e)
            raise e

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

    # Interpreting Expressions
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

            case Expr.Variable(name):
                return self.environment.get(name)

            case Expr.Assignment(name, value):
                self.environment.assign(name, self.evaluate(value))

            case Expr.Logical(Token.Type.OR, left, right):
                lv = self.evaluate(left)
                if self.is_truthy(lv):
                    return lv
                return self.evaluate(right)

            case Expr.Logical(Token.Type.AND, left, right):
                lv = self.evaluate(left)
                if not self.is_truthy(lv):
                    return lv
                return self.evaluate(right)

            case Expr.Call(callee, paren, args):
                cv = self.evaluate(callee)
                argv = [self.evaluate(arg) for arg in args]

                if not isinstance(cv, LoxCallable):
                    raise InterpreterTokenError(
                        paren, "Can only call functions and classes"
                    )

                if len(argv) != cv.arity():
                    raise InterpreterTokenError(
                        paren,
                        f"Expected {cv.arity()} arguments, got {len(argv)} instead",
                    )
                return cv.call(self, argv)

            case _:
                raise InterpreterExpressionError(
                    expression, "Could not evaluate Expression"
                )

    # Executing Statements
    def execute(self, statement: Stmt.Statement):
        match statement:
            case Stmt.Print(expr):
                print(self.stringify(self.evaluate(expr)))

            case Stmt.Expression(expr):
                self.evaluate(expr)

            case Stmt.Function():
                function = LoxFunction(statement, self.environment)
                self.environment.define(statement.name.lexeme, function)

            case Stmt.Var(name, initializer):
                value = None
                if initializer is not None:
                    value = self.evaluate(initializer)

                self.environment.define(name.lexeme, value)

            case Stmt.Block(stmts):
                self.execute_block(stmts, Environment(self.environment))

            case Stmt.If(cond, conseq, alt):
                if self.is_truthy(self.evaluate(cond)):
                    self.execute(conseq)
                elif alt is not None:
                    self.execute(alt)

            case Stmt.While(cond, body):
                while self.is_truthy(self.evaluate(cond)):
                    self.execute(body)

            case Stmt.Return(_, value):
                raise Return(None if value is None else self.evaluate(value))

            case _:
                raise InterpreterStatementError(
                    statement, "Could not execute Statement"
                )

    def execute_block(self, statements: list[Stmt.Statement], environment: Environment):
        previous = self.environment
        try:
            self.environment = environment
            self.execute_statements(statements)
        finally:
            self.environment = previous

    def execute_statements(self, statements: list[Stmt.Statement]):
        for stmt in statements:
            self.execute(stmt)


class REPLInterpreter(Interpreter):
    def execute(self, statement: Stmt.Statement):
        if isinstance(statement, Stmt.Expression):
            print(self.stringify(self.evaluate(statement.expression)))
        else:
            super().execute(statement)


if __name__ == "__main__":
    Interpreter().interpret([Stmt.Print(Expr.Literal(2.0))])
