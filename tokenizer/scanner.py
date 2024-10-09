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
        for line_num, line in enumerate(file):
            line_num = str(int(line_num) + 1)
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
                elif c.isalpha():
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

                # String literal state
                elif c in token_specification[TokenType.STRING]:
                    if c == '"':
                        word = ''
                        #tokens.append(Token(TokenType.Str_lit, '"', start))
                        i += 1 
                        start = i
                        
                        while i < len(input_string) and input_string[i] != '"':
                            word += input_string[i]
                            i += 1
                        
                        if i >= len(input_string) or input_string[i] != '"':
                            raise ValueError(f"Unterminated string literal at line {line_num} position {start}")
                        
                        i += 1
                        tokens.append(Token(TokenType.STRING, word, start))
                        #tokens.append(Token(TokenType.Str_lit, '"', start))


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

                    # check for invalid identifier starting with a digit
                    if i < len(input_string) and (input_string[i].isalpha() or input_string[i] == '_'):
                        while i < len(input_string) and (input_string[i].isalnum() or input_string[i] == '_'):
                            i += 1
                        invalid_identifier = input_string[start:i]
                        raise ValueError(f"Invalid identifier starting with digit: '{invalid_identifier}' "
                                         f"at line {line_num} position {start}")
                    tokens.append(Token(TokenType.NUMBER, line_num, start))

                # error state
                else:
                    raise ValueError(f"Unrecognized character at line {line_num}, position {i}: {c}")
    print("scanner end")
    return tokens