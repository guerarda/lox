import unittest

import lox
import expression as Expr

from ast_printer import ASTPrinter
from context import Context
from tokens import Token


class TestLox(unittest.TestCase):
    def test_operators(self):
        lox.run(Context("- + == != ="))

    def test_string(self):
        lox.run(Context("\"this is a string\""))

    def test_number(self):
        str = ("123"
               " 123.456"
               " .123"
               " 123.")
        
        lox.run(Context(str))

    def test_identifer(self):
        str = ("var"
               " variable"
               " my_function"
               " _my_var"
               " my1337")
        lox.run(Context(str))

class TestASTPrinter(unittest.TestCase):
    def test_print(self):
        t_min = Token(Token.Type.MINUS, "-", None, 1)
        t_star = Token(Token.Type.STAR, "*", None, 1)

        e_123 = Expr.Literal(123.0)
        e_456 = Expr.Literal(45.6)

        e_min123 = Expr.Unary(t_min, e_123)
        e_grp = Expr.Grouping(e_456)

        e_mult = Expr.Binary(e_min123, t_star, e_grp)


        print(ASTPrinter().print(e_mult))


if __name__ == "__main__":
    unittest.main()



