## Context-free Grammar (CFG)

```ebnf
# Main Program
<procedure> ::= procedure main is <decl-seq> begin <stmt-seq> end
              | procedure main is begin <stmt-seq> end
              
# Declarations
<decl-seq> ::= <decl> <decl-seq> | ε
<decl> ::= <decl-var>
<decl-var> ::= var id ; | var id = <expr> ;

# Statements
<stmt-seq> ::= <stmt> <stmt-seq> | ε
<stmt> ::= <assign> | <if> | <loop> | <print> | <decl>
<assign> ::= id = <expr> ;
<print> ::= print ( <expr> ) ;
<if> ::= if <cond> then <stmt-seq> end
       | if <cond> then <stmt-seq> else <stmt-seq> end
<loop> ::= while <cond> do <stmt-seq> end

# Conditions and Expressions
<cond> ::= not <cond> | <cmpr> | <cmpr> and <cond> | <cmpr> or <cond>
<cmpr> ::= <expr> == <expr> | <expr> != <expr> | <expr> < <expr> | <expr> > <expr>
         | <expr> <= <expr> | <expr> >= <expr>
<expr> ::= <term> | <term> + <expr> | <term> - <expr>
<term> ::= <factor> | <factor> * <term> | <factor> / <term>
<factor> ::= id | numbers | string | (<expr>) | in()
```

## Main Parsing Process
The parsing process follows this sequence:

1. Validate program structure (`procedure main is`)
2. Parse declarations (`decl_seq`)
3. Process `begin` keyword
4. Parse statement sequence (`stmt_seq`)
5. Validate program end

## Parser Class Code Explanation

The purpose of the `Parser` class is to parse a series of tokens according to a specific grammar, 
generating meaningful outputs or raising errors if the tokens do not match the expected structure. 
Below is an explanation of each method:

### 1. `__init__`
```python
def __init__(self, tokens):
    self.tokens = tokens
    self.position = 0
```
**Explanation**:  
This constructor initializes the `Parser` class, taking a list of tokens as a parameter. `tokens` is a list containing the sequence of tokens to be parsed. `position` represents the current position of the parser, initialized to 0.

---

### 2. `current_token`
```python
def current_token(self):
    if self.position < len(self.tokens):
        return self.tokens[self.position]
    return None
```
**Explanation**:  
This method returns the current token based on the `position`. If `position` exceeds the length of the tokens, it returns `None`, indicating that there are no more tokens to parse.

---

### 3. `next_token`
```python
def next_token(self):
    self.position += 1
    if self.position < len(self.tokens):
        return self.tokens[self.position]
    return None
```
**Explanation**:  
This method moves the parsing position forward by one and returns the next token. If there are no more tokens, it returns `None`.

---

### 4. `expect_token`
```python
def expect_token(self, tokenName=None):
    token = self.current_token()
    if token is None:
        raise ParserError(f"Unexpected end of input, expected '{tokenName}'")
    
    if tokenName is not None and token.value != tokenName:
        raise ParserError(f"Expected token value '{tokenName}', got '{token.value}'")
    self.next_token()
```
**Explanation**:  
This method checks if the current token matches the expected value. If it doesn't match or if it is `None`, it raises a `ParserError`. If the token matches, it moves to the next token.

---

### 5. `match_token`
```python
def match_token(self, tokenName=None):
    token = self.current_token()
    if token is None:
        return False
    if tokenName is not None:
        if token.value != tokenName:
            return False
    return True
```
**Explanation**:  
This method checks if the current token matches the given `tokenName`. If it does, it returns `True`, otherwise it returns `False`. If no `tokenName` is provided, it simply checks if a token exists.

---

### 6. `peek_next_token`
```python
def peek_next_token(self):
    if self.position + 1 < len(self.tokens):
        return self.tokens[self.position + 1]
    return None
```
**Explanation**:  
This method returns the next token without advancing the current position. It is useful for looking ahead in the token sequence.

---

### 7. `parse`
```python
def parse(self):
    print("parse start...")
    self.expect_token("procedure")
    if not self.match_token("main"):
        raise ParserError(f"Expected 'main' after 'procedure', got '{self.current_token().value}'")
    self.expect_token("main")
    self.expect_token("is")

    print("procedure main is")

    self.decl_seq()

    self.expect_token("begin")
    print("begin")

    self.stmt_seq()

    self.expect_token("end")
    print("end")

    if self.current_token() is not None:
        raise ParserError(f"Unexpected token '{self.current_token().value}' after 'end'")
    
    print("parse end")
```
**Explanation**:  
This method is the main entry point for parsing. It expects specific tokens in a defined sequence (`procedure`, `main`, `is`, etc.). 
It calls other methods like `decl_seq` and `stmt_seq` to parse declarations and statements. 
If any token is not as expected, it raises a `ParserError`.

---

### 8. `decl_seq`
```python
def decl_seq(self):
    while self.match_token("var"):
        self.decl()
```
**Explanation**:  
This method parses a sequence of declarations. It continues to call `decl` as long as the current token is `var`.

---

### 9. `decl`
```python
def decl(self):
    self.decl_var()
```
**Explanation**:  
This method handles declarations. Currently, it calls `decl_var` to handle variable declarations.

---

### 10. `stmt_seq`
```python
def stmt_seq(self):
    while self.current_token() is not None and not self.match_token("end") and not self.match_token("else"):
        self.stmt()
```
**Explanation**:  
This method parses a sequence of statements until it encounters `end` or `else`. It calls `stmt` to parse each individual statement.

---

