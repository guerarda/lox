# interpreter

import logging
import math
import time

import expression as Expr
import statement as Stmt
from environment import Environment
from errors import LoxError, LoxRuntimeError
from loxcallable import LoxCallable, Return
from loxclass import LoxClass
from loxfunction import LoxFunction
from loxinstance import LoxInstance
from tokens import Token


# Native functions
class Clock(LoxCallable):
    def arity(self):
        return 0

    def call(self, interpreter, args):
        return time.time()

    def __str__(self):
        return f"<native fn>"


class InterpreterError(LoxError):
    def __init__(self, token: Token, message: str):
        super().__init__(message)
        self.token = token
        self.message = message

    def __str__(self):
        return f"{self.token.line + 1} | {self.message}."


class Interpreter:
    def __init__(self, environment: Environment | None = None):
        self.globals = environment if environment else Environment()
        self.globals.define(Token.IDENTIFIER("clock"), Clock())

        self.environment = self.globals
        self.logger = logging.getLogger("Lox.Interpreter")

    def interpret(self, statements: list[Stmt.Statement]):
        has_error = False
        for stmt in statements:
            try:
                self.execute(stmt)

            except LoxError as e:
                self.logger.error(e)
                has_error = True

        if has_error:
            raise LoxError()

    def is_truthy(self, obj: object) -> bool:
        match obj:
            case None:
                return False

            case bool():
                return obj

            case _:
                return True

    def is_equal(self, left, right) -> bool:
        match [left, right]:
            case [bool(), bool()]:
                return left == right

            case [bool(), _] | [_, bool()]:
                return False

            case [_, math.inf] | [math.inf, _]:
                return False

            case _:
                return left == right

    def check_number_operand(self, operator: Token, operand: object):
        if not isinstance(operand, float):
            raise LoxRuntimeError(operator, "Operand must be a number")

    def check_number_operands(self, operator: Token, left: object, right: object):
        if not (isinstance(left, float) and isinstance(right, float)):
            raise LoxRuntimeError(operator, "Operands must be numbers")

    def stringify(self, value: object):
        match value:
            case True:
                return "true"
            case False:
                return "false"

            case None:
                return "nil"

            case float():
                return f"{value:g}"
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
                rv = self.evaluate(right)
                self.check_number_operands(expression.operator, lv, rv)

                return float(lv) - float(rv)

            case Expr.Binary(Token(Token.Type.PLUS), left, right):
                lv = self.evaluate(left)
                rv = self.evaluate(right)

                if isinstance(lv, str) and isinstance(rv, str):
                    return str(lv) + str(rv)

                if isinstance(lv, float) and isinstance(rv, float):
                    return float(lv) + float(rv)

                raise LoxRuntimeError(
                    expression.operator, "Operands must be two numbers or two strings"
                )

            case Expr.Binary(Token(Token.Type.STAR), left, right):
                lv = self.evaluate(left)
                rv = self.evaluate(right)
                self.check_number_operands(expression.operator, lv, rv)

                return float(lv) * float(rv)

            case Expr.Binary(Token(Token.Type.SLASH), left, right):
                lv = self.evaluate(left)
                rv = self.evaluate(right)

                # Python throws an exception when dividing by zero.
                # Unlike java on top of which Lox is implemented. We
                # want the same behavior so we have to handle this
                # case specifically.
                if rv == 0.0:
                    return math.inf

                self.check_number_operands(expression.operator, lv, rv)

                return float(lv) / float(rv)

            case Expr.Binary(Token(Token.Type.GREATER), left, right):
                lv = self.evaluate(left)
                rv = self.evaluate(right)
                self.check_number_operands(expression.operator, lv, rv)
                return float(lv) > float(rv)

            case Expr.Binary(Token(Token.Type.GREATER_EQUAL), left, right):
                lv = self.evaluate(left)
                rv = self.evaluate(right)
                self.check_number_operands(expression.operator, lv, rv)

                return float(lv) >= float(rv)

            case Expr.Binary(Token(Token.Type.LESS), left, right):
                lv = self.evaluate(left)
                rv = self.evaluate(right)
                self.check_number_operands(expression.operator, lv, rv)

                return float(lv) < float(rv)

            case Expr.Binary(Token(Token.Type.LESS_EQUAL), left, right):
                lv = self.evaluate(left)
                rv = self.evaluate(right)
                self.check_number_operands(expression.operator, lv, rv)

                return float(lv) <= float(rv)

            case Expr.Binary(Token(Token.Type.EQUAL_EQUAL), left, right):
                return self.is_equal(self.evaluate(left), self.evaluate(right))

            case Expr.Binary(Token(Token.Type.BANG_EQUAL), left, right):
                return not self.is_equal(self.evaluate(left), self.evaluate(right))

            case Expr.Grouping(expr):
                return self.evaluate(expr)

            case Expr.Variable(name):
                return self.environment.get(name)

            case Expr.Assignment(name, value):
                val = self.evaluate(value)
                self.environment.assign(name, val)
                return val

            case Expr.Logical(Token(Token.Type.OR), left, right):
                lv = self.evaluate(left)
                if self.is_truthy(lv):
                    return lv
                return self.evaluate(right)

            case Expr.Logical(Token(Token.Type.AND), left, right):
                lv = self.evaluate(left)
                if not self.is_truthy(lv):
                    return lv
                return self.evaluate(right)

            case Expr.Call(callee, paren, args):
                cv = self.evaluate(callee)
                argv = [self.evaluate(arg) for arg in args]

                if not isinstance(cv, LoxCallable):
                    raise InterpreterError(paren, "Can only call functions and classes")

                if len(argv) != cv.arity():
                    raise InterpreterError(
                        paren,
                        f"Expected {cv.arity()} arguments but got {len(argv)}",
                    )
                return cv.call(self, argv)

            case Expr.Get(target, name):
                obj = self.evaluate(target)

                if isinstance(obj, LoxInstance):
                    return obj.get(name)
                raise LoxRuntimeError(name, "Only instances have properties")

            case Expr.Set(target, name, value):
                obj = self.evaluate(target)

                if isinstance(obj, LoxInstance):
                    v = self.evaluate(value)
                    obj.set(name, v)
                    return v
                raise LoxRuntimeError(name, "Only instances have fields")

            case Expr.This(keyword):
                return self.environment.get(keyword)

            case Expr.Super(keyword, method):
                superclass = self.environment.get(keyword)
                assert isinstance(superclass, LoxClass)

                obj = self.environment.get(Token.THIS())
                assert isinstance(obj, LoxInstance)

                resolved_method = superclass.find_method(method.lexeme)
                if not resolved_method:
                    raise InterpreterError(
                        method, f"Undefined property '{method.lexeme}'"
                    )

                return resolved_method.bind(obj)

            case _:
                raise NotImplementedError

    # Executing Statements
    def execute(self, statement: Stmt.Statement):
        match statement:
            case Stmt.Print(expr):
                print(self.stringify(self.evaluate(expr)))

            case Stmt.Expression(expr):
                self.evaluate(expr)

            case Stmt.Function(name, _, _):
                # In the global scope, function declarations are
                # different, they're visible to the whole scope. This
                # enables mutual recursion, but only in the global
                # scope.
                env = self.globals
                if self.environment.enclosing:
                    self.environment = self.environment.split()
                    env = self.environment

                env.define(name)
                function = LoxFunction(statement, self.environment)
                env.assign(name, function)

            case Stmt.Class(name, _, _):
                superclass = None
                if statement.superclass:
                    superclass = self.evaluate(statement.superclass)
                    if not isinstance(superclass, LoxClass):
                        raise InterpreterError(
                            statement.superclass.name, "Superclass must be a class"
                        )

                self.environment.define(name)

                if superclass:
                    self.environment = self.environment.push()
                    self.environment.define(Token.SUPER(name.line), superclass)

                methods: dict[str, LoxFunction] = {}
                for method in statement.methods:
                    methods[method.name.lexeme] = LoxFunction(
                        method, self.environment, method.name.lexeme == "init"
                    )

                klass = LoxClass(statement.name, superclass, methods)

                if superclass:
                    self.environment = self.environment.pop()

                self.environment.assign(name, klass)

            case Stmt.Var(name, initializer):
                value = None
                if initializer is not None:
                    value = self.evaluate(initializer)

                self.environment = Environment(self.environment)
                self.environment.define(name, value)

            case Stmt.Block(stmts):
                self.execute_block(stmts, self.environment.push())

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
                raise NotImplementedError

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
