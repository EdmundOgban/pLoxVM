from contextlib import contextmanager

from .error_machinery import ErrorMachinery
from .opcodes import *
from .scanner import TokenType
from .precedence import Precedence
from . import compiler, hashmap, pratt, scanner, types, value
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

    def emit_loop(self, loop_start):
        self.emit_byte(OP_LOOP)
        offset = self.chunk.count - loop_start + 2
        if offset > 65535:
            self._error("Loop body too large.")

        self.emit_byte((offset >> 8) & 0xFF)
        self.emit_byte(offset & 0xFF)

    def emit_jump(self, instruction):
        self.emit_byte(instruction)
        self.emit_bytes(0xFF, 0xFF)
        return self.chunk.count - 2

    def patch_jump(self, offset):
        jump = self.chunk.count - offset - 2

        if jump > 65535:
            self._error("Too much code to jump over.")

        self.chunk.code[offset] = (jump >> 8) & 0xFF
        self.chunk.code[offset + 1] = jump & 0xFF

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
        self.locals = value.Locals()
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

    def _block(self):
        while not self._check(TokenType.RIGHT_BRACE) and not self._check(TokenType.EOF):
            self._declaration()

        self._consume(TokenType.RIGHT_BRACE, "Expect '}' after block.")

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

    def _statement_if(self):
        self._consume(TokenType.LEFT_PAREN, "Expect '(' after 'if'.")
        self._expression()
        self._consume(TokenType.RIGHT_PAREN, "Expect ')' after condition.")
        then_jump = self.emit_jump(OP_JUMP_IF_FALSE)
        self.emit_byte(OP_POP)
        self._statement()
        else_jump = self.emit_jump(OP_JUMP)
        self.patch_jump(then_jump)
        self.emit_byte(OP_POP)
        if self._match(TokenType.ELSE):
            self._statement()

        self.patch_jump(else_jump)

    def _statement_while(self):
        loop_start = self.chunk.count
        self._consume(TokenType.LEFT_PAREN, "Expect '(' after 'while'.")
        self._expression()
        self._consume(TokenType.RIGHT_PAREN, "Expect ')' after condition.")
        exit_jump = self.emit_jump(OP_JUMP_IF_FALSE)
        self.emit_byte(OP_POP)
        self._statement()
        self.emit_loop(loop_start)
        self.patch_jump(exit_jump)
        self.emit_byte(OP_POP)

    def _statement_for(self):
        with self._scope():
            self._consume(TokenType.LEFT_PAREN, "Expect '(' after 'for'.")
            if self._match(TokenType.SEMICOLON):
                pass
            elif self._match(TokenType.VAR):
                self._statement_var()
            else:
                self._statement_expression()

            loop_start = self.chunk.count
            exit_jump = -1
            if not self._match(TokenType.SEMICOLON):
                self._expression()
                self._consume(TokenType.SEMICOLON, "Expect ';'.")
                exit_jump = self.emit_jump(OP_JUMP_IF_FALSE)
                self.emit_byte(OP_POP)

            if not self._match(TokenType.RIGHT_PAREN):
                body_jump = self.emit_jump(OP_JUMP)
                increment_start = self.chunk.count
                self._expression()
                self.emit_byte(OP_POP)
                self._consume(TokenType.RIGHT_PAREN, "Expect ')' after clauses.")
                self.emit_loop(loop_start)
                loop_start = increment_start
                self.patch_jump(body_jump)

            self._statement()
            self.emit_loop(loop_start)
            if exit_jump != -1:
                self.patch_jump(exit_jump)
                self.emit_byte(OP_POP)

    def _statement_print(self):
        self._expression()
        self._consume(TokenType.SEMICOLON, "Expect ';' after value.")
        self.emit_byte(OP_PRINT)

    @contextmanager
    def _scope(self):
        self.locals.scope_depth += 1
        yield
        self.locals.scope_depth -= 1
        # FIXME: Make this more pythonic
        while self.locals.count > 0 and self.locals.depth[self.locals.count - 1] > self.locals.scope_depth:
            self.emit_byte(OP_POP)
            self.locals.locals.pop()
            self.locals.count -= 1

        if self.locals.scope_depth == 0:
            self.locals.depth = []

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
        elif self._match(TokenType.IF):
            self._statement_if()
        elif self._match(TokenType.WHILE):
            self._statement_while()
        elif self._match(TokenType.FOR):
            self._statement_for()
        elif self._match(TokenType.LEFT_BRACE):
            with self._scope():
                self._block()
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
        self._named_variable(self.previous, can_assign)

    def _resolve_local(self, name):
        # FIXME: Make this more pythonic
        for i in range(self.locals.count - 1, -1, -1):
            localname = self.locals.locals[i]
            if name.length == localname.length and name.lexeme == localname.lexeme:
                if self.locals.depth[i] == -1:
                    self._error("Can't read local variable in its own initializer.")

                return i

        return -1

    def _named_variable(self, name, can_assign):
        arg = self._resolve_local(name)

        if arg != -1:
            opcode_set = OP_SET_LOCAL
            opcode_get = OP_GET_LOCAL
        else:
            arg = self._identifier_constant(name)
            opcode_set = OP_SET_GLOBAL
            opcode_get = OP_GET_GLOBAL

        if can_assign and self._match(TokenType.EQUAL):
            self._expression()
            self.emit_bytes(opcode_set, arg)
        else:
            self.emit_bytes(opcode_get, arg)

    def _and_(self, can_assign):
        end_jump = self.emit_jump(OP_JUMP_IF_FALSE)
        self.emit_byte(OP_POP)
        self._parse_precedence(Precedence.AND)
        self.patch_jump(end_jump)

    def _or_(self, can_assign):
        else_jump = self.emit_jump(OP_JUMP_IF_FALSE)
        end_jump = self.emit_jump(OP_JUMP)
        self.patch_jump(else_jump)
        self.emit_byte(OP_POP)
        self._parse_precedence(Precedence.OR)
        self.patch_jump(end_jump)

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
        self._declare_variable()
        if self.locals.scope_depth > 0:
            return 0

        return self._identifier_constant(self.previous)

    def _define_variable(self, globvar):
        if self.locals.scope_depth > 0:
            self.locals.initialize_current()
            return

        self.emit_bytes(OP_DEFINE_GLOBAL, globvar)

    def _declare_variable(self):
        if self.locals.scope_depth == 0:
            return

        name = self.previous
        for localname, depth in self.locals:
            if depth != -1 and depth < self.locals.scope_depth:
                break

            if name.length == localname.length and name.lexeme == localname.lexeme:
                self._error("Already variable with this name in this scope.")

        self.locals.add(name, uninitialized=True)

    def _identifier_constant(self, name):
        return self._make_constant(types.LoxString(name.lexeme))

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
