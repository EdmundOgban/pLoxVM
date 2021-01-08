from .error_machinery import ErrorMachinery
from .opcodes import *
from .scanner import TokenType
from .precedence import Precedence
from . import compiler, hashmap, pratt, scanner, types
from . import debug


errmac = ErrorMachinery()

BINARY_OPS = {
    TokenType.PLUS: (OP_ADD,),
    TokenType.MINUS: (OP_SUBTRACT,),
    TokenType.STAR: (OP_MULTIPLY,),
    TokenType.SLASH: (OP_DIVIDE,),
    TokenType.BANG_EQUAL: (OP_EQUAL, OP_NOT),
    TokenType.EQUAL_EQUAL: (OP_EQUAL,),
    TokenType.GREATER: (OP_GREATER,),
    TokenType.GREATER_EQUAL: (OP_LESS, OP_NOT),
    TokenType.LESS: (OP_LESS,),
    TokenType.LESS_EQUAL: (OP_GREATER, OP_NOT),
}

SYNC_TOKENS = {
    TokenType.CLASS,
    TokenType.FUN,
    TokenType.VAR,
    TokenType.FOR,
    TokenType.IF,
    TokenType.WHILE,
    TokenType.PRINT,
    TokenType.RETURN
}


class VariablesManager:
    def parse_variable(self, message):
        pass

    def define_variable(self, var):
        pass


class Emitter:
    def __init__(self):
        self.previous = None
        self.chunk = None

    def emit_constant(self, value):
        pos = self._make_constant(value)
        self.emit_bytes(OP_CONSTANT, pos)

    def emit_return(self):
        self.emit_byte(OP_RETURN)

    def emit_byte(self, byte):
        self.chunk.write(byte, self.previous.line)

    def emit_bytes(self, *args):
        for byte in args:
            self.emit_byte(byte)

    def _make_constant(self, value):
        constant = self.chunk.add_constant(value)
        if constant > 255:
            self._error("Too many constants in one chunk.")
            return 0

        return constant

class Compiler(Emitter):
    def __init__(self):
        super().__init__()
        self.scanner = scanner.Scanner()
        self.strings = hashmap.HashMap()
        self.globals = hashmap.HashMap()
        self.previous = None
        self.current = None

    def compile(self, source, cnk):
        self.scanner.init(source)
        self.chunk = cnk
        self._advance()

        while not self._match(TokenType.EOF):
            self._declaration()

        # self._expression()
        # self._consume(TokenType.EOF, "Expect end of expression.")

        self._end_compiler()
        return not errmac.errored

    def _advance(self):
        self.previous = self.current
        while True:
            self.current = self.scanner.scan_token()
            if self.current is None:
                continue

            if self.current.type is not TokenType.ERROR:
                break

            self._error_at_current(self.current.lexeme)

    def _grouping(self, can_assign):
        self._expression()
        self._consume(TokenType.RIGHT_PAREN, "Expect ')' after expression.")

    def _expression(self):
        self._parse_precedence(Precedence.ASSIGNMENT)

    def _statement_var(self):
        globvar = self._parse_variable("Expect variable name.")

        if self._match(TokenType.EQUAL):
            self._expression()
        else:
            self.emit_byte(OP_NIL)

        self._consume(TokenType.SEMICOLON, "Expect ';' after variable declaration.")
        self._define_variable(globvar)

    def _statement_expression(self):
        self._expression()
        self._consume(TokenType.SEMICOLON, "Expect ';' after expression.")
        self.emit_byte(OP_POP)

    def _statement_print(self):
        self._expression()
        self._consume(TokenType.SEMICOLON, "Expect ';' after value.")
        self.emit_byte(OP_PRINT)

    def _declaration(self):
        if self._match(TokenType.VAR):
            self._statement_var()
        else:
            self._statement()

        if errmac.panic_mode:
            self._synchronize()

    def _statement(self):
        if self._match(TokenType.PRINT):
            self._statement_print()
        else:
            self._statement_expression()

    def _number(self, can_assign):
        value = float(self.previous.lexeme)
        self.emit_constant(value)

    def _string(self, can_assign):
        string = self.previous.lexeme[1:-1]
        inst = self.strings.get(string)
        if inst is None:
            inst = types.LoxString(string)
            self.strings.insert(inst.hash, inst, byhash=True)

        self.emit_constant(inst)

    def _variable(self, can_assign):
        self._named_variable(self.previous.lexeme, can_assign)

    def _named_variable(self, name, can_assign):
        arg = self._identifier_constant(name)

        if can_assign and self._match(TokenType.EQUAL):
            self._expression()
            self.emit_bytes(OP_SET_GLOBAL, arg)
        else:
            self.emit_bytes(OP_GET_GLOBAL, arg)

    def _binary(self, can_assign):
        operator_type = self.previous.type
        rule = pratt.RULES.get(operator_type)
        opcodes = BINARY_OPS.get(operator_type)
        self._parse_precedence(rule.precedence + 1)
        self.emit_bytes(*opcodes)

    def _literal(self, can_assign):
        operator_type = self.previous.type

        if operator_type is TokenType.NIL:
            self.emit_byte(OP_NIL)
        elif operator_type is TokenType.FALSE:
            self.emit_byte(OP_FALSE)
        elif operator_type is TokenType.TRUE:
            self.emit_byte(OP_TRUE)

    def _unary(self, can_assign):
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

        can_assign = precedence <= Precedence.ASSIGNMENT
        prefix_rule(self, can_assign)
        while precedence <= pratt.RULES.get(self.current.type).precedence:
            self._advance()
            infix_rule = pratt.RULES.get(self.previous.type).infix
            infix_rule(self, can_assign)

        if can_assign and self._match(TokenType.EQUAL):
            self._error("Invalid assignment target.")

    def _parse_variable(self, message):
        self._consume(TokenType.IDENTIFIER, message)
        return self._identifier_constant(self.previous.lexeme)

    def _define_variable(self, globvar):
        self.emit_bytes(OP_DEFINE_GLOBAL, globvar)

    def _identifier_constant(self, name):
        return self._make_constant(types.LoxString(name))

    def _end_compiler(self):
        self.emit_return()
        if debug.PRINT_CODE and not errmac.errored:
            debug.disassemble(self.chunk, "code")

    def _not_synchronizable(self):
        return (
            self.current.type is not TokenType.EOF
            and self.previous.type is not TokenType.SEMICOLON
            and self.current.type not in SYNC_TOKENS
        )

    def _synchronize(self):
        errmac.panic_mode = False

        while self._not_synchronizable():
            self._advance()

    def _consume(self, token_type, message):
        if self.current.type is token_type:
            self._advance()
        else:
            self._error_at_current(message)

    def _match(self, token_type):
        if not self._check(token_type):
            return False

        self._advance()
        return True

    def _check(self, token_type):
        return self.current.type is token_type

    def _error_at_current(self, message):
        errmac.error_at(self.current, message)

    def _error(self, message):
        errmac.error_at(self.previous, message)
