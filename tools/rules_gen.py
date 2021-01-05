from pathlib import Path
from textwrap import dedent

from ..scanner import TokenType


IMPORTS = [
    "from collections import namedtuple",
    "",
    "from .scanner import TokenType",
    "from .compiler import Precedence",   
]

PREAMBLE = """\
ParseRule = namedtuple("ParseRule", ["prefix", "infix", "precedence"])
"""

PRECEDENCES = {
    TokenType.LEFT_PAREN: ["grouping", None, None],
    TokenType.MINUS: ["unary", "binary", "TERM"],
    TokenType.PLUS: [None, "binary", "TERM"],
    TokenType.SLASH: [None, "binary", "FACTOR"],
    TokenType.STAR: [None, "binary", "FACTOR"],
    TokenType.BANG: ["unary", None, None],
    TokenType.BANG_EQUAL: [None, "binary", "EQUALITY"],
    TokenType.EQUAL_EQUAL: [None, "binary", "EQUALITY"],
    TokenType.GREATER: [None, "binary", "COMPARISON"],
    TokenType.GREATER_EQUAL: [None, "binary", "COMPARISON"],
    TokenType.LESS: [None, "binary", "COMPARISON"],
    TokenType.LESS_EQUAL: [None, "binary", "COMPARISON"],
    TokenType.STRING: ["string", None, None],
    TokenType.NUMBER: ["number", None, None],
    TokenType.FALSE: ["literal", None, None],
    TokenType.NIL: ["literal", None, None],
    TokenType.TRUE: ["literal", None, None],
}


def write_imports(f):
    for line in IMPORTS:
        f.write(f"{line}\n")

    f.write("\n\n")


def write_preamble(f):
    f.write(f"{PREAMBLE}\n\n")


def write_precedences(f, tokens=TokenType):
    functions = set()
    lines = []
    
    for name, value in tokens.__members__.items():
        tokprec = PRECEDENCES.get(value)
        if tokprec:
            prefix = tokprec[0]
            infix = tokprec[1]
            prec = tokprec[2]
            if prefix:
                functions.add(prefix)

            if infix:
                functions.add(infix)

            s = f"ParseRule({prefix}, {infix}, Precedence.{str(prec).upper()})"
        else:
            s = "ParseRule(None, None, Precedence.NONE)"

        lines.append(f"    {value.__class__.__name__}.{name}: " + s)

    for function in sorted(functions):
        f.write(dedent(f""" \
            def {function}(inst):
                return inst._{function}()
            \n\n"""))

    f.write("RULES = {\n")
    for line in lines:
        f.write(f"{line},\n")
    f.write("}\n")


def main(fname):
    with open(fname, "w") as f:
        write_imports(f)
        write_preamble(f)
        write_precedences(f)


if __name__ == "__main__":
    main(Path(__file__).parent.parent.joinpath("pratt.py"))
