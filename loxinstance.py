# loxinstance

from typing import TYPE_CHECKING

from errors import LoxRuntimeError
from tokens import Token

if TYPE_CHECKING:
    from loxclass import LoxClass


class LoxInstance:
    def __init__(self, klass: "LoxClass"):
        self.klass = klass
        self.fields: dict[str, object] = {}

    def __str__(self):
        return f"{str(self.klass)} instance"

    def get(self, name: Token) -> object:
        if name.lexeme in self.fields:
            return self.fields[name.lexeme]

        raise LoxRuntimeError(name, f"Undefined property '{name.lexeme}'.")
