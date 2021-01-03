from operator import add, sub, mul, truediv

from . import value


def binary_op(stack, opfunc):
    b = stack.pop()
    a = stack.pop()
    stack.push(opfunc(a, b))


class Arithmetics:
    def OP_ADD(self, vm):
        return binary_op(vm.stack, add)

    def OP_SUBTRACT(self, vm):
        return binary_op(vm.stack, sub)

    def OP_MULTIPLY(self, vm):
        return binary_op(vm.stack, mul)
        
    def OP_DIVIDE(self, vm):
        return binary_op(vm.stack, truediv)


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
        vm.stack.stack[-1] *= -1
