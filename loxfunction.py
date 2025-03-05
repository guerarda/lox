# loxfunction

from typing import TYPE_CHECKING

import statement as Stmt
from environment import Environment
from loxcallable import LoxCallable, Return
from loxinstance import LoxInstance
from tokens import Token

if TYPE_CHECKING:
    from interpreter import Interpreter


class LoxFunction(LoxCallable):
    def __init__(
        self,
        declaration: Stmt.Function,
        closure: Environment,
        is_initializer: bool = False,
    ):
        self.declaration = declaration
        self.closure = closure
        self.is_initializer = is_initializer

    def __str__(self):
        return f"<fn {self.declaration.name.lexeme}>"

    def arity(self) -> int:
        return len(self.declaration.params)

    def call(self, interpreter: "Interpreter", args: list[object]):
        env = Environment(self.closure).define_multiple(self.declaration.params, args)

        try:
            interpreter.execute_block(self.declaration.body, env)
        except Return as e:
            if self.is_initializer:
                return env.get(Token.THIS())
            return e.value

        if self.is_initializer:
            return env.get(Token.THIS())

    def bind(self, instance: LoxInstance) -> "LoxFunction":
        env = Environment(self.closure)
        env.define(Token.THIS(), instance)

        return LoxFunction(self.declaration, env, self.is_initializer)
