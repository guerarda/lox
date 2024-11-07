# environment


import logging

from errors import LoxError
from tokens import Token


class Environment:
    def __init__(self, enclosing: "Environment|None" = None):
        self.values: dict[str, object] = {}
        self.enclosing = enclosing
        self.logger = logging.getLogger("Lox.Environment")

    def ancestor(self, distance: int):
        env: Environment = self

        while distance > 0:
            assert env.enclosing is not None
            env = env.enclosing
            distance -= 1
        return env

    def define(self, name: str, value: object):
        self.values[name] = value

    def get(self, name: Token):
        if name.lexeme in self.values:
            return self.values[name.lexeme]

        if self.enclosing is not None:
            return self.enclosing.get(name)

        raise LoxError(f"Undefined variable '{name.lexeme}'")

    def get_at(self, name: Token, distance: int):
        return self.ancestor(distance).values.get(name.lexeme)

    def assign(self, name: Token, value: object):
        if name.lexeme in self.values:
            self.values[name.lexeme] = value
            return

        if self.enclosing is not None:
            return self.enclosing.assign(name, value)

        raise LoxError(f"Undefined variable '{name.lexeme}'")

    def assign_at(self, distance: int, name: Token, value: object):
        self.ancestor(distance).values[name.lexeme] = value
