# loxfunction

from typing import TYPE_CHECKING

import statement as Stmt
from environment import Environment
from loxcallable import LoxCallable, Return

if TYPE_CHECKING:
    from interpreter import Interpreter


class LoxFunction(LoxCallable):
    def __init__(self, declaration: Stmt.Function, closure: Environment):
        self.declaration = declaration
        self.closure = closure

    def __str__(self):
        return f"<fn {self.declaration.name.lexeme}>"

    def arity(self) -> int:
        return len(self.declaration.params)

    def call(self, interpreter: "Interpreter", args: list[object]):
        env = Environment(self.closure).define_multiple(self.declaration.params, args)

        try:
            interpreter.execute_block(self.declaration.body, env)
        except Return as e:
            return e.value
