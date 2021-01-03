from enum import IntEnum, auto


class Precedence(IntEnum):
    NONE = auto()
    ASSIGNMENT = auto()
    OR = auto()
    AND = auto()
    EQUALITY = auto()
    TERM = auto()
    FACTOR = auto()
    UNARY = auto()
    CALL = auto()
    PRIMARY = auto()
