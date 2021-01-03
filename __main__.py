import sys

from .ploxvm import Plox
from .chunk import Chunk
from .opcodes import *
from .vm import VM


def usage(me):
    print(f"Usage: {me} [script]")


if __name__ == "__main__":
    lox = Plox()

    if len(sys.argv) == 1:
        lox.repl()
    elif len(sys.argv) == 2:
        lox.run_file(sys.argv[1])
    else:
        usage(sys.argv[0])
