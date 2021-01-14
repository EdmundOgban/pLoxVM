from .opcodes import *
from .enums import VMResult
from .error_machinery import ErrorMachinery
from . import compiler, chunk, dispatcher, hashmap, value
from . import debug


errmac = ErrorMachinery()


class VM:
    def __init__(self):
        self.stack = value.Stack()
        self.compiler = compiler.Compiler()
        self.globals = hashmap.HashMap()
        self.instructions = dispatcher.Instructions()
        self.init()

    def init(self):
        self.chunk = None
        self.ip = 0
        self.stack.reset()

    def trace(self):
        print("          ", end="")
        for slot in self.stack:
            print("[ ", end="")
            value.print_value(slot)
            print(" ]", end="")
        print()

        debug.disasm_instruction(self.chunk, self.ip)

    def run(self):
        while True:
            if debug.TRACE_EXECUTION:
                self.trace()

            instr = self.next_instruction()
            instr_name = OPCODES[instr]
            if instr_name is not None:
                ret = self.instructions.dispatch(instr_name, self)
                if ret is not None:
                    return ret
            else:
                # TODO: report invalid instruction
                pass

    def interpret(self, source):
        self.chunk = chunk.Chunk()
        if not self.compiler.compile(source, self.chunk):
            return VMResult.COMPILE_ERROR

        return self.run()

    def next_instruction(self):
        instr = self.chunk.code[self.ip]
        self.ip += 1
        return instr

    def next_short(self):
        val = self.chunk.code[self.ip]
        self.ip += 1
        val <<= 8
        val |= self.chunk.code[self.ip]
        self.ip += 1
        return val

    def runtime_error(self, message):
        line = self.chunk.lines[self.ip - 1]
        message = f"{message}\n[line {line}] in script"
        errmac.runtime_error(message)
