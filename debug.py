from .opcodes import *
from . import value

TRACE_EXECUTION = False
PRINT_CODE = False


def simple_instruction(opname, offset):
    print(opname)
    return offset + 1


def constant_instruction(opname, chunk, offset):
    constant = chunk.code[offset + 1]
    print(f"{opname:16} {constant:4} ", end="")
    value.print_value(chunk.constants.values[constant])
    print()
    return offset + 2


def byte_instruction(opname, chunk, offset):
    slot = chunk.code[offset + 1]
    print(f"{opname:16} {slot:4} ")
    return offset + 2


def jump_instruction(opname, sign, chunk, offset):
    jump = chunk.code[offset + 1] << 8
    jump |= chunk.code[offset + 2]
    print(f"{opname:16} {offset:4} -> {offset + 3 + sign * jump}")
    return offset + 3


def disasm_instruction(chunk, offset):
    inst = chunk.code[offset]
    if offset > 0 and chunk.lines[offset] == chunk.lines[offset - 1]:
        print("   | ", end="")
    else:
        print(f"{offset:04} ", end="")

    opname = OPCODES[inst]
    if opname in OPCODES_SIMPLE:
        return simple_instruction(opname, offset)
    elif opname in OPCODES_CONSTANT:
        return constant_instruction(opname, chunk, offset)
    elif opname in OPCODES_BYTEINSTR:
        return byte_instruction(opname, chunk, offset)
    elif opname in OPCODES_JUMPINSTR:
        return jump_instruction(opname, -1 if inst == OP_LOOP else 1, chunk, offset)
    else:
        print(f"Unknown opcode {inst}")

    return offset + 1


def disassemble(chunk, name):
    print(f"== {name} ==")
    offset = 0
    while offset < chunk.count:
        offset = disasm_instruction(chunk, offset)
