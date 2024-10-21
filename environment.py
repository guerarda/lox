# environment


from loxerrors import LoxError
from tokens import Token


import logging


class Environment:
    def __init__(self):
        self.values = {}
        self.logger = logging.getLogger("Lox.Environment")

    def define(self, name: str, value: object):
        self.values[name] = value

    def get(self, name: Token):
        if name.lexeme in self.values:
            return self.values[name.lexeme]

        raise LoxError(f"Undefined variable '{name.lexeme}'")

    def assign(self, name: Token, value: object):
        if name.lexeme in self.values:
            self.values[name.lexeme] = value
            return

        raise LoxError(f"Undefined variable '{name.lexeme}'")
