# loxtest

import argparse
import os
import re
import unittest
from pathlib import Path

EXPECT_OUTPUT_PATTERN = re.compile("// expect: ?(.*)")
EXPECT_ERROR_PATTERN = re.compile(r"// Error at ['\"](.+?)['\"]:\s+(.*)")
EXPECT_RUNTIME_ERROR_PATTERN = re.compile("// expect runtime error: (.+)")

ALIASES = {
    "ControlFlow": [
        "block/empty.lox",
        "for",
        "if",
        "logical_operator",
        "while",
        "variable/unreached_undefined.lox",
    ],
    "Classes": [
        "assignment/to_this.lox" "call/object.lox",
        "class",
        "closure/close_over_method_parameter.lox",
        "constructor",
        "field",
        "inheritance",
        "method",
        "number/decimal_point_at_eof.lox",
        "number/trailing_dot.lox",
        "operator/equals_class.lox",
        "operator/equals_method.lox",
        "operator/not_class.lox",
        "regression/394.lox",
        "super",
        "this",
        "return/in_method.lox",
        "variable/local_from_method.lox",
    ],
    "EarlyChapters": ["scanning", "expressions"],
    "Functions": [
        "call",
        "closure",
        "for/closure_in_body.lox",
        "for/return_closure.lox",
        "for/return_inside.lox",
        "for/syntax.lox",
        "function",
        "operator/not.lox",
        "regression/40.lox",
        "return",
        "unexpected_character.lox",
        "while/closure_in_body.lox",
        "while/return_closure.lox",
        "while/return_inside.lox",
    ],
    "Inheritance": [
        "class/local_inherit_other.lox",
        "class/local_inherit_self.lox",
        "class/inherit_self.lox",
        "class/inherited_method.lox",
        "inheritance",
        "regression/394.lox",
        "super",
    ],
    "Limits": [
        "limit/loop_too_large.lox",
        "limit/no_reuse_constants.lox",
        "limit/too_many_constants.lox",
        "limit/too_many_locals.lox",
        "limit/too_many_upvalues.lox",
        "limit/stack_overflow.lox",
        "function/too_many_parameters.lox",
    ],
}


def boilerplate() -> str:

    str = "import sys\n"
    str += "import unittest\n"
    str += "from contextlib import contextmanager\n"
    str += "from io import StringIO\n\n"
    str += "import lox as Lox\n"
    str += "\n\n"

    str += "@contextmanager\n"
    str += "def captured_output():\n"
    str += "    new_out, new_err = StringIO(), StringIO()\n"
    str += "    old_out, old_err = sys.stdout, sys.stderr\n"
    str += "    try:\n"
    str += "        sys.stdout, sys.stderr = new_out, new_err\n"
    str += "        yield sys.stdout, sys.stderr\n"
    str += "    finally:\n"
    str += "        sys.stdout, sys.stderr = old_out, old_err\n"
    str += "\n\n"

    return str


def begin_test_case(name: str) -> str:
    return f"class {name.capitalize()}(unittest.TestCase):\n"


def add_test(filename: str) -> str:
    name = Path(filename).stem

    expected_outputs = []
    expected_errors = []
    expected_runtime_errors = []

    with open(filename) as file:
        lines = file.readlines()
        for i, l in enumerate(lines):
            output_match = EXPECT_OUTPUT_PATTERN.search(l)
            error_match = EXPECT_ERROR_PATTERN.search(l)
            runtime_error_match = EXPECT_RUNTIME_ERROR_PATTERN.search(l)

            if output_match:
                expected_outputs.append(output_match.group(1))

            elif error_match:
                token = error_match.group(1)
                message = error_match.group(2)
                expected_errors.append((i + 1, token, message))

            elif runtime_error_match:
                message = runtime_error_match.group(1)
                expected_runtime_errors.append((i + 1, message))

    # If there are no expectations at all, return empty string
    if not expected_outputs and not expected_errors and not expected_runtime_errors:
        return ""

    str = f"    def test_{name}(self):\n"
    str += f"        with captured_output() as (out, err):\n"

    if expected_errors or expected_runtime_errors:
        str += f"            with self.assertRaises(SystemExit):\n"
        str += f"                Lox.run_file('{filename}')\n\n"
    else:
        str += f"            Lox.run_file('{filename}')\n\n"

    # Handle expected outputs
    if expected_outputs:
        str += f"            # Expected Outputs\n"
        str += f"            self.assertEqual(out.getvalue().splitlines(), {expected_outputs})\n\n"

    # Handle expected errors
    if expected_errors:
        # Check that each expected error appears in the error output
        str += f"            # Expected Errors\n"
        for line, token, message in expected_errors:
            error_msg = f"{line} | Error at '{repr(token)[1:-1]}': {message}"
            str += f"            self.assertIn({repr(error_msg)},  err.getvalue().splitlines())\n"
        str += "\n"

    # Handle expected runtime errors
    if expected_runtime_errors:
        # Check that each expected error appears in the error output
        str += f"            # Expected Runtime Errors\n"
        for line, message in expected_runtime_errors:
            error_msg = f"{line} | {message}"
            str += f"            self.assertIn({repr(error_msg)}, err.getvalue().splitlines())\n"
        str += "\n"

    return str


