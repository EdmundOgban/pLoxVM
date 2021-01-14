
class LoxException(Exception):
    pass

class LoxStackOverflow(LoxException):
    pass

class LoxTooManyLocals(LoxException):
    pass
