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

OPCODES_BYTEINSTR = [
    "OP_GET_LOCAL",
    "OP_SET_LOCAL",
    "OP_GET_GLOBAL",
    "OP_DEFINE_GLOBAL",
    "OP_SET_GLOBAL",
]

OPCODES_JUMPINSTR = [
    "OP_JUMP_IF_FALSE",
    "OP_JUMP",
    "OP_LOOP"
]

OPCODES = [*OPCODES_SIMPLE, *OPCODES_CONSTANT, *OPCODES_BYTEINSTR, *OPCODES_JUMPINSTR]

for machcode, opcode in enumerate(OPCODES):
    globals()[opcode] = machcode
