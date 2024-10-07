from .grammar import *
from .token import Token

def scan(filename):
    print("scanner start...")
    tokens = []

    sorted_operators = sorted([op for op in token_specification[TokenType.OPERATOR] if not op.isalpha()],
                       key=lambda x: -len(x))
    symbols = token_specification[TokenType.SEPARATOR] | token_specification[TokenType.LPAR] | \
                token_specification[TokenType.RPAR]
    
    with (open(filename, 'r', encoding='utf-8') as file):
        for num, line in enumerate(file):
            input_string = line.strip()
            i = 0
            while i < len(input_string):
                c = input_string[i]
                start = i

                # ignore whitespace
                if c.isspace():
                    i += 1
                    continue

                # keyword or identifier or operator (and, not, or) state
                elif c.isalpha() or c == '_':
                    word = ""
                    while i < len(input_string) and (input_string[i].isalnum() or input_string[i] == '_'):
                        word += input_string[i]
                        i += 1

                    if word in token_specification[TokenType.KEYWORD]:
                        tokens.append(Token(TokenType.KEYWORD, word, start))
                    elif word in token_specification[TokenType.OPERATOR]:
                        tokens.append(Token(TokenType.OPERATOR, word, start))
                    else:
                        tokens.append(Token(TokenType.IDENTIFIER, word, start))

                # operator (everything other than and, or, not) state
                elif c in token_specification[TokenType.OPERATOR]:
                    for op in sorted_operators:
                        if input_string.startswith(op, i):
                            tokens.append(Token(TokenType.OPERATOR, op, i))
                            i += len(op)
                            break

                # symbol (separator, lpar and rpar) state
                elif c in symbols:
                    if c in token_specification[TokenType.SEPARATOR]:
                        tokens.append(Token(TokenType.SEPARATOR, c, i))
                    elif c in token_specification[TokenType.LPAR]:
                        tokens.append(Token(TokenType.LPAR, c, i))
                    else:
                        tokens.append(Token(TokenType.RPAR, c, i))
                    i += 1

                # number state
                elif c.isdigit():
                    num = ''
                    seen_dot = False
                    while i < len(input_string) and (input_string[i].isdigit() or
                                                     (input_string[i] == '.' and not seen_dot)):
                        if input_string[i] == '.':
                            seen_dot = True
                        num += input_string[i]
                        i += 1
                    tokens.append(Token(TokenType.NUMBER, num, start))

                # error state
                else:
                    num = str(int(num) + 1)
                    raise ValueError(f"Unrecognized character at line {num}, position {i}: {c}")
    print("scanner end")
    return tokens