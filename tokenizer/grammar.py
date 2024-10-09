from enum import Enum, auto

class TokenType(Enum):
    KEYWORD = auto()
    OPERATOR = auto()
    SEPARATOR = auto()
    LPAR = auto()
    RPAR = auto()
    IDENTIFIER = auto()
    NUMBER = auto()
    STRING = auto()

class Keyword(Enum):
    IF = "if"
    THEN = "then"
    ELSE = "else"
    WHILE = "while"
    DO = "do"
    END = "end"
    PROCEDURE = "procedure"
    VAR = "var"
    BEGIN = "begin"
    PRINT = "print"
    MAIN = "main"
    IS = "is"
    IN = "in"

class Operator(Enum):
    ASSIGN = '='
    PLUS = '+'
    MINUS = '-'
    MULTIPLY = '*'
    DIVIDE = '/'
    MODULO = '%'
    EQ = "=="
    NOT_EQ = "!="
    LE = "<="
    GE = ">="
    LT = '<'
    GT = '>'
    AND = "and"
    OR = "or"
    NOT = "not"

class Separator(Enum):
    SEMICOLON = ';'
    COMMA = ','

class Parenthesis(Enum):
    LPAR = '('
    RPAR = ')'

class String_literal(Enum):
    STRING = '"'

token_specification = {
    TokenType.KEYWORD: set([kw.value for kw in Keyword]),
    TokenType.OPERATOR: set([op.value for op in Operator]),
    TokenType.SEPARATOR: set([sep.value for sep in Separator]),
    TokenType.LPAR: {Parenthesis.LPAR.value},
    TokenType.RPAR: {Parenthesis.RPAR.value},
    TokenType.STRING: {String_literal.STRING.value}
}