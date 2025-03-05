# tokens.py

from dataclasses import dataclass
from enum import Enum, auto


@dataclass
class Token:
    class Type(Enum):
        # Single-character tokens
        LEFT_PAREN = (auto(),)
        RIGHT_PAREN = (auto(),)
        LEFT_BRACE = (auto(),)
        RIGHT_BRACE = (auto(),)
        COMMA = (auto(),)
        DOT = (auto(),)
        MINUS = (auto(),)
        PLUS = (auto(),)
        SEMICOLON = (auto(),)
        SLASH = (auto(),)
        STAR = (auto(),)

        # One or two characters tokens
        BANG = (auto(),)
        BANG_EQUAL = (auto(),)
        EQUAL = (auto(),)
        EQUAL_EQUAL = (auto(),)

        GREATER = (auto(),)
        GREATER_EQUAL = (auto(),)
        LESS = (auto(),)
        LESS_EQUAL = (auto(),)

        # Literals
        IDENTIFIER = (auto(),)
        STRING = (auto(),)
        NUMBER = (auto(),)

        # Keywords
        AND = (auto(),)
        CLASS = (auto(),)
        ELSE = (auto(),)
        FALSE = (auto(),)
        FUN = (auto(),)
        FOR = (auto(),)
        IF = (auto(),)
        NIL = (auto(),)
        OR = (auto(),)
        PRINT = (auto(),)
        RETURN = (auto(),)
        SUPER = (auto(),)
        THIS = (auto(),)
        TRUE = (auto(),)
        VAR = (auto(),)
        WHILE = (auto(),)

        EOF = auto()

    type: Type
    lexeme: str = ""
    literal: object = None
    line: int = 0

    def __str__(self):
        if self.literal:
            return f"'{self.lexeme}' {self.type} | {self.literal}"
        else:
            return f"'{self.lexeme}' {self.type}"

    # Utils for quickly creating Tokens
    @classmethod
    def THIS(cls, line: int = 0):
        return Token(Token.Type.THIS, "this", None, line)

    @classmethod
    def SUPER(cls, line: int = 0):
        return Token(Token.Type.SUPER, "super", None, line)

    @classmethod
    def IDENTIFIER(cls, name: str, line: int = 0):
        return Token(Token.Type.IDENTIFIER, name, line)
