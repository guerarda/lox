import unittest

from astprinter import ASTPrinter
from context import Context
from interpreter import Interpreter, InterpreterError
from parser import Parser
from scanner import Scanner
from tokens import Token
import expression as Expr


class TestScanner(unittest.TestCase):
    def test_operators(self):
        tokens = Scanner(Context("- + == != =")).scan_tokens()

        self.assertEqual(len(tokens), 6)
        self.assertEqual(tokens[0].type, Token.Type.MINUS)
        self.assertEqual(tokens[1].type, Token.Type.PLUS)
        self.assertEqual(tokens[2].type, Token.Type.EQUAL_EQUAL)
        self.assertEqual(tokens[3].type, Token.Type.BANG_EQUAL)
        self.assertEqual(tokens[4].type, Token.Type.EQUAL)
        self.assertEqual(tokens[5].type, Token.Type.EOF)

    def test_string(self):
        src = "this is a string"
        tokens = Scanner(Context(f'"{src}"')).scan_tokens()

        self.assertEqual(len(tokens), 2)
        self.assertEqual(tokens[0].type, Token.Type.STRING)
        self.assertEqual(tokens[0].literal, src)
        self.assertEqual(tokens[1].type, Token.Type.EOF)

    def test_number(self):
        nums = [123, 123.456, 1321453563453543, 1.4832749832]
        src = " ".join(str(n) for n in nums)
        tokens = Scanner(Context(src)).scan_tokens()

        self.assertEqual(len(tokens), len(nums) + 1)
        self.assertEqual(tokens[-1].type, Token.Type.EOF)

        for tok, num in zip(tokens[:-1], nums):
            self.assertEqual(tok.literal, num)

    def test_identifer(self):
        src = "var" " variable" " my_function" " _my_var" " my1337"
        tokens = Scanner(Context(src)).scan_tokens()

        self.assertEqual(len(tokens), 6)
        self.assertEqual(tokens[-1].type, Token.Type.EOF)

        self.assertEqual(tokens[0].type, Token.Type.VAR)
        for token in tokens[1:-1]:
            self.assertEqual(token.type, Token.Type.IDENTIFIER)


class TestASTPrinter(unittest.TestCase):
    def test_print(self):
        t_min = Token(Token.Type.MINUS, "-", None, 1)
        t_star = Token(Token.Type.STAR, "*", None, 1)

        e_123 = Expr.Literal(123.0)
        e_456 = Expr.Literal(45.6)

        e_min123 = Expr.Unary(t_min, e_123)
        e_grp = Expr.Grouping(e_456)

        e_mult = Expr.Binary(t_star, e_min123, e_grp)

        print(ASTPrinter().print(e_mult))


class TestParser(unittest.TestCase):
    def test_expression(self):
        tokens = [
            Token(Token.Type.NUMBER, "123", 123, 1),
            Token(Token.Type.PLUS, "+", None, 1),
            Token(Token.Type.NUMBER, "456", 456, 1),
            Token(Token.Type.EOF, "", None, 1),
        ]

        print(Parser(tokens).expression())

    def test_scan_parse(self):
        test_str = "(123 == (100 + 23)) != false"
        s = Scanner(Context(test_str))
        s.scan_tokens()

        print(ASTPrinter().print(Parser(s.tokens).parse()))


class TestInterpreter(unittest.TestCase):
    def test_unary(self):
        self.assertEqual(
            Interpreter().evaluate(
                Expr.Unary(Token(Token.Type.BANG, "!", None, 0), Expr.Literal(True))
            ),
            False,
        )

        self.assertEqual(
            Interpreter().evaluate(
                Expr.Unary(Token(Token.Type.MINUS, "-", None, 0), Expr.Literal(2.0))
            ),
            -2.0,
        )

        with self.assertRaises(InterpreterError):
            Interpreter().evaluate(
                Expr.Unary(Token(Token.Type.PLUS, "+", None, 0), Expr.Literal(2.0))
            )

        with self.assertRaises(InterpreterError):
            Interpreter().evaluate(
                Expr.Unary(Token(Token.Type.PLUS, "-", None, 0), Expr.Literal("foo"))
            )

        with self.assertRaises(InterpreterError):
            Interpreter().evaluate(
                Expr.Unary(Token(Token.Type.PLUS, "*", None, 0), Expr.Literal(False))
            )

    def test_binary(self):
        self.assertEqual(
            Interpreter().evaluate(
                Expr.Binary(
                    Token(Token.Type.PLUS, "+", None, 0),
                    Expr.Literal(2.0),
                    Expr.Literal(3.0),
                )
            ),
            5.0,
        )

        self.assertTrue(
            Interpreter().evaluate(
                Expr.Binary(Token.GREATER(), Expr.Literal(4.0), Expr.Literal(3.0))
            )
        )
        self.assertTrue(
            Interpreter().evaluate(
                Expr.Binary(Token.GREATER_EQUAL(), Expr.Literal(4.0), Expr.Literal(4.0))
            )
        )
        with self.assertRaises(InterpreterError):
            Interpreter().evaluate(
                Expr.Binary(Token.SLASH(), Expr.Literal(2.0), Expr.Literal(0.0))
            )


if __name__ == "__main__":
    unittest.main()
