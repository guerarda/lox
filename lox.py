# lox

import logging
import sys

from .environment import Environment
from .interpreter import Interpreter
from .loxerrors import LoxError, LoxRuntimeError
from .parser import Parser
from .scanner import Scanner

global_environment = Environment()
has_error = False
has_runtime_error = False


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
        run(file.read())

        if has_error:
            exit(65)

        if has_runtime_error:
            exit(70)


def run_prompt():
    print("Lox Interpreter")
    while True:
        source = input("> ")
        run_catch_errors(source)
        global has_error
        has_error = False

        global has_runtime_error
        has_runtime_error = False


def run_catch_errors(source):
    try:
        run(source)

    except LoxError:
        return


def run(source: str):
    try:
        scanner = Scanner(source)
        parser = Parser(scanner.scan_tokens())
        stmts = parser.parse()

    except LoxRuntimeError as e:
        global has_runtime_error
        has_runtime_error = True
        raise e

    except LoxError as e:
        global has_error
        has_error = True
        raise e

    assert stmts is not None  # Would have raised an exception
    Interpreter(global_environment).interpret(stmts)


if __name__ == "__main__":
    main(sys.argv)
