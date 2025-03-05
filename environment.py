# environment

import logging

from errors import LoxRuntimeError
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

    def __str__(self):
        res = str(self.values)
        if self.enclosing:
            res += " -> " + str(self.enclosing)
        return res

    def define(self, name: Token, value: object) -> "Environment":
        self.values[name.lexeme] = value
        return self

    def define_multiple(
        self, names: list[Token], values: list[object]
    ) -> "Environment":
        for name, value in zip(names, values):
            self.values[name.lexeme] = value
        return self

    def assign(self, name: Token, value: object):
        if name.lexeme in self.values:
            self.values[name.lexeme] = value
            return self

        if self.enclosing:
            self.enclosing.assign(name, value)
            return self

        raise LoxRuntimeError(name, f"Undefined variable '{name.lexeme}'")

    def get(self, name: Token) -> object:
        if name.lexeme in self.values:
            return self.values[name.lexeme]

        if self.enclosing is not None:
            return self.enclosing.get(name)

        raise LoxRuntimeError(name, f"Undefined variable '{name.lexeme}'")
