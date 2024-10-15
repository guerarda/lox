# lox

from context import Context
from interpreter import Interpreter
from scanner import Scanner
from parser import Parser


def main(argv):
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
    while True:
        source = input("> ")
        context = Context(source)
        run(context)
        context.reset_errors()


def run(context):
    scanner = Scanner(context)
    context.tokens = scanner.scan_tokens()

    parser = Parser(context)
    expr = parser.parse()

    if context.has_error:
        return

    Interpreter(context).interpret(expr)


def test_run(src):
    """Same as run() but we use function that don't try to catch
    exceptions so we can catch them in the tests.
    """
    context = Context(src)
    scanner = Scanner(context)
    context.tokens = scanner.scan_tokens()

    parser = Parser(context)
    expr = parser.expression()

    if context.has_error:
        return

    return Interpreter(context).evaluate(expr)
