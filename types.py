from array import array
from copy import copy
from enum import Enum, auto

from . import hashmap


class LoxTypes(Enum):
    OBJECT = auto()
    STRING = auto()


class LoxObject:
    type = LoxTypes.OBJECT


class LoxString(LoxObject):
    type = LoxTypes.STRING

    def __init__(self, s=""):
        self.buffer = array('B')
        self.length = 0
        if s:
            self.populate(s)

        self.hash = hashmap.fnv1a(self.buffer)

    def populate(self, s):
        for cp in s:
            n = ord(cp)
            if n > 0x7F:
                self._encode(n)
            else:
                self.buffer.append(n)

            self.length += 1

    # def index(self, idx):
    #     i = 0
    #     actual = 0
    #     top = len(self.buffer)
    #     while i < top:
    #         c = self.buffer[i]
    #         if actual == idx:
    #             if c & 0x80:
    #                 return self._decode(self.buffer[i:i+3])
    #             else:
    #                 return chr(c)

    #         i += 3 if c & 0x80 else 1
    #         actual += 1

    def merge(self, other):
        self.buffer += other.buffer
        self.length += other.length

    def _encode(self, value):
        self.buffer.append(((value & 0xFF0000) >> 16) | 0x80) # Mark as Unicode character start
        self.buffer.append((value & 0xFF00) >> 8)
        self.buffer.append(value & 0xFF)

    def _decode(self, hunk):
        padded = bytes((hunk[2], hunk[1], hunk[0] & 0x7F, 0))
        return padded.decode("utf-32-le")

    def __str__(self):
        chars = []
        i = 0
        top = len(self.buffer)
        while i < top:
            c = self.buffer[i]
            if c & 0x80:
                dec = self._decode(self.buffer[i:i+3])
                i += 3
            else:
                dec = chr(c)
                i += 1

            chars.append(dec)

        return "".join(chars)

    def __eq__(self, other):
        if isinstance(other, LoxString):
            return all([self.length == other.length, self.hash == other.hash,
                self.buffer == other.buffer])
        else:
            return self.buffer == other

    def __add__(self, other):
        new = LoxString()
        new.merge(self)
        new.merge(other)
        return new
