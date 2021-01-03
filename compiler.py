from .error_machinery import ErrorMachinery
from .opcodes import *
from .scanner import TokenType
from .precedence import Precedence
from . import scanner, compiler, pratt, debug


errmac = ErrorMachinery()


class Emitter:
    def __init__(self):
        self.previous = None
        self.chunk = None

    def emit_constant(self, pos):
        self.emit_bytes(OP_CONSTANT, pos)

    def emit_return(self):
        self.emit_byte(OP_RETURN)

    def emit_byte(self, byte):
        self.chunk.write(byte, self.previous.line)

    def emit_bytes(self, b1, b2):
        self.emit_byte(b1)
        self.emit_byte(b2)


class Compiler(Emitter):
    def __init__(self):
        super().__init__()
        self.scanner = scanner.Scanner()
        self.previous = None
        self.current = None

    def compile(self, source, cnk):
        self.scanner.init(source)
        self.chunk = cnk
        self._advance()
        self._expression()
        self._consume(TokenType.EOF, "Expect end of expression.")
        self._end_compiler()
        return not errmac.errored

    def _advance(self):
        self.previous = self.current
        while True:
            self.current = self.scanner.scan_token()
            if self.current.type != TokenType.ERROR:
                break

            self._error_at_current(self.current.lexeme)

    def _grouping(self):
        self._expression()
        self._consume(TokenType.RIGHT_PAREN, "Expect ')' after expression.")

    def _expression(self):
        self._parse_precedence(Precedence.ASSIGNMENT)

    def _number(self):
        value = float(self.previous.lexeme)
        pos = self._make_constant(value)
        self.emit_constant(pos)

    def _binary(self):
        operator_type = self.previous.type
        rule = pratt.RULES.get(operator_type)
        self._parse_precedence(rule.precedence + 1)

        if operator_type is TokenType.PLUS:
            self.emit_byte(OP_ADD)
        elif operator_type is TokenType.MINUS:
            self.emit_byte(OP_SUBTRACT)
        elif operator_type is TokenType.STAR:
            self.emit_byte(OP_MULTIPLY)
        elif operator_type is TokenType.SLASH:
            self.emit_byte(OP_DIVIDE)

    def _literal(self):
        operator_type = self.previous.type

        if operator_type is TokenType.NIL:
            self.emit_byte(OP_NIL)
        elif operator_type is TokenType.FALSE:
            self.emit_byte(OP_FALSE)
        elif operator_type is TokenType.TRUE:
            self.emit_byte(OP_TRUE)

    def _unary(self):
        operator_type = self.previous.type

        self._parse_precedence(Precedence.UNARY)
        if operator_type is TokenType.MINUS:
            self.emit_byte(OP_NEGATE)
        elif operator_type is TokenType.BANG:
            self.emit_byte(OP_NOT)

    def _parse_precedence(self, precedence):
        self._advance()
        prefix_rule = pratt.RULES.get(self.previous.type).prefix
        if prefix_rule is None:
            self._error("Expect expression.")
            return

        prefix_rule(self)
        while precedence <= pratt.RULES.get(self.current.type).precedence:
            self._advance()
            infix_rule = pratt.RULES.get(self.previous.type).infix
            infix_rule(self)

    def _end_compiler(self):
        self.emit_return()
        if debug.PRINT_CODE and not errmac.errored:
            debug.disassemble(self.chunk, "code")

    def _make_constant(self, value):
        constant = self.chunk.add_constant(value)
        if constant > 255:
            self._error("Too many constants in one chunk.")
            return 0

        return constant

    def _consume(self, token_type, message):
        if self.current.type is token_type:
            self._advance()
        else:
            self._error_at_current(message)

    def _error_at_current(self, message):
        errmac.error_at(self.current, message)

    def _error(self, message):
        errmac.error_at(self.previous, message)
