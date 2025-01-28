# loxclass

from loxcallable import LoxCallable
from loxinstance import LoxInstance
from tokens import Token


class LoxClass(LoxCallable):
    def __init__(self, name: Token):
        self.name = name

    def __str__(self):
        return f"{self.name.lexeme}"

    def arity(self):
        return 0

    def call(self, interpreter, args):
        return LoxInstance(self)
