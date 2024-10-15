# context


class Context:
    def __init__(self, source=None):
        self.source = source
        self.tokens = []
        self.has_error = False
        self.has_runtime_error = False

    def reset_errors(self):
        self.has_error = False
        self.has_runtime_error = False
