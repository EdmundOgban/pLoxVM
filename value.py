from array import array


def print_value(value, end=""):
    out = None

    if value is None:
        out = "nil"
    elif value is True or value is False:
        out = str(value).lower()
    elif isinstance(value, float):
        out = f"{value:g}"

    if out:
        print(out, end=end)


class ValueArray:
    # def __init__(self):
    #     self.init()

    def init(self, type="d"):
        self.values = array(type)
        self._count = 0

    def write(self, byte):
        self.values.append(byte)
        self._count += 1

    def free(self):
        self.init()

    @property
    def count(self):
        return self._count
