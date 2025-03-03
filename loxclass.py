# loxclass

from loxcallable import LoxCallable
from loxfunction import LoxFunction
from loxinstance import LoxInstance
from tokens import Token


class LoxClass(LoxCallable):
    def __init__(self, name: Token, methods: dict[str, LoxFunction]):
        self.name = name
        self.methods = methods

    def __str__(self):
        return f"{self.name.lexeme}"

    def arity(self):
        if "init" in self.methods and (init := self.methods["init"]):
            return init.arity()
        return 0

    def call(self, interpreter, args):
        instance = LoxInstance(self)
        if "init" in self.methods and (init := self.methods["init"]):
            init.bind(instance).call(interpreter, args)

        return instance
