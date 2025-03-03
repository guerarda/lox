# Lox

## Description
A Python implementation of the Lox interpreter.

## Usage

To execute a program from a file:
```sh
# Read and execute a file
$ python lox.py myprogram.lox
```

Or you can run the interactive interpreter:
```sh
# Start the interpreter interactively
$ python lox.py

Lox Interpreter
> 
```

## Testing
The full test suite lives in `tests/cases`. It can be run like this:
```sh
$ make test                             # Run the complete test suite
$ make test variable                    # Run only the tests in tests/cases/variable
$ make test variable/shadow_global.lox  # Run a single test
```

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements
- [Crafting Interpreters](https://github.com/munificent/craftinginterpreters)
