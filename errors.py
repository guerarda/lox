# errors


class LoxError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message


class LoxRuntimeError(LoxError):
    pass
