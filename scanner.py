from enum import Enum, auto


class TokenType(Enum):
  # Single-character tokens.
  LEFT_PAREN = auto()
  RIGHT_PAREN = auto()
  LEFT_BRACE = auto()
  RIGHT_BRACE = auto()
  COMMA = auto()
  DOT = auto()
  MINUS = auto()
  PLUS = auto()
  SEMICOLON = auto()
  SLASH = auto()
  STAR = auto()
  COLON = auto()
  QUERY = auto()

  # One or two character tokens.
  BANG = auto()
  BANG_EQUAL = auto()
  EQUAL = auto()
  EQUAL_EQUAL = auto()
  GREATER = auto()
  GREATER_EQUAL = auto()
  LESS = auto()
  LESS_EQUAL = auto()
  PLUS_PLUS = auto()
  MINUS_MINUS = auto()

  # Literals.
  IDENTIFIER = auto()
  STRING = auto()
  NUMBER = auto()

  # Keywords.
  AND = auto()
  CLASS = auto()
  ELSE = auto()
  FALSE = auto()
  FUN = auto()
  FOR = auto()
  IF = auto()
  NIL = auto()
  OR = auto()
  PRINT = auto()
  RETURN = auto()
  SUPER = auto()
  THIS = auto()
  TRUE = auto()
  VAR = auto()
  WHILE = auto()
  LOOP = auto()
  BREAK = auto()

  # Specials.
  COMMENT = auto()
  ERROR = auto()
  EOF = auto()
  NEWLINE = auto()
  UNUSEFUL = auto()


LEXEMES = {
    "(": TokenType.LEFT_PAREN,
    ")": TokenType.RIGHT_PAREN,
    "{": TokenType.LEFT_BRACE,
    "}": TokenType.RIGHT_BRACE,
    ",": TokenType.COMMA,
    ".": TokenType.DOT,
    "-": TokenType.MINUS,
    "+": TokenType.PLUS,
    ";": TokenType.SEMICOLON,
    "/": TokenType.SLASH,
    "*": TokenType.STAR,
    '!': TokenType.BANG,
    '=': TokenType.EQUAL,
    ">": TokenType.GREATER,
    "<": TokenType.LESS,
    '"': TokenType.STRING,
    "?": TokenType.QUERY,
    ":": TokenType.COLON,
    " ": TokenType.UNUSEFUL,
    "++": TokenType.PLUS_PLUS,
    "--": TokenType.MINUS_MINUS,
    "!=": TokenType.BANG_EQUAL,
    "==": TokenType.EQUAL_EQUAL,
    ">=": TokenType.GREATER_EQUAL,
    "<=": TokenType.LESS_EQUAL,
    "//": TokenType.COMMENT,
    "\r": TokenType.UNUSEFUL,
    "\t": TokenType.UNUSEFUL,
    "\n": TokenType.NEWLINE
}

KEYWORDS = {
    "and": TokenType.AND,
    "class": TokenType.CLASS,
    "else": TokenType.ELSE,
    "false": TokenType.FALSE,
    "fun": TokenType.FUN,
    "for": TokenType.FOR,
    "if": TokenType.IF,
    "nil": TokenType.NIL,
    "or": TokenType.OR,
    "print": TokenType.PRINT,
    "return": TokenType.RETURN,
    "super": TokenType.SUPER,
    "this": TokenType.THIS,
    "true": TokenType.TRUE,
    "var": TokenType.VAR,
    "while": TokenType.WHILE,
    "loop": TokenType.LOOP,
    "break": TokenType.BREAK
}


class Token:
    def __init__(self, type, lexeme, line):
        self.type = type
        self.lexeme = lexeme
        self.line = line

    def __str__(self):
        return f"{self.type} {self.lexeme}"

    def __repr__(self):
        if isinstance(self.lexeme, str):
            lexeme = f'"{self.lexeme}"'
        else:
            lexeme = self.lexeme

        return (f"{self.__class__.__name__}({self.type}, {lexeme},"
            f" {self.line})")


def isidentchar(c):
    return c.isalnum() or c == "_"


class Scanner:
    def __init__(self):
        self.source = None

    def init(self, source):
        self.source = source
        self.source_len = len(source)
        self.start = 0
        self.current = 0
        self.line = 1

    def scan_token(self):
        self.start = self.current

        if self.finished():
            return self._make_token(TokenType.EOF)

        c = self._advance()
        token_type = self._get_lexeme(c)
        if token_type:
            if token_type is TokenType.COMMENT:
                self._consume_line()
            elif token_type is TokenType.NEWLINE:
                self.line += 1
            elif token_type is TokenType.STRING:
                return self._consume_string()
            elif token_type is not TokenType.UNUSEFUL:
                return self._make_token(token_type)
        elif c.isdigit():
            return self._consume_number()
        elif isidentchar(c):
            return self._consume_identifier()
        else:
            return self._error_token(f"Unexpected character {self._current_token}")

    def finished(self, *, offset=0):
        return self.current + offset >= self.source_len

    def _consume_line(self):
        while self._peek() != "\n" and not self.finished():
            self._advance()

    def _consume_string(self):
        c = self._peek()
        while c != '"':
            if self.finished():
                return self._error_token("Unterminated string.")

            if c == "\n":
                self.line += 1

            self._advance()
            c = self._peek()

        # The closing "
        self._advance()
        return self._make_token(TokenType.STRING)

    def _consume_digits(self):
        while self._peek().isdigit():
            self._advance()

    def _consume_number(self):
        self._consume_digits()

        if self._peek() == "." and self._peek_next().isdigit():
            # Go past the dot
            self._advance()
            self._consume_digits()

        return self._make_token(TokenType.NUMBER)

    def _consume_identifier(self):
        while isidentchar(self._peek()):
            self._advance()

        keyword = KEYWORDS.get(self._current_token)
        if keyword:
            return self._make_token(keyword)
        else:
            return self._make_token(TokenType.IDENTIFIER)

    def _get_lexeme(self, c):
        twochars = LEXEMES.get(c + self._peek())

        if twochars:
            self.current += 1
            return twochars
        else:
            return LEXEMES.get(c)

    def _advance(self):
        c = self.source[self.current]
        self.current += 1
        return c

    def _peek_next(self):
        if self.finished(offset=1):
            return ""
        else:
            return self.source[self.current + 1]

    def _peek(self):
        if self.finished():
            return ""
        else:
            return self.source[self.current]

    def _make_token(self, type):
        return Token(type, self._current_token, self.line)

    def _error_token(self, message):
        return Token(TokenType.ERROR, message, self.line)

    @property
    def _current_token(self):
        return self.source[self.start:self.current]
