import unittest

import lox

class TestLox(unittest.TestCase):
    def test_operators(self):
        lox.run("- + == != =")

    def test_string(self):
        lox.run("\"this is a string")

    def test_number(self):
        lox.run("123")
        lox.run("123.456")
        lox.run(".2134")
        lox.run("123.")

    def test_identifer(self):
        lox.run("var")
        lox.run("variable")
        lox.run("my_function")
        lox.run("_my_var")
        lox.run("my1337")

if __name__ == "__main__":
    unittest.main()
