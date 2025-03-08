# errors

from tokens import Token


class LoxError(Exception):
    def __init__(self, message: str = ""):
        super().__init__(message)
        self.message = message


class LoxRuntimeError(LoxError):
    def __init__(self, token: Token, message: str):
        super().__init__(message)
        self.token = token
        self.message = message

    def __str__(self):
        return f"{self.token.line + 1} | {self.message}."
