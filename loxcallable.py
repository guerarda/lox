# loxcallable

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from interpreter import Interpreter


class Return(Exception):
    def __init__(self, value: object):
        self.value = value


class LoxCallable:
    def arity(self) -> int:
        raise NotImplementedError

    def call(self, interpreter: "Interpreter", args: list[object]):
        raise NotImplementedError
