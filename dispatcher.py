from operator import add, sub, mul, truediv, gt, lt

from .enums import VMResult
from . import types, value


def _binary_op(vm, opfunc):
    b = vm.stack.peek()
    a = vm.stack.peek(1)
    both_float = isinstance(a, float) and isinstance(b, float)
    both_string = isinstance(a, types.LoxString) and isinstance(b, types.LoxString)

    if not any([both_float, both_string]):
        vm.runtime_error("Operands must be two numbers or two strings.")
        return VMResult.RUNTIME_ERROR

    b = vm.stack.pop()
    a = vm.stack.pop()
    vm.stack.push(opfunc(a, b))


def _is_falsey(value):
    return value is None or not bool(value)


def _equality(a, b):
    if type(a) is not type(b):
        return False

    if a is True or a is False:
        return a is b

    if a is None:
        return True

    return a == b


class Arithmetics:
    def OP_ADD(self, vm):
        return _binary_op(vm, add)

    def OP_SUBTRACT(self, vm):
        return _binary_op(vm, sub)

    def OP_MULTIPLY(self, vm):
        return _binary_op(vm, mul)
        
    def OP_DIVIDE(self, vm):
        return _binary_op(vm, truediv)


class Comparisons:
    def OP_EQUAL(self, vm):
        b = vm.stack.pop()
        a = vm.stack.pop()
        vm.stack.push(_equality(a, b))

    def OP_GREATER(self, vm):
        return _binary_op(vm, gt)

    def OP_LESS(self, vm):
        return _binary_op(vm, lt)


class Singletons:
    def OP_NIL(self, vm):
        vm.stack.push(None)

    def OP_FALSE(self, vm):
        vm.stack.push(False)

    def OP_TRUE(self, vm):
        vm.stack.push(True)


class Instructions(Arithmetics, Singletons, Comparisons):
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

    def OP_NOT(self, vm):
        value = vm.stack.stack[-1]
        vm.stack.stack[-1] = _is_falsey(value)
