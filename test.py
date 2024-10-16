import unittest

from astprinter import ASTPrinter
from context import Context
from interpreter import Interpreter, InterpreterError
from parser import ParseError
from scanner import Scanner
from tokens import Token
import expression as Expr
import lox as Lox

import sys
from contextlib import contextmanager
from io import StringIO


@contextmanager
def captured_output():
    new_out, new_err = StringIO(), StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout, sys.stderr = old_out, old_err


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

        ASTPrinter().print(e_mult)


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


class TestLox(unittest.TestCase):
    def test_parsing(self):
        with self.assertRaises(ParseError):
            Lox.test_run("1 ++ 2")

        with self.assertRaises(ParseError):
            Lox.test_run("(()")

    def test_expression(self):
        with captured_output() as (out, _):
            Lox.test_run("print 1==1;")
            self.assertRegex(out.getvalue(), "true")

        with captured_output() as (out, _):
            Lox.test_run("print 1 == 2;")
            self.assertRegex(out.getvalue(), "false")

        with captured_output() as (out, _):
            Lox.test_run("print 1 != 2;")
            self.assertRegex(out.getvalue(), "true")

        with captured_output() as (out, _):
            Lox.test_run("print 2.5 > 1.2;")
            self.assertRegex(out.getvalue(), "true")

        with captured_output() as (out, _):
            Lox.test_run("print (123 == (100 + 23)) != false;")
            self.assertRegex(out.getvalue(), "true")


if __name__ == "__main__":
    unittest.main()
