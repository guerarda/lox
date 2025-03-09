# environment

import logging

from errors import LoxRuntimeError
from tokens import Token


class Environment:
    def __init__(self, other: "Environment|None" = None):
        self.values: dict[str, object] = {}
        self.sibling = other
        self.enclosing = other.enclosing if other else None

        self.logger = logging.getLogger("Lox.Environment")

    def __contains__(self, item: str):
        if item in self.values:
            return True

        if self.sibling is not None:
            return item in self.sibling

        if self.enclosing is not None:
            return item in self.enclosing

        return False

    def __str__(self):
        s = str(self.values)
        if self.sibling:
            s += f"\n -> {self.sibling}"

        elif self.enclosing:
            s += f"\n ->> {self.sibling}"

        return s

    def define(self, name: Token, value: object = None):
        self.values[name.lexeme] = value

    def define_multiple(self, names: list[Token], values: list[object]):
        for name, value in zip(names, values):
            self.values[name.lexeme] = value

    def assign(self, name: Token, value: object):
        if name.lexeme in self.values:
            self.values[name.lexeme] = value

        elif self.sibling:
            self.sibling.assign(name, value)

        elif self.enclosing:
            self.enclosing.assign(name, value)

        else:
            raise LoxRuntimeError(name, f"Undefined variable '{name.lexeme}'")

    def get(self, name: Token) -> object:
        if name.lexeme in self.values:
            return self.values[name.lexeme]

        if self.sibling is not None:
            return self.sibling.get(name)

        if self.enclosing is not None:
            return self.enclosing.get(name)

        raise LoxRuntimeError(name, f"Undefined variable '{name.lexeme}'")

    def push(self) -> "Environment":
        env = Environment()
        env.enclosing = self
        return env

    def split(self) -> "Environment":
        return Environment(self)

    def pop(self) -> "Environment":
        assert self.enclosing
        return self.enclosing
