from collections import namedtuple

from .scanner import TokenType
from .compiler import Precedence


ParseRule = namedtuple("ParseRule", ["prefix", "infix", "precedence"])


def number(inst):
   return inst._number()


def unary(inst):
   return inst._unary()


def grouping(inst):
   return inst._grouping()


def binary(inst):
   return inst._binary()


def literal(inst):
   return inst._literal()


RULES = {
    TokenType.LEFT_PAREN: ParseRule(grouping, None, None),
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
    TokenType.BANG: ParseRule(None, None, Precedence.NONE),
    TokenType.BANG_EQUAL: ParseRule(None, None, Precedence.NONE),
    TokenType.EQUAL: ParseRule(None, None, Precedence.NONE),
    TokenType.EQUAL_EQUAL: ParseRule(None, None, Precedence.NONE),
    TokenType.GREATER: ParseRule(None, None, Precedence.NONE),
    TokenType.GREATER_EQUAL: ParseRule(None, None, Precedence.NONE),
    TokenType.LESS: ParseRule(None, None, Precedence.NONE),
    TokenType.LESS_EQUAL: ParseRule(None, None, Precedence.NONE),
    TokenType.PLUS_PLUS: ParseRule(None, None, Precedence.NONE),
    TokenType.MINUS_MINUS: ParseRule(None, None, Precedence.NONE),
    TokenType.IDENTIFIER: ParseRule(None, None, Precedence.NONE),
    TokenType.STRING: ParseRule(None, None, Precedence.NONE),
    TokenType.NUMBER: ParseRule(number, None, None),
    TokenType.AND: ParseRule(None, None, Precedence.NONE),
    TokenType.CLASS: ParseRule(None, None, Precedence.NONE),
    TokenType.ELSE: ParseRule(None, None, Precedence.NONE),
    TokenType.FALSE: ParseRule(literal, None, None),
    TokenType.FUN: ParseRule(None, None, Precedence.NONE),
    TokenType.FOR: ParseRule(None, None, Precedence.NONE),
    TokenType.IF: ParseRule(None, None, Precedence.NONE),
    TokenType.NIL: ParseRule(literal, None, None),
    TokenType.OR: ParseRule(None, None, Precedence.NONE),
    TokenType.PRINT: ParseRule(None, None, Precedence.NONE),
    TokenType.RETURN: ParseRule(None, None, Precedence.NONE),
    TokenType.SUPER: ParseRule(None, None, Precedence.NONE),
    TokenType.THIS: ParseRule(None, None, Precedence.NONE),
    TokenType.TRUE: ParseRule(literal, None, None),
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
