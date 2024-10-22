# parser.py

import logging

import expression as Expr
import statement as Stmt
from loxerrors import LoxError
from .tokens import Token


class ParseError(LoxError):
    def __init__(self, token, message):
        super().__init__(message)
        self.message = message
        self.token = token

    def __str__(self):
        if self.token.type == Token.Type.EOF:
            return f"line {self.token.line + 1}, at EOL. {self.message}"
        return f"line {self.token.line + 1}, at '{self.token.lexeme}'. {self.message}"


class Parser:
    """Parse a list of AST Tokens and returns a corresponding
    Expression"""

    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.current = 0
        self.logger = logging.getLogger("Lox.Parser")

    # Public functions
    def parse(self):
        try:
            return self.statements()
        except ParseError as e:
            self.logger.error(e)
            raise e

    def statements(self) -> list[Stmt.Statement]:
        statements = []
        while not self.is_at_end():
            statements.append(self.declaration())

        return statements

    def expression(self) -> Expr.Expression:
        return self.assignment()

    # Private Functions
    # Look for specific token types
    def match(self, token: Token.Type) -> bool:
        if self.peek().type == token:
            self.advance()
            return True

        return False

    def match_any(self, tokens: list[Token.Type]):
        if self.peek().type in tokens:
            self.advance()
            return True

        return False

    def expect(self, token: Token.Type, message: str):
        if self.peek().type == token:
            self.advance()
            return

        raise ParseError(self.peek(), message)

    # Move within and inspect the list of tokens
    def advance(self):
        if not self.is_at_end():
            self.current += 1

    def previous(self) -> Token:
        return self.tokens[self.current - 1]

    def peek(self) -> Token:
        return self.tokens[self.current]

    def is_at_end(self) -> bool:
        return self.peek().type == Token.Type.EOF

    # Parse Expressions
    def assignment(self) -> Expr.Expression:
        expr = self.equality()

        if self.match(Token.Type.EQUAL):
            equal = self.previous()
            value = self.assignment()

            if isinstance(expr, Expr.Variable):
                return Expr.Assignment(expr.name, value)

            raise ParseError(equal, "Invalid assigment target")

        return expr

    def equality(self) -> Expr.Expression:
        lhs = self.comparison()

        while self.match_any([Token.Type.BANG_EQUAL, Token.Type.EQUAL_EQUAL]):
            op = self.previous()
            rhs = self.comparison()
            lhs = Expr.Binary(op, lhs, rhs)

        return lhs

    def comparison(self) -> Expr.Expression:
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
            lhs = Expr.Binary(op, lhs, rhs)

        return lhs

    def term(self) -> Expr.Expression:
        lhs = self.factor()

        while self.match_any([Token.Type.MINUS, Token.Type.PLUS]):
            op = self.previous()
            rhs = self.factor()
            lhs = Expr.Binary(op, lhs, rhs)

        return lhs

    def factor(self) -> Expr.Expression:
        lhs = self.unary()

        while self.match_any([Token.Type.STAR, Token.Type.SLASH]):
            op = self.previous()
            rhs = self.unary()
            lhs = Expr.Binary(op, lhs, rhs)

        return lhs

    def unary(self) -> Expr.Expression:
        if self.match_any([Token.Type.BANG, Token.Type.MINUS]):
            op = self.previous()
            rhs = self.unary()

            return Expr.Unary(op, rhs)

        return self.primary()

    def primary(self) -> Expr.Expression:
        if self.match(Token.Type.FALSE):
            return Expr.Literal(False)

        if self.match(Token.Type.TRUE):
            return Expr.Literal(True)

        if self.match(Token.Type.NIL):
            return Expr.Literal(None)

        if self.match_any([Token.Type.NUMBER, Token.Type.STRING]):
            return Expr.Literal(self.previous().literal)

        if self.match(Token.Type.LEFT_PAREN):
            expr = self.expression()
            self.expect(Token.Type.RIGHT_PAREN, "Expect ')' after expression")
            return Expr.Grouping(expr)

        if self.match(Token.Type.IDENTIFIER):
            return Expr.Variable(self.previous())

        raise ParseError(self.peek(), "Expect expression")

    # Parse Statements
    def declaration(self) -> Stmt.Statement:
        if self.match(Token.Type.VAR):
            return self.var_decl()
        return self.statement()

    def statement(self) -> Stmt.Statement:
        if self.match(Token.Type.PRINT):
            return self.print_stmt()

        if self.match(Token.Type.LEFT_BRACE):
            return self.block_stmt()

        return self.expression_stmt()

    def block_stmt(self) -> Stmt.Block:
        stmts = []

        while not self.peek().type == Token.Type.RIGHT_BRACE and not self.is_at_end():
            stmts.append(self.declaration())

        self.expect(Token.Type.RIGHT_BRACE, "Expect '}' after block")
        return Stmt.Block(stmts)

    def print_stmt(self) -> Stmt.Print:
        expr = self.expression()
        self.expect(Token.Type.SEMICOLON, "Expect ';' after value")
        return Stmt.Print(expr)

    def expression_stmt(self) -> Stmt.Expression:
        expr = self.expression()
        self.expect(Token.Type.SEMICOLON, "Expect ';' after expression")
        return Stmt.Expression(expr)

    def var_decl(self) -> Stmt.Var:
        self.expect(Token.Type.IDENTIFIER, "Expect variable name")
        name = self.previous()

        initializer = None
        if self.match(Token.Type.EQUAL):
            initializer = self.expression()

        self.expect(Token.Type.SEMICOLON, "Expect ';' after variable declaration")
        return Stmt.Var(name, initializer)
