
def scan(filename):
    print("scanner start")
    token_specification = [
        ('KEYWORD', ['if', 'then', 'else', 'while', 'do', 'end', 'procedure', 'var', 'begin', 'print']),
        ('OPERATOR', ['=','+', '-', '*', '/', '==', '!=', '<=', '>=', '<', '>', 'and', 'or', 'not']),
        ('SEPARATOR', [';']),
        ('LPAR', ['(']),
        ('RPAR', [')'])
    ]
    
    tokens = []
    
    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            input_string = line.strip()
            i = 0
            while i < len(input_string):
                # ignore whitespace
                if input_string[i].isspace():
                    i += 1
                    continue

                matched = False

                # Keyword
                for token_type, values in token_specification:
                    if token_type == 'KEYWORD':
                        for keyword in values:
                            if input_string[i:i+len(keyword)] == keyword and (i+len(keyword) == len(input_string) or not input_string[i+len(keyword)].isalnum()):
                                tokens.append((token_type, keyword))
                                i += len(keyword)
                                matched = True
                                break
                        if matched:
                            break

                # Operator
                if not matched:
                    for operator in token_specification[1][1]:
                        if input_string[i:i+len(operator)] == operator:
                            tokens.append(('OPERATOR', operator))
                            i += len(operator)
                            matched = True
                            break

                # Symbol
                if not matched:
                    for token_type, values in token_specification[2:]:
                        if input_string[i] in values:
                            tokens.append((token_type, input_string[i]))
                            i += 1
                            matched = True
                            break

                # Integer
                if not matched and input_string[i].isdigit():
                    num = ''
                    while i < len(input_string) and (input_string[i].isdigit() or input_string[i] == '.'):
                        num += input_string[i]
                        i += 1
                    tokens.append(('NUMBER', num))
                    matched = True

                # Id
                if not matched and input_string[i].isalpha():
                    identifier = ''
                    while i < len(input_string) and (input_string[i].isalnum()):
                        identifier += input_string[i]
                        i += 1
                    tokens.append(('IDENTIFIER', identifier))
                    matched = True

                # No found
                if not matched:
                    raise ValueError(f"Unrecognized character: {input_string[i]}")
    
    return tokens