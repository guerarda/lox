# scanner

import logging

from errors import LoxError
from tokens import Token


class ScannerError(LoxError):
    def __init__(self, line, char, message):
        super().__init__(message)
        self.message = message
        self.line = line
        self.char = char

    def __str__(self):
        return f"{self.line + 1} |  Error at '{self.char}', {self.message}."


class Scanner:
    keywords = {
        "and": Token.Type.AND,
        "class": Token.Type.CLASS,
        "else": Token.Type.ELSE,
        "false": Token.Type.FALSE,
        "for": Token.Type.FOR,
        "fun": Token.Type.FUN,
        "if": Token.Type.IF,
        "nil": Token.Type.NIL,
        "or": Token.Type.OR,
        "print": Token.Type.PRINT,
        "return": Token.Type.RETURN,
        "super": Token.Type.SUPER,
        "this": Token.Type.THIS,
        "true": Token.Type.TRUE,
        "var": Token.Type.VAR,
        "while": Token.Type.WHILE,
    }

    def __init__(self, source: str):
        self.source = source
        self.start = 0  # Index of the first char in the current lexeme.
        self.current = 0  # Index of the char being scanned.
        self.line = 0
        self.tokens = []
        self.logger = logging.getLogger("Lox.Scanner")

    def scan_tokens(self):
        try:
            while not self.is_at_end():
                self.start = self.current
                self.scan_token()

        except ScannerError as e:
            self.logger.error(e)
            raise e

        # End of file
        self.tokens.append(Token(Token.Type.EOF, "", None, self.line))

        return self.tokens

    def scan_token(self):
        c = self.advance()

        match c:
            # Single Character Lexemes
            case "(":
                self.add_token(Token.Type.LEFT_PAREN)

            case ")":
                self.add_token(Token.Type.RIGHT_PAREN)

            case "{":
                self.add_token(Token.Type.LEFT_BRACE)

            case "}":
                self.add_token(Token.Type.RIGHT_BRACE)

            case ",":
                self.add_token(Token.Type.COMMA)

            case ".":
                self.add_token(Token.Type.DOT)

            case "-":
                self.add_token(Token.Type.MINUS)

            case "+":
                self.add_token(Token.Type.PLUS)

            case ";":
                self.add_token(Token.Type.SEMICOLON)

            case "*":
                self.add_token(Token.Type.STAR)

            # Two-Character Lexemes
            case "!":
                if self.advance_if("="):
                    self.add_token(Token.Type.BANG_EQUAL)
                else:
                    self.add_token(Token.Type.BANG)

            case "=":
                if self.advance_if("="):
                    self.add_token(Token.Type.EQUAL_EQUAL)
                else:
                    self.add_token(Token.Type.EQUAL)

            case "<":
                if self.advance_if("="):
                    self.add_token(Token.Type.LESS_EQUAL)
                else:
                    self.add_token(Token.Type.LESS)

            case ">":
                if self.advance_if("="):
                    self.add_token(Token.Type.GREATER_EQUAL)
                else:
                    self.add_token(Token.Type.GREATER)

            case "/":
                if self.advance_if("/"):
                    while self.peek() != "\n" and not self.is_at_end():
                        self.advance()
                else:
                    self.add_token(Token.Type.SLASH)

            # Whitespaces
            case " " | "\r" | "\t":
                pass

            case '"':
                self.add_string()

            case "\n":
                self.line += 1

            case _ if c.isdecimal():
                self.add_number()

            case _ if c.isalpha() or c == "_":
                self.add_identifier()

            case _:
                raise ScannerError(self.line, c, "Unexpected character")

    def add_string(self):
        while self.peek() != '"' and not self.is_at_end():
            if self.peek() == "\n":
                self.line += 1

            self.advance()

        if self.is_at_end():
            raise ScannerError(self.line, "EOF", "Unterminated string")

        self.advance()  # Consume closing quote

        str = self.source[self.start + 1 : self.current - 1]
        self.add_token(Token.Type.STRING, str)

    def add_number(self):
        while self.peek().isdigit():
            self.advance()

        if self.peek() == "." and self.peek_next().isdigit():
            self.advance()  # Consume the .

            while self.peek().isdigit():
                self.advance()

        self.add_token(Token.Type.NUMBER, float(self.source[self.start : self.current]))

    def add_identifier(self):
        while self.peek().isalnum() or self.peek() == "_":
            self.advance()

        str = self.source[self.start : self.current]

        if str not in self.keywords:
            self.add_token(Token.Type.IDENTIFIER)
        else:
            self.add_token(self.keywords[str])

    def add_token(self, type: Token.Type, literal=None):
        lexeme = self.source[self.start : self.current]
        self.tokens.append(Token(type, lexeme, literal, self.line))

    def is_at_end(self) -> bool:
        return self.current >= len(self.source)

    def advance(self) -> str:
        c = self.source[self.current]
        self.current += 1

        return c

    def advance_if(self, expected: str):
        if self.is_at_end():
            return False

        c = self.source[self.current]

        if c != expected:
            return False

        self.current += 1

        return True

    def peek(self):
        return self.source[self.current] if not self.is_at_end() else ""

    def peek_next(self):
        return (
            self.source[self.current + 1] if self.current + 1 < len(self.source) else ""
        )
