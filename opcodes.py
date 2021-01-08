OPCODES_SIMPLE = [
    "OP_ADD",
    "OP_SUBTRACT",
    "OP_MULTIPLY",
    "OP_DIVIDE",
    "OP_NOT",
    "OP_PRINT",
    "OP_NEGATE",
    "OP_FALSE",
    "OP_POP",
    "OP_GET_GLOBAL",
    "OP_DEFINE_GLOBAL",
    "OP_SET_GLOBAL",
    "OP_NIL",
    "OP_TRUE",
    "OP_EQUAL",
    "OP_GREATER",
    "OP_LESS",
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
