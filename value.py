from array import array

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

    if out:
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
