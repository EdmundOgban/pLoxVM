from array import array
from . import debug, value


class Chunk:
    def __init__(self):
        self.constants = value.ValueArray()
        self.init()

    def init(self):
        self.code = array('B')
        self.lines = array('i')
        self._count = 0
        self.constants.init()

    def write(self, byte, line):
        self.code.append(int(byte) & 0xFF)
        self.lines.append(line)
        self._count += 1

    def add_constant(self, value):
        pos = self.constants.count
        self.constants.write(value)
        return pos

    def disassemble(self, name):
        return debug.disassemble(self, name)

    @property
    def count(self):
        return self._count
