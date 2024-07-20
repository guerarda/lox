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
            run(file)
            if has_error:
                raise SystemExit
    

def run_prompt():
    while True:
        source = input("> ")
        run(source)
        global has_error
        has_error = False
        
    
def run(source):
    scanner = Scanner(source)
    scanner.scan_tokens()

    for token in scanner.tokens:
        print(token)


def error(position, message):
    print(f"Error: {position}: {message}")
    global has_error
    has_error = True
    
if __name__ == "__main__":
    main(sys.argv)
