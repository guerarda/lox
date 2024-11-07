# lox

import logging
import sys

from environment import Environment
from errors import LoxError, LoxRuntimeError
from interpreter import Interpreter, REPLInterpreter
from parser import Parser
from resolver import Resolver
from scanner import Scanner

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
        run_catch_errors(file.read())

        if has_error:
            exit(65)

        if has_runtime_error:
            exit(70)


def run_prompt():
    print("Lox Interpreter")
    while True:
        source = input("> ")
        run_catch_errors(source, True)
        global has_error
        has_error = False

        global has_runtime_error
        has_runtime_error = False


def run_catch_errors(source: str, is_repl: bool = False):
    try:
        run(source, is_repl)

    except LoxError:
        return


def run(source: str, is_repl: bool = False):
    global has_error
    global has_runtime_error
    try:
        scanner = Scanner(source)
        parser = Parser(scanner.scan_tokens())
        stmts = parser.parse()

        if parser.has_error:
            has_error = True
            return

    except LoxRuntimeError as e:
        has_runtime_error = True
        raise e

    except LoxError as e:
        has_error = True
        raise e

    assert stmts is not None  # Would have raised an exception

    interpreter = (
        REPLInterpreter(global_environment)
        if is_repl
        else Interpreter(global_environment)
    )

    resolver = Resolver(interpreter)
    resolver.resolve(stmts)

    if resolver.has_error:
        has_error = True
        return

    if is_repl:
        REPLInterpreter(global_environment).interpret(stmts)
    else:
        Interpreter(global_environment).interpret(stmts)


if __name__ == "__main__":
    main(sys.argv)
