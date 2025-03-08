# lox

import logging
import sys

from analyzer import Analyzer
from environment import Environment
from errors import LoxError, LoxRuntimeError
from interpreter import Interpreter, REPLInterpreter
from parser import Parser
from scanner import Scanner

global_environment = Environment()
has_error = False
has_runtime_error = False


def main(argv):
    logging.basicConfig(format="%(name)s %(levelname)s: %(message)s")
    if len(argv) > 2:
        sys.exit("Usage lox.py filename")

    if len(argv) == 2:
        run_file(argv[1])

    else:
        run_prompt()


def run_file(path):
    global has_error
    has_error = False

    global has_runtime_error
    has_runtime_error = False

    with open(path) as file:
        run_catch_errors(file.read())
        if has_error:
            sys.exit(65)

        if has_runtime_error:
            sys.exit(70)


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
    global has_error
    global has_runtime_error

    try:
        run(source, is_repl)

    except LoxRuntimeError:
        has_runtime_error = True

    except LoxError:
        has_error = True


def run(source: str, is_repl: bool = False):

    scanner = Scanner(source)
    parser = Parser(scanner.scan_tokens())
    stmts = parser.parse()

    if stmts is None:
        global has_error
        has_error = True
        return

    Analyzer().analyze(stmts)

    if is_repl:
        REPLInterpreter(global_environment).interpret(stmts)
    else:
        Interpreter(Environment()).interpret(stmts)


if __name__ == "__main__":
    main(sys.argv)
