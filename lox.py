from context import Context
from scanner import Scanner


import sys

def main (argv):
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
            raise SystemExit
    

def run_prompt():
    while True:
        source = input("> ")
        context = Context(source)
        run(context)
        
    
def run(context):
    scanner = Scanner(context)
    scanner.scan_tokens()

    for token in scanner.tokens:
        print(token)


if __name__ == "__main__":
    main(sys.argv)
