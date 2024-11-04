from tokenizer.grammar import *
from .parser_error import ParserError


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.position = 0

    def current_token(self):
        if self.position < len(self.tokens):
            return self.tokens[self.position]
        return None
    
    def next_toekn(self):
        self.position += 1
        if self.position < len(self.tokens):
            return self.tokens[self.position]
        return None
    
    def expect_token(self, tokenName=None):
        token = self.current_token()
        if token is None:
            raise ParserError(f"Unexpected end of input, expected '{tokenName}'")
    
        #print(f"Expecting token: '{tokenName}', got: {repr(token.value)}")
        
        if tokenName is not None and token.value != tokenName:
            raise ParserError(f"Expected token value '{tokenName}', got '{token.value}'")
        self.next_toekn()

    def match_token(self, tokenName=None):
        token = self.current_token()
        if token is None:
            return False
        if tokenName is not None:
            if token.value != tokenName:
                return False
        return True
    
    def peek_next_token(self):
        if self.position + 1 < len(self.tokens):
            return self.tokens[self.position + 1]
        return None
    





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
    
    def decl_seq(self):
        while self.match_token("var"):
            self.decl()
    
    def decl(self):
        self.decl_var()

    def stmt_seq(self):
        while self.current_token() is not None and not self.match_token("end") and not self.match_token("else"):
            self.stmt()

    def decl_var(self):
        self.expect_token("var")
        if self.current_token() is None:
            raise ParserError("Expected identifier after 'var', but got nothing")
        var_name = self.current_token().value
        if not var_name.isidentifier():
            raise ParserError(f"Invalid identifier '{var_name}' after 'var'")
        self.next_toekn()

        if self.current_token().value == "=":
            self.expect_token("=")
            expr = self.expr()
            self.expect_token(";")
            print(f"var {var_name} = {expr};")
        else:
            self.expect_token(";")
            print(f"var {var_name};")

    def stmt(self):
        token = self.current_token()
        #print(f"Current statement token: {token}")
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

    def assign(self):
        var_name = self.current_token().value
        if not var_name.isidentifier():
            raise ParserError(f"Invalid identifier '{var_name}' in assignment")
        self.next_toekn()
        self.expect_token("=")
        expr = self.expr()
        self.expect_token(";")
        print(f"{var_name} = {expr};")

    def print_stmt(self):
        self.expect_token("print")
        self.expect_token("(")
        expr = self.expr()
        self.expect_token(")")
        self.expect_token(";")
        print(f"print({expr})")

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

    def loop(self):
        self.expect_token("while")
        cond = self.cond()
        self.expect_token("do")
        print(f"while {cond} do")

        self.stmt_seq()
        self.expect_token("end")
        print("end")

    def cond(self):
        if self.match_token("not"):
            self.expect_token("not")
            cond_expr = self.cond() 
            return f"not ({cond_expr})"
        
        left = self.cmpr()
        
        while self.match_token("or") or self.match_token("and"):
            op = self.current_token().value
            self.next_toekn()
            right = self.cmpr()
            left = f"({left} {op} {right})"
        
        return left

    def cmpr(self):
        left = self.expr()
        if self.match_token("==") or self.match_token("!=") or \
           self.match_token("<") or self.match_token(">") or \
           self.match_token("<=") or self.match_token(">="):
            op = self.current_token().value
            self.next_toekn()
            right = self.expr()
            return f"{left} {op} {right}"
        return left
    

    def expr(self):
        left = self.term()
        while self.match_token("+") or self.match_token("-"):
            op = self.current_token().value
            self.next_toekn()
            right = self.term()
            left = f"({left} {op} {right})"
        return left
    

    def term(self):
        left = self.factor()
        while self.match_token("*") or self.match_token("/"):
            op = self.current_token().value
            self.next_toekn()
            right = self.factor()
            left = f"({left} {op} {right})"
        return left
    

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
            self.next_toekn()
            return value
        else:
            identifier = token.value
            self.next_toekn()
            return identifier