def find_tests(dir: str) -> dict[str, list[str]]:
    files = Path(dir).glob("**/*.lox")

    test_names = {}
    for f in files:
        test_names.setdefault(f.parent.name, []).append(f)

    return test_names


def generate_tests(basedir: str, output: str):
    str = boilerplate()

    for k, v in sorted(find_tests(basedir).items()):

        tests = []
        for t in v:
            teststr = add_test(t)
            if teststr:
                tests.append(teststr)

        if tests:
            str += begin_test_case(k)
            str += "".join(tests)

    with open(output, "w") as out:
        out.write(str)


def list_tests(basedir: str):
    tests = find_tests(basedir)

    for k, v in sorted(tests.items(), key=lambda p: p == ""):
        if k == Path(basedir).stem:
            indent = 0
        else:
            indent = 4
            print(f"\n{k}:")

        for t in v:
            print(f"{' '*indent}{Path(t).relative_to(basedir)}")


def filter_tests(
    add: list[str], skip: list[str], suite: unittest.TestSuite
) -> unittest.TestSuite:

    filtered = unittest.TestSuite()

    for test in suite:
        if isinstance(test, unittest.TestCase):
            # It's an individual test
            class_name = test.__class__.__name__
            test_name = test._testMethodName

            if class_name.casefold() in skip:
                # The group is to be skipped
                continue

            test_file = f"{class_name.casefold()}/{test_name[5:].casefold()}.lox"
            if test_file in skip:
                # The individual file is to be skipped
                continue

            if not add or class_name.casefold() in add or test_file in add:
                filtered.addTest(test)
        else:
            # It's a suite, recursively process it
            filtered.addTest(filter_tests(add, skip, test))

    return filtered


def run_tests(targets: list[str], skip: list[str], verbosity: int):
    loader = unittest.TestLoader()
    all_tests = loader.discover(".", "test*.py")

    add = []
    remove = []

    for target in targets:
        if target in ALIASES:
            add.extend(ALIASES[target])
        else:
            add.append(target)

    for s in skip:
        if s in ALIASES:
            remove.extend(ALIASES[s])
        else:
            add.append(s)

    suite = filter_tests(add, remove, all_tests) if targets or skip else all_tests

    runner = unittest.TextTestRunner(verbosity=verbosity)
    return runner.run(suite)


def main():
    parser = argparse.ArgumentParser(
        description="Generate and run test for Lox interpreter"
    )
    parser.add_argument("-v", "--verbose", action="count", default=1)

    subparsers = parser.add_subparsers(
        dest="command", required=True, help="Command to execute"
    )

    # Parser for generating unit tests from the test files
    gen_parser = subparsers.add_parser(
        "generate", help="Generate unit test cases from test files"
    )
    gen_parser.add_argument("path", help="Directory containing the test files")
    gen_parser.add_argument("--out", help="Output for the generated test file")

    # Parser for running all or a subset of tests
    run_parser = subparsers.add_parser("run", help="Run all or a subset of unit tests")
    run_parser.add_argument(
        "targets", nargs="*", help="Tests to run. Run all tests if empty"
    )
    run_parser.add_argument("--skip", nargs="+", help="Tests to skip")

    # Parser for listing tests
    list_parser = subparsers.add_parser("list", help="List all the unit tests found")
    list_parser.add_argument("path", help="Directory containing the test files")

    args = parser.parse_args()

    if args.command == "generate":
        generate_tests(args.path, args.out)

    elif args.command == "list":
        list_tests(args.path)

    elif args.command == "run":
        if args.skip is None:
            args.skip = []
        run_tests(args.targets, args.skip, args.verbose)


if __name__ == "__main__":
    main()
