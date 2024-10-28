# loxfunction

from typing import TYPE_CHECKING

import statement as Stmt
from environment import Environment
from loxcallable import LoxCallable

if TYPE_CHECKING:
    from interpreter import Interpreter


class LoxFunction(LoxCallable):
    def __init__(self, declaration: Stmt.Function):
        self.declaration = declaration

    def __str__(self):
        return f"<fn {self.declaration.name.lexeme}>"

    def arity(self) -> int:
        return len(self.declaration.params)

    def call(self, interpreter: "Interpreter", args: list[object]):
        env = Environment(interpreter.environment)

        for value, decl in zip(args, self.declaration.params):
            env.define(decl.lexeme, value)

        interpreter.execute_block(self.declaration.body, env)
