from array import array

from .exceptions import LoxStackOverflow, LoxTooManyLocals
from . import types


def print_value(value, end=""):
    out = None

    if value is None:
        out = "nil"
    elif value is True or value is False:
        out = str(value).lower()
    elif isinstance(value, float):
        out = f"{value:g}"
    elif isinstance(value, types.LoxString):
        out = str(value)
    else:
        out = f"??? {value}"

    if out is not None:
        print(out, end=end)


class ValueArray:
    # def __init__(self):
    #     self.init()

    def init(self):
        self.values = []
        self._count = 0

    def write(self, byte):
        self.values.append(byte)
        self._count += 1

    @property
    def count(self):
        return self._count


class Stack:
    def __init__(self, maxsize=256):
        self.stack = []
        self.stack_top = 0
        self.maxsize = maxsize

    def push(self, val):
        if self.stack_top == self.maxsize:
            raise LoxStackOverflow

        self.stack.append(val)
        self.stack_top += 1

    def pop(self):
        self.stack_top -= 1
        return self.stack.pop()

    def peek(self, distance=0):
        return self.stack[-1 - distance]

    def reset(self):
        self.stack_top = 0

    def __iter__(self):
        return iter(self.stack)


class Locals:
    def __init__(self):
        self.locals = []
        self.depth = []
        self.scope_depth = 0
        self.count = 0

    # @property
    # def count(self):
    #     #return len(self.locals)

    def add(self, name, *, uninitialized=True):
        if self.count > 255:
            raise LoxTooManyLocals

        self.locals.append(name)
        self.count += 1
        self.depth.append(-1 if uninitialized else self.scope_depth)

    def initialize_current(self):
        self.depth[self.count - 1] = self.scope_depth

    def __iter__(self):
        for name, depth in zip(self.locals, self.depth):
            yield name, depth
