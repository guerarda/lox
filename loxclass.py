# loxclass

from loxcallable import LoxCallable
from loxfunction import LoxFunction
from loxinstance import LoxInstance
from tokens import Token


class LoxClass(LoxCallable):
    def __init__(
        self,
        name: Token,
        superclass: "LoxClass | None",
        methods: dict[str, LoxFunction],
    ):
        self.name = name
        self.superclass = superclass
        self.methods = methods

    def __str__(self):
        return f"{self.name.lexeme}"

    def arity(self):
        initializer = self.find_method("init")
        if initializer:
            return initializer.arity()
        return 0

    def call(self, interpreter, args):
        instance = LoxInstance(self)

        initializer = self.find_method("init")
        if initializer:
            initializer.bind(instance).call(interpreter, args)
        return instance

    def find_method(self, name: str) -> LoxFunction | None:
        if name in self.methods:
            return self.methods[name]

        if self.superclass:
            return self.superclass.find_method(name)

        return None
