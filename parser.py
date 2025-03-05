# parser.py

import logging

import expression as Expr
import statement as Stmt
from errors import LoxError
from tokens import Token


class ParseError(LoxError):
    def __init__(self, token: Token, message: str):
        super().__init__(message)
        self.message = message
        self.token = token

    def __str__(self):
        if self.token.type == Token.Type.EOF:
            return f"Error at EOL. {self.message}"
        return (
            f"{self.token.line + 1} | Error at '{self.token.lexeme}': {self.message}."
        )


class Parser:
    """Parse a list of AST Tokens and returns a corresponding
    list of Statements"""

    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.current = 0
        self.has_error = False
        self.logger = logging.getLogger("Lox.Parser")

    # Public functions
    def parse(self):
        return self.statements()

    def statements(self) -> list[Stmt.Statement]:
        statements = []
        while not self.is_at_end():
            statements.append(self.declaration())

        return statements

    def expression(self) -> Expr.Expression:
        return self.assignment()

    # Private Functions
    def synchronize(self):
        self.advance()

        while not self.is_at_end():
            if self.previous().type == Token.Type.SEMICOLON:
                return

            if self.peek().type in [
                Token.Type.CLASS,
                Token.Type.FOR,
                Token.Type.FUN,
                Token.Type.IF,
                Token.Type.PRINT,
                Token.Type.RETURN,
                Token.Type.VAR,
                Token.Type.WHILE,
            ]:
                return
            self.advance()

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
            return self.previous()

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
        expr = self.logic_or()

        if self.match(Token.Type.EQUAL):
            equal = self.previous()
            value = self.assignment()

            if isinstance(expr, Expr.Variable):
                return Expr.Assignment(expr.name, value)

            elif isinstance(expr, Expr.Get):
                return Expr.Set(expr.target, expr.name, value)

            raise ParseError(equal, "Invalid assignment target")

        return expr

    def logic_or(self) -> Expr.Expression:
        lhs = self.logic_and()

        while self.match(Token.Type.OR):
            op = self.previous()
            rhs = self.logic_and()
            lhs = Expr.Logical(op, lhs, rhs)

        return lhs

    def logic_and(self) -> Expr.Expression:
        lhs = self.equality()

        while self.match(Token.Type.AND):
            op = self.previous()
            rhs = self.equality()
            lhs = Expr.Logical(op, lhs, rhs)

        return lhs

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

        return self.call()

    def call(self) -> Expr.Expression:
        expr = self.primary()

        while True:
            if self.match(Token.Type.LEFT_PAREN):
                expr = self.read_call(expr)

            elif self.match(Token.Type.DOT):
                name = self.expect(
                    Token.Type.IDENTIFIER, "Expect property name after '.'."
                )
                expr = Expr.Get(expr, name)

            else:
                break
        return expr

    def read_call(self, callee: Expr.Expression) -> Expr.Call:
        args = []
        if not self.peek().type == Token.Type.RIGHT_PAREN:
            while True:
                if len(args) > 254:
                    raise ParseError(self.peek(), "Can't have more than 255 arguments")

                args.append(self.expression())
                if not self.match(Token.Type.COMMA):
                    break
        paren = self.expect(Token.Type.RIGHT_PAREN, "Expect ')' after arguments")

        return Expr.Call(callee, paren, args)

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

        if self.match(Token.Type.THIS):
            return Expr.This(self.previous())

        if self.match(Token.Type.IDENTIFIER):
            return Expr.Variable(self.previous())

        if self.match(Token.Type.SUPER):
            keyword = self.previous()
            self.expect(Token.Type.DOT, "Expect '.' after 'super'")
            method = self.expect(Token.Type.IDENTIFIER, "Expect superclass method name")

            return Expr.Super(keyword, method)

        raise ParseError(self.peek(), "Expect expression")

    # Parse Statements
    def declaration(self) -> Stmt.Statement | None:
        try:
            if self.match(Token.Type.CLASS):
                return self.class_decl()
            if self.match(Token.Type.FUN):
                return self.fun_decl("function")
            if self.match(Token.Type.VAR):
                return self.var_decl()
            return self.statement()

        except ParseError as e:
            self.has_error = True
            self.logger.error(e)
            self.synchronize()

    def statement(self) -> Stmt.Statement:
        if self.match(Token.Type.FOR):
            return self.for_stmt()

        if self.match(Token.Type.IF):
            return self.if_stmt()

        if self.match(Token.Type.PRINT):
            return self.print_stmt()

        if self.match(Token.Type.WHILE):
            return self.while_stmt()

        if self.match(Token.Type.LEFT_BRACE):
            return Stmt.Block(self.block())

        if self.match(Token.Type.RETURN):
            return self.return_stmt()

        return self.expression_stmt()

    def class_decl(self):
        name = self.expect(Token.Type.IDENTIFIER, "Expect class name")

        superclass = None
        if self.peek().type == Token.Type.LESS:
            self.advance()
            self.expect(Token.Type.IDENTIFIER, "Expect superclass name")
            superclass = Expr.Variable(self.previous())

        self.expect(Token.Type.LEFT_BRACE, "Expect '{' before class body")

        methods = []
        while not self.peek().type == Token.Type.RIGHT_BRACE and not self.is_at_end():
            methods.append(self.fun_decl("method"))

        self.expect(Token.Type.RIGHT_BRACE, "Expect '}' after class body")

        return Stmt.Class(name, superclass, methods)

    def fun_decl(self, kind: str):
        name = self.expect(Token.Type.IDENTIFIER, f"Expect {kind} name")
        self.expect(Token.Type.LEFT_PAREN, "Expect '(' after function name")

        params = []
        if not self.peek().type == Token.Type.RIGHT_PAREN:
            while True:
                if len(params) > 254:
                    raise ParseError(self.peek(), "Can't have more than 255 parameters")
                params.append(
                    self.expect(Token.Type.IDENTIFIER, "Expect parameter name")
                )
                if not self.match(Token.Type.COMMA):
                    break
        self.expect(Token.Type.RIGHT_PAREN, "Expect ')' after arguments")
        self.expect(Token.Type.LEFT_BRACE, f"Expect '{{' before {kind} body")
        body = self.block()

        return Stmt.Function(name, params, body)

    def var_decl(self) -> Stmt.Var:
        name = self.expect(Token.Type.IDENTIFIER, "Expect variable name")

        initializer = None
        if self.match(Token.Type.EQUAL):
            initializer = self.expression()

        self.expect(Token.Type.SEMICOLON, "Expect ';' after variable declaration")
        return Stmt.Var(name, initializer)

    def for_stmt(self) -> Stmt.Statement:
        self.expect(Token.Type.LEFT_PAREN, "Expect '(' after for")

        initializer = None
        if self.match(Token.Type.SEMICOLON):
            pass
        elif self.match(Token.Type.VAR):
            initializer = self.var_decl()
        else:
            initializer = self.expression_stmt()
        # Statement eats the next ';'

        cond = None
        if not self.peek().type == Token.Type.SEMICOLON:
            cond = self.expression()
        self.expect(Token.Type.SEMICOLON, "Expect ';' after condition")

        inc = None
        if not self.peek().type == Token.Type.RIGHT_PAREN:
            inc = self.expression()
        self.expect(Token.Type.RIGHT_PAREN, "Expect ')' after for clauses")

        # Build the while-loop
        loop = Stmt.While(
            cond if cond is not None else Expr.Literal(True),
            (
                self.statement()
                if inc is None
                else Stmt.Block([self.statement(), Stmt.Expression(inc)])
            ),
        )

        if initializer is None:
            return loop

        return Stmt.Block([initializer, loop])

    def if_stmt(self) -> Stmt.If:
        self.expect(Token.Type.LEFT_PAREN, "Expect '(' after if")
        condition = self.expression()
        self.expect(Token.Type.RIGHT_PAREN, "Expect ')' after condition")

        consequence = self.statement()
        alternative = None
        if self.match(Token.Type.ELSE):
            alternative = self.statement()

        return Stmt.If(condition, consequence, alternative)

    def print_stmt(self) -> Stmt.Print:
        expr = self.expression()
        self.expect(Token.Type.SEMICOLON, "Expect ';' after value")
        return Stmt.Print(expr)

    def while_stmt(self) -> Stmt.While:
        self.expect(Token.Type.LEFT_PAREN, "Expect '(' after while")
        cond = self.expression()
        self.expect(Token.Type.RIGHT_PAREN, "Expect ')' after condition")

        body = self.declaration()
        assert body is not None

        return Stmt.While(cond, body)

    def block(self) -> list[Stmt.Statement]:
        stmts = []

        while not self.peek().type == Token.Type.RIGHT_BRACE and not self.is_at_end():
            stmts.append(self.declaration())

        self.expect(Token.Type.RIGHT_BRACE, "Expect '}' after block")

        return stmts

    def expression_stmt(self) -> Stmt.Expression:
        expr = self.expression()
        self.expect(Token.Type.SEMICOLON, "Expect ';' after expression")
        return Stmt.Expression(expr)

    def return_stmt(self) -> Stmt.Return:
        token = self.previous()
        value = None

        if self.peek().type != Token.Type.SEMICOLON:
            value = self.expression()

        self.expect(Token.Type.SEMICOLON, "Expect ';' after return value")

        return Stmt.Return(token, value)
