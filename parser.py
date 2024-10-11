# parser.py

from tokens import Token
from expression import *


class Parser:
    """Parse a list of AST Tokens and returns a corresponding
    Expression"""

    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.current = 0

    def parse(self) -> Expression:
        return self.expression()

    # Look for specific token types
    def match(self, token: Token.Type) -> bool:
        if self.tokens[self.current].type == token:
            self.advance()
            return True

        return False

    def match_any(self, tokens: list[Token.Type]):
        if self.tokens[self.current].type in tokens:
            self.advance()
            return True

        return False

    def expect(self, token: Token.Type):
        if self.tokens[self.current].type == token:
            self.advance()
            return

        raise SyntaxError

    # Move within and inspect the list of tokens
    def advance(self):
        if not self.is_at_end():
            self.current += 1

    def previous(self) -> Token:
        return self.tokens[self.current - 1]

    def peek(self) -> Token:
        return self.tokens[self.current]

    def is_at_end(self) -> bool:
        return self.tokens[self.current] == Token.Type.EOF

    # Parse Expressions
    def expression(self) -> Expression:
        return self.equality()

    def equality(self) -> Expression:
        lhs = self.comparison()

        while self.match_any([Token.Type.BANG_EQUAL, Token.Type.EQUAL_EQUAL]):
            op = self.previous()
            rhs = self.comparison()
            lhs = Binary(lhs, op, rhs)

        return lhs

    def comparison(self) -> Expression:
        lhs = self.term()

        while self.match_any(
            [
                Token.Type.GREATER,
                Token.Type.GREATER_EQUAL,
                Token.Type.LESS,
                Token.Type.LESS_EQUAL,
            ]
        ):
            op = self.previous()
            rhs = self.term()
            lhs = Binary(lhs, op, rhs)

        return lhs

    def term(self) -> Expression:
        lhs = self.factor()

        while self.match_any([Token.Type.MINUS, Token.Type.PLUS]):
            op = self.previous()
            rhs = self.factor()
            lhs = Binary(lhs, op, rhs)

        return lhs

    def factor(self) -> Expression:
        lhs = self.unary()

        while self.match_any([Token.Type.STAR, Token.Type.SLASH]):
            op = self.previous()
            rhs = self.unary()
            lhs = Binary(lhs, op, rhs)

        return lhs

    def unary(self) -> Expression:
        if self.match_any([Token.Type.BANG, Token.Type.MINUS]):
            op = self.previous()
            rhs = self.unary()

            return Unary(op, rhs)

        return self.primary()

    def primary(self) -> Expression:
        if self.match(Token.Type.FALSE):
            return Literal(False)

        if self.match(Token.Type.TRUE):
            return Literal(True)

        if self.match(Token.Type.NIL):
            return Literal(None)

        if self.match_any([Token.Type.NUMBER, Token.Type.STRING]):
            return Literal(self.previous().literal)

        if self.match(Token.Type.LEFT_PAREN):
            expr = self.expression()
            self.expect(Token.Type.RIGHT_PAREN)

            return Grouping(expr)

        raise SyntaxError
