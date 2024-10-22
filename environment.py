# environment


import logging

from errors import LoxError
from tokens import Token


class Environment:
    def __init__(self, enclosing: "Environment|None" = None):
        self.values = {}
        self.enclosing = enclosing
        self.logger = logging.getLogger("Lox.Environment")

    def define(self, name: str, value: object):
        self.values[name] = value

    def get(self, name: Token):
        if name.lexeme in self.values:
            return self.values[name.lexeme]

        if self.enclosing is not None:
            return self.enclosing.get(name)

        raise LoxError(f"Undefined variable '{name.lexeme}'")

    def assign(self, name: Token, value: object):
        if name.lexeme in self.values:
            self.values[name.lexeme] = value
            return

        if self.enclosing is not None:
            return self.enclosing.assign(name, value)

        raise LoxError(f"Undefined variable '{name.lexeme}'")
