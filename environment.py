# environment

import logging

from errors import LoxError
from tokens import Token


class Environment:
    def __init__(self, enclosing: "Environment|None" = None):
        self.values: dict[str, object] = {}
        self.enclosing = enclosing
        self.logger = logging.getLogger("Lox.Environment")

    def __contains__(self, item: str):
        if item in self.values:
            return True

        if self.enclosing is not None:
            return item in self.enclosing

        return False

    def copy(self) -> "Environment":
        env = Environment()
        env.values = self.values.copy()
        env.enclosing = self.enclosing
        return env

    def define(self, name: Token, value: object) -> "Environment":
        if name.lexeme in self.values:
            self.logger.error(
                f"Line {name.line}, Already a variable with the name '{name.lexeme}' in scope."
            )

        env = self.copy()
        env.values[name.lexeme] = value
        return env

    def define_multiple(
        self, names: list[Token], values: list[object]
    ) -> "Environment":
        env = self.copy()

        for name, value in zip(names, values):
            if name.lexeme in self.values:
                self.logger.error(
                    f"Line {name.line}, Already a variable with the name '{name.lexeme}' in scope."
                )

            env.values[name.lexeme] = value
        return env

    def assign(self, name: Token, value: object):
        if name.lexeme in self.values:
            env = self.copy()
            env.values[name.lexeme] = value
            return env

        if self.enclosing is not None:
            self.overwrite(name, value)
            return self

        raise LoxError(f"Undefined variable '{name.lexeme}'")

    def overwrite(self, name: Token, value: object):
        if name.lexeme in self.values:
            self.values[name.lexeme] = value
            return self

        if self.enclosing is not None:
            return self.enclosing.overwrite(name, value)

    def get(self, name: Token) -> object:
        if name.lexeme in self.values:
            return self.values[name.lexeme]

        if self.enclosing is not None:
            return self.enclosing.get(name)

        raise LoxError(f"Undefined variable '{name.lexeme}'")
