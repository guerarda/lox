class Context:
    def __init__(self, source):
        self.source = source
        self.has_error = False

    def error(self, position, message):
        print(f"Error: {position}: {message}")
        self.has_errors = True
