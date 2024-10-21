# lox

from context import Context
from interpreter import Interpreter
from scanner import Scanner
from parser import Parser

import logging
import sys

LOX_INTERPRETER = Interpreter()


def main(argv):
    logging.basicConfig(format="%(name)s %(levelname)s: %(message)s")
    if len(argv) > 2:
        raise SystemExit("Usage lox.py filename")

    if len(argv) == 2:
        run_file(argv[1])

    else:
        run_prompt()


def run_file(path):
    with open(path) as file:
        context = Context(file)
        run(context)

        if context.has_error:
            exit(65)

        if context.has_runtime_error:
            exit(70)


def run_prompt():
    print("Lox Interpreter")
    while True:
        source = input("> ")
        context = Context(source)
        run(context)
        context.reset_errors()


def run(context):
    scanner = Scanner(context)
    context.tokens = scanner.scan_tokens()

    parser = Parser(context)
    stmts = parser.parse()

    if context.has_error:
        return

    assert stmts is not None  # Would have raised an exception
    LOX_INTERPRETER.context = context
    LOX_INTERPRETER.interpret(stmts)


def test_run(src):
    """Same as run() but we use function that don't try to catch
    exceptions so we can catch them in the tests.
    """
    LOX_INTERPRETER.context = Context(src)
    scanner = Scanner(LOX_INTERPRETER.context)

    LOX_INTERPRETER.context.tokens = scanner.scan_tokens()

    parser = Parser(LOX_INTERPRETER.context)
    stmts = parser.statements()

    if LOX_INTERPRETER.context.has_error:
        return

    return LOX_INTERPRETER.execute_statements(stmts)


if __name__ == "__main__":
    main(sys.argv)
