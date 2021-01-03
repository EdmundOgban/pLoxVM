import sys

from .scanner import TokenType


def stderr(message, *args, **kwargs):
    print(message, *args, file=sys.stderr, **kwargs)


class ErrorMachinery:
    __instance = None

    def __init__(self):
        self.reset()

    def __new__(cls):
        if ErrorMachinery.__instance is None:
            ErrorMachinery.__instance = object.__new__(cls)

        return ErrorMachinery.__instance

    def error_at(self, token, message):
        if self.panic_mode:
            return

        self.panic_mode = True
        stderr(f"[line {token.line}] Error", end="")
        if token.type is TokenType.EOF:
            stderr(" at end", end="")
        elif token.type is not TokenType.ERROR:
            stderr(f" at {token.lexeme}", end="")

        stderr(f": {message}")
        self.errored = True

    def runtime_error(self, message):
        stderr(message)
        self.runtime_errored = True

    def reset(self):
        self.errored = False
        self.runtime_errored = False
        self.panic_mode = False