from array import array


def print_value(value, end=""):
    print(f"{value:g}", end=end)


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
