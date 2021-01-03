from enum import Enum, auto


class VMResult(Enum):
    OK = auto()
    COMPILE_ERROR = auto()
    RUNTIME_ERROR = auto()

