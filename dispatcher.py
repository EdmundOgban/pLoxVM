from operator import add, sub, mul, truediv

from .enums import VMResult
from . import value


def binary_op(vm, opfunc):
    if not isinstance(vm.stack.peek(), float) or not isinstance(vm.stack.peek(1), float):
        vm.runtime_error("Operands must be numbers.")
        return VMResult.RUNTIME_ERROR

    b = vm.stack.pop()
    a = vm.stack.pop()
    vm.stack.push(opfunc(a, b))


class Arithmetics:
    def OP_ADD(self, vm):
        return binary_op(vm, add)

    def OP_SUBTRACT(self, vm):
        return binary_op(vm, sub)

    def OP_MULTIPLY(self, vm):
        return binary_op(vm, mul)
        
    def OP_DIVIDE(self, vm):
        return binary_op(vm, truediv)


class Instructions(Arithmetics):
    def dispatch(self, instr_name, vm):
        return getattr(self, instr_name)(vm)

    def OP_RETURN(self, vm):
        value.print_value(vm.stack.pop(), end="\n")
        return True

    def OP_CONSTANT(self, vm):
        addr = vm.next_instruction()
        constant = vm.chunk.constants.values[addr]
        vm.stack.push(constant)

    def OP_NEGATE(self, vm):
        if not isinstance(vm.stack.peek(), float):
            vm.runtime_error("Operand must be a number.")
            return VMResult.RUNTIME_ERROR

        vm.stack.stack[-1] *= -1
