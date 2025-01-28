# loxinstance

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from loxclass import LoxClass


class LoxInstance:
    def __init__(self, klass: "LoxClass"):
        self.klass = klass

    def __str__(self):
        return f"{str(self.klass)} instance"
