# tokens.py

from enum import auto, Enum

from dataclasses import dataclass


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


    # Utils for quickly creating Tokens, mostly for tests
    @classmethod
    def MINUS(cls):
        return Token(Token.Type.MINUS, "-", None, 0)

    @classmethod
    def SLASH(cls):
        return Token(Token.Type.SLASH, "/", None, 0)

    @classmethod
    def GREATER(cls):
        return Token(Token.Type.GREATER, ">", None, 0)

    @classmethod
    def GREATER_EQUAL(cls):
        return Token(Token.Type.GREATER_EQUAL, ">=", None, 0)
