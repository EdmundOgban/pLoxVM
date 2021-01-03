OPCODES_SIMPLE = [
    "OP_ADD",
    "OP_SUBTRACT",
    "OP_MULTIPLY",
    "OP_DIVIDE",
    "OP_NEGATE",
    "OP_NIL",
    "OP_TRUE",
    "OP_FALSE",
    "OP_RETURN",
]

OPCODES_CONSTANT = [
    "OP_CONSTANT",
]

OPCODES = [*OPCODES_SIMPLE, *OPCODES_CONSTANT]
OPNAMES = {}

for machcode, opcode in enumerate(OPCODES, 1):
    globals()[opcode] = machcode
    OPNAMES[machcode] = opcode