### 11. `decl_var`
```python
def decl_var(self):
    self.expect_token("var")
    if self.current_token() is None:
        raise ParserError("Expected identifier after 'var', but got nothing")
    var_name = self.current_token().value
    if not var_name.isidentifier():
        raise ParserError(f"Invalid identifier '{var_name}' after 'var'")
    self.next_token()

    if self.current_token().value == "=":
        self.expect_token("=")
        expr = self.expr()
        self.expect_token(";")
        print(f"var {var_name} = {expr};")
    else:
        self.expect_token(";")
        print(f"var {var_name};")
```
**Explanation**:  
This method parses a variable declaration. It expects a `var` token, followed by an identifier, and optionally an assignment (`=`) with an expression. It then expects a semicolon (`;`) to end the declaration.

---

### 12. `stmt`
```python
def stmt(self):
    token = self.current_token()
    if token.value == "var":
        self.decl()
    elif token.value == "print":
        self.print_stmt()
    elif token.value == "if":
        self.if_stmt()
    elif token.value == "while":
        self.loop()
    elif token.value.isidentifier():
        next_token = self.peek_next_token()
        if next_token and next_token.value == "=":
            self.assign()
    else:
        raise ParserError(f"Unexpected token '{token.value}' in statement")
```
**Explanation**:  
This method parses a statement. It checks the type of the current token and calls the appropriate method (`decl`, `print_stmt`, `if_stmt`, `loop`, `assign`) to handle that statement type. If the token is not recognized, it raises a `ParserError`.

---

### 13. `assign`
```python
def assign(self):
    var_name = self.current_token().value
    if not var_name.isidentifier():
        raise ParserError(f"Invalid identifier '{var_name}' in assignment")
    self.next_token()
    self.expect_token("=")
    expr = self.expr()
    self.expect_token(";")
    print(f"{var_name} = {expr};")
```
**Explanation**:  
This method handles assignment statements. It expects an identifier, followed by an equals sign (`=`) and an expression, and ends with a semicolon (`;`).

---

### 14. `print_stmt`
```python
def print_stmt(self):
    self.expect_token("print")
    self.expect_token("(")
    expr = self.expr()
    self.expect_token(")")
    self.expect_token(";")
    print(f"print({expr})")
```
**Explanation**:  
This method parses a print statement. It expects the `print` keyword, followed by an expression in parentheses, and ends with a semicolon (`;`).

---

### 15. `if_stmt`
```python
def if_stmt(self):
    self.expect_token("if")
    cond = self.cond()
    self.expect_token("then")
    print(f"if {cond} then")
    self.stmt_seq()
    if self.match_token("else"):
        self.expect_token("else")
        print("else")
        self.stmt_seq()
    self.expect_token("end")
    print("end")
```
**Explanation**:  
This method parses an `if` statement. It expects the `if` keyword, followed by a condition, and then a sequence of statements. It may also have an `else` clause, followed by another sequence of statements, and ends with `end`.

---

### 16. `loop`
```python
def loop(self):
    self.expect_token("while")
    cond = self.cond()
    self.expect_token("do")
    print(f"while {cond} do")

    self.stmt_seq()
    self.expect_token("end")
    print("end")
```
**Explanation**:  
This method parses a `while` loop. It expects the `while` keyword, followed by a condition, the `do` keyword, a sequence of statements, and ends with `end`.

---

### 17. `cond`
```python
def cond(self):
    if self.match_token("not"):
        self.expect_token("not")
        cond_expr = self.cond() 
        return f"not ({cond_expr})"
    
    left = self.cmpr()
    
    while self.match_token("or") or self.match_token("and"):
        op = self.current_token().value
        self.next_token()
        right = self.cmpr()
        left = f"({left} {op} {right})"
    
    return left
```
**Explanation**:  
This method parses a condition, which can include logical operators like `not`, `or`, and `and`. It supports parsing compound conditions by combining multiple comparisons.

---

### 18. `cmpr`
```python
def cmpr(self):
    left = self.expr()
    if self.match_token("==") or self.match_token("!=") or \
       self.match_token("<") or self.match_token(">") or \
       self.match_token("<=") or self.match_token(">="):
        op = self.current_token().value
        self.next_token()
        right = self.expr()
        return f"{left} {op} {right}"
    return left
```
**Explanation**:  
This method parses a comparison expression, such as `==`, `!=`, `<`, `>`, `<=`, or `>=`. It returns the comparison result in string format.

---

### 19. `expr`
```python
def expr(self):
    left = self.term()
    while self.match_token("+") or self.match_token("-"):
        op = self.current_token().value
        self.next_token()
        right = self.term()
        left = f"({left} {op} {right})"
    return left
```
**Explanation**:  
This method parses an arithmetic expression involving addition or subtraction. It combines terms using the `+` or `-` operators.

---

### 20. `term`
```python
def term(self):
    left = self.factor()
    while self.match_token("*") or self.match_token("/"):
        op = self.current_token().value
        self.next_token()
        right = self.factor()
        left = f"({left} {op} {right})"
    return left
```
**Explanation**:  
This method parses an arithmetic term involving multiplication or division. It combines factors using the `*` or `/` operators.

---

### 21. `factor`
```python
def factor(self):
    token = self.current_token()
    if token.value == "(":
        self.expect_token("(")
        expr = self.expr()
        self.expect_token(")")
        return f"({expr})"
    elif token.value == "in":
        self.expect_token("in")
        self.expect_token("(")
        self.expect_token(")")
        return "in()"
    elif token.value.isdigit() or (token.value.startswith('"') and token.value.endswith('"')):
        value = token.value
        self.next_token()
        return value
    else:
        identifier = token.value
        self.next_token()
        return identifier
```
**Explanation**:  
This method parses a factor, which can be a number, a string, a variable, or an expression in parentheses. It returns the value or identifier based on the current token.

---
