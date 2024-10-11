# COMS-4115-Numera

## Lexical Grammar
- Keywords = `if | then | else | while | do | end | procedure | var | begin | print | main | is | in`
- Identifiers = `[a-zA-Z][a-zA-Z0-9_]*`
- Operators = `== | != | <= | >= | = | + | - | * | / | % | < | > | and | or | not`
- Numbers = `Integer | Float` Integer = `0 | [1-9][0-9]*`  Float = `[0-9]+\.[0-9]* | \.[0-9]+`
- LPAR = `(`, RPAR = `)`
- Separator = `; | ,`
- String = `"[^"]"` (accept any chactacter except " within the double quote)
- Whitespace = `[\t\n\r]+`

Team:
* Yixuan Li (yl3803)
* Meng Gao (mg4774)

## Lexer Usage Guide

Prerequisite 
    - Docker must already be installed on the system.

1. clone repository
```
git clone https://github.com/Yixli9811/COMS-4115-Numera.git 
cd COMS-4115-Numera
```

2. Build a Docker image
```
docker build -t coms-4115-numera .
```
- make sure docker daemon is running (docker desktop is open)

3. Run the Docker container    
    we provide 5 files to test our program and one error file to show error report  
    (test_file.txt,test_file2.txt,test_file3.txt,test_file4.txt,test_file5.txt) (test_file_error.txt)
```
docker run -p 4000:80 coms-4115-numera python3 main.py test/test_file.txt
```

## Lexer code description
1. Define Operators and Symbols  
```
sorted_operators = sorted([op for op in token_specification[TokenType.OPERATOR] if not op.isalpha()],
                           key=lambda x: -len(x))
symbols = token_specification[TokenType.SEPARATOR] | token_specification[TokenType.LPAR] | \
          token_specification[TokenType.RPAR]
```
`sorted()` is used to sort non-alphabetic operators in descending order by length to ensure that longer operators are matched first, avoiding ambiguity.     

2. Keywords, Identifiers, and Logical Operators: Concatenate characters to form words and check if they are keywords or identifiers.
```
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
```
3. Operators: Match longer operators first.   
```
elif c in token_specification[TokenType.OPERATOR]:
    for op in sorted_operators:
        if input_string.startswith(op, i):
            tokens.append(Token(TokenType.OPERATOR, op, i))
            i += len(op)
            break
```
4. Symbols: Handle separators, left parentheses, right parentheses, etc.   
```
elif c in symbols:
    if c in token_specification[TokenType.SEPARATOR]:
        tokens.append(Token(TokenType.SEPARATOR, c, i))
    elif c in token_specification[TokenType.LPAR]:
        tokens.append(Token(TokenType.LPAR, c, i))
    else:
        tokens.append(Token(TokenType.RPAR, c, i))
    i += 1
```
5. Numbers: Handle integers and floating-point numbers, while checking for invalid identifiers.   
```
elif c.isdigit():
    num = ''
    seen_dot = False
    while i < len(input_string) and (input_string[i].isdigit() or
                                     (input_string[i] == '.' and not seen_dot)):
        if input_string[i] == '.':
            seen_dot = True
        num += input_string[i]
        i += 1

    if i < len(input_string) and (input_string[i].isalpha() or input_string[i] == '_'):
        while i < len(input_string) and (input_string[i].isalnum() or input_string[i] == '_'):
            i += 1
        invalid_identifier = input_string[start:i]
        raise ValueError(f"Invalid identifier starting with digit: '{invalid_identifier}' "
                         f"at line {line_num} position {start}")
    tokens.append(Token(TokenType.NUMBER, line_num, start))
```
6. Unrecognized Characters: Throw an error.   
```
else:
    raise ValueError(f"Unrecognized character at line {line_num}, position {i}: {c}")
```



