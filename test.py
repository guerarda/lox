import unittest

import lox
from context import Context

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

if __name__ == "__main__":
    unittest.main()
