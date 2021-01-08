from collections import namedtuple

from .scanner import TokenType
from .compiler import Precedence


ParseRule = namedtuple("ParseRule", ["prefix", "infix", "precedence"])


def binary(inst, can_assign):
   return inst._binary(can_assign)


def grouping(inst, can_assign):
   return inst._grouping(can_assign)


def literal(inst, can_assign):
   return inst._literal(can_assign)


def number(inst, can_assign):
   return inst._number(can_assign)


def string(inst, can_assign):
   return inst._string(can_assign)


def unary(inst, can_assign):
   return inst._unary(can_assign)


def variable(inst, can_assign):
   return inst._variable(can_assign)


RULES = {
    TokenType.LEFT_PAREN: ParseRule(grouping, None, Precedence.NONE),
    TokenType.RIGHT_PAREN: ParseRule(None, None, Precedence.NONE),
    TokenType.LEFT_BRACE: ParseRule(None, None, Precedence.NONE),
    TokenType.RIGHT_BRACE: ParseRule(None, None, Precedence.NONE),
    TokenType.COMMA: ParseRule(None, None, Precedence.NONE),
    TokenType.DOT: ParseRule(None, None, Precedence.NONE),
    TokenType.MINUS: ParseRule(unary, binary, Precedence.TERM),
    TokenType.PLUS: ParseRule(None, binary, Precedence.TERM),
    TokenType.SEMICOLON: ParseRule(None, None, Precedence.NONE),
    TokenType.SLASH: ParseRule(None, binary, Precedence.FACTOR),
    TokenType.STAR: ParseRule(None, binary, Precedence.FACTOR),
    TokenType.COLON: ParseRule(None, None, Precedence.NONE),
    TokenType.QUERY: ParseRule(None, None, Precedence.NONE),
    TokenType.BANG: ParseRule(unary, None, Precedence.NONE),
    TokenType.BANG_EQUAL: ParseRule(None, binary, Precedence.EQUALITY),
    TokenType.EQUAL: ParseRule(None, None, Precedence.NONE),
    TokenType.EQUAL_EQUAL: ParseRule(None, binary, Precedence.EQUALITY),
    TokenType.GREATER: ParseRule(None, binary, Precedence.COMPARISON),
    TokenType.GREATER_EQUAL: ParseRule(None, binary, Precedence.COMPARISON),
    TokenType.LESS: ParseRule(None, binary, Precedence.COMPARISON),
    TokenType.LESS_EQUAL: ParseRule(None, binary, Precedence.COMPARISON),
    TokenType.PLUS_PLUS: ParseRule(None, None, Precedence.NONE),
    TokenType.MINUS_MINUS: ParseRule(None, None, Precedence.NONE),
    TokenType.IDENTIFIER: ParseRule(variable, None, Precedence.NONE),
    TokenType.STRING: ParseRule(string, None, Precedence.NONE),
    TokenType.NUMBER: ParseRule(number, None, Precedence.NONE),
    TokenType.AND: ParseRule(None, None, Precedence.NONE),
    TokenType.CLASS: ParseRule(None, None, Precedence.NONE),
    TokenType.ELSE: ParseRule(None, None, Precedence.NONE),
    TokenType.FALSE: ParseRule(literal, None, Precedence.NONE),
    TokenType.FUN: ParseRule(None, None, Precedence.NONE),
    TokenType.FOR: ParseRule(None, None, Precedence.NONE),
    TokenType.IF: ParseRule(None, None, Precedence.NONE),
    TokenType.NIL: ParseRule(literal, None, Precedence.NONE),
    TokenType.OR: ParseRule(None, None, Precedence.NONE),
    TokenType.PRINT: ParseRule(None, None, Precedence.NONE),
    TokenType.RETURN: ParseRule(None, None, Precedence.NONE),
    TokenType.SUPER: ParseRule(None, None, Precedence.NONE),
    TokenType.THIS: ParseRule(None, None, Precedence.NONE),
    TokenType.TRUE: ParseRule(literal, None, Precedence.NONE),
    TokenType.VAR: ParseRule(None, None, Precedence.NONE),
    TokenType.WHILE: ParseRule(None, None, Precedence.NONE),
    TokenType.LOOP: ParseRule(None, None, Precedence.NONE),
    TokenType.BREAK: ParseRule(None, None, Precedence.NONE),
    TokenType.COMMENT: ParseRule(None, None, Precedence.NONE),
    TokenType.ERROR: ParseRule(None, None, Precedence.NONE),
    TokenType.EOF: ParseRule(None, None, Precedence.NONE),
    TokenType.NEWLINE: ParseRule(None, None, Precedence.NONE),
    TokenType.UNUSEFUL: ParseRule(None, None, Precedence.NONE),
}
