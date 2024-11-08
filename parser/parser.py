from tokenizer.grammar import *
from .ast_node import *
from .parser_error import ParserError

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.position = 0

    def current_token(self):
        if self.position < len(self.tokens):
            return self.tokens[self.position]
        return None
    
    def next_token(self):
        self.position += 1
        if self.position < len(self.tokens):
            return self.tokens[self.position]
        return None
    
    def expect_token(self, tokenName=None):
        token = self.current_token()
        if token is None:
            raise ParserError(f"Unexpected end of input, expected '{tokenName}'")

        if tokenName is not None and token.value != tokenName:
            raise ParserError(f"Expected token '{tokenName}', got '{token.value}' on line {token.line_num}")
        self.next_token()

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
            raise ParserError(f"Expected 'main' after 'procedure', got '{self.current_token().value}' on line {self.current_token().line_num}")
        self.expect_token("main")
        self.expect_token("is")

        declarations = self.decl_seq()

        self.expect_token("begin")
        statements = self.stmt_seq()
        self.expect_token("end")

        if self.current_token() is not None:
            raise ParserError(f"Unexpected token '{self.current_token().value}' after 'end' on line {self.current_token().line_num}")
        
        print("parse end")
        return Program(declarations=declarations, statements=statements)
    
    def decl_seq(self):
        declarations = []
        while self.match_token("var"):
            declarations.append(self.decl())
        return declarations
    
    def decl(self):
        return self.decl_var()

    def decl_var(self):
        self.expect_token("var")
        token = self.current_token()
        if token is None:
            raise ParserError("Expected identifier after 'var', but got nothing")
        var_name = token.value
        if not var_name.isidentifier():
            raise ParserError(f"Invalid identifier '{var_name}' after 'var'")
        self.next_token()

        initial_value = None
        if self.match_token("="):
            self.expect_token("=")
            initial_value = self.expr()
            self.expect_token(";")
        else:
            self.expect_token(";")
        return Declaration(name=var_name, initial_value=initial_value)

    def stmt_seq(self):
        statements = []
        while self.current_token() is not None and not self.match_token("end") and not self.match_token("else"):
            statements.append(self.stmt())
        return statements

    def stmt(self):
        token = self.current_token()
        if token is None:
            raise ParserError("Unexpected end of input in statement")

        token = self.current_token()
        if token.value == "var":
            return self.decl()
        elif token.value == "print":
            return self.print_stmt()
        elif token.value == "if":
            return self.if_stmt()
        elif token.value == "while":
            return self.loop()
        elif token.value.isidentifier():
            next_token = self.peek_next_token()
            if next_token and next_token.value == "=":
                return self.assign()
        else:
            raise ParserError(f"Unexpected token '{token.value}' in statement on line {token.line_num}")

    def assign(self):
        var_name = self.current_token().value
        if not var_name.isidentifier():
            raise ParserError(f"Invalid identifier '{var_name}' in assignment")
        target = Identifier(name=var_name)
        self.next_token()
        self.expect_token("=")
        expr = self.expr()
        self.expect_token(";")
        return AssignmentStatement(target=target, value=expr)

    def print_stmt(self):
        self.expect_token("print")
        self.expect_token("(")
        expr = self.expr()
        self.expect_token(")")
        self.expect_token(";")
        return PrintStatement(expression=expr)

    def if_stmt(self):
        self.expect_token("if")
        condition = self.cond()
        self.expect_token("then")
        then_block = self.stmt_seq()
        else_block = None

        if self.match_token("else"):
            self.expect_token("else")
            else_block = self.stmt_seq()

        self.expect_token("end")
        return IfStatement(condition=condition, then_block=then_block, else_block=else_block)

    def loop(self):
        self.expect_token("while")
        condition = self.cond()
        self.expect_token("do")
        body = self.stmt_seq()
        self.expect_token("end")
        return WhileStatement(condition=condition, body=body)

    def cond(self):
        if self.match_token("not"):
            self.expect_token("not")
            cond_expr = self.cond() 
            return UnaryOperation(operator="not", operand=cond_expr)
        
        left = self.cmpr()
        
        while self.match_token("or") or self.match_token("and"):
            op = self.current_token().value
            self.next_token()
            right = self.cmpr()
            left = BinaryOperation(left=left, operator=op, right=right)
        
        return left

    def cmpr(self):
        left = self.expr()
        if self.match_token("==") or self.match_token("!=") or \
           self.match_token("<") or self.match_token(">") or \
           self.match_token("<=") or self.match_token(">="):
            op = self.current_token().value
            self.next_token()
            right = self.expr()
            return BinaryOperation(left=left, operator=op, right=right)
        return left
    

    def expr(self):
        left = self.term()
        while self.match_token("+") or self.match_token("-"):
            op = self.current_token().value
            self.next_token()
            right = self.term()
            left = BinaryOperation(left=left, operator=op, right=right)
        return left
    

    def term(self):
        left = self.factor()
        while self.match_token("*") or self.match_token("/"):
            op = self.current_token().value
            self.next_token()
            right = self.factor()
            left = BinaryOperation(left=left, operator=op, right=right)
        return left
    

    def factor(self):
        token = self.current_token()
        if token.value == "(":
            self.expect_token("(")
            expr = self.expr()
            self.expect_token(")")
            return expr
        elif token.value == "in":
            self.expect_token("in")
            self.expect_token("(")
            self.expect_token(")")
            return Input()
        elif token.value.isdigit():
            value = int(token.value)
            self.next_token()
            return Constant(value=value)
        elif token.value.startswith('"') and token.value.endswith('"'):
            value = token.value[1:-1]  # Remove quotes
            self.next_token()
            return Constant(value=value)
        else:
            identifier = token.value
            self.next_token()
            return Identifier(name=identifier)

    def print_ast(self, node, level=0, is_last=True, prefix=""):
        if node is None:
            return

        branch = "└── " if is_last else "├── "
        print(f"{prefix}{branch}{node.__class__.__name__}", end="")

        if isinstance(node, Identifier):
            print(f" ({node.name})")
        elif isinstance(node, Constant):
            print(f" ({node.value})")
        elif isinstance(node, Declaration):
            print(f" ({node.name})")
        elif isinstance(node, AssignmentStatement):
            print(f" ({node.target})")
        else:
            print()

        # prepare the prefix for children
        new_prefix = prefix + ("    " if is_last else "│   ")

        children = []
        if isinstance(node, Program):
            children.extend(node.declarations)
            children.extend(node.statements)
        elif isinstance(node, Declaration) and node.initial_value:
            children.append(node.initial_value)
        elif isinstance(node, AssignmentStatement):
            children.append(node.value)
        elif isinstance(node, PrintStatement):
            children.append(node.expression)
        elif isinstance(node, IfStatement):
            children.append(node.condition)
            children.extend(node.then_block)
            if node.else_block:
                children.extend(node.else_block)
        elif isinstance(node, WhileStatement):
            children.append(node.condition)
            children.extend(node.body)
        elif isinstance(node, BinaryOperation):
            children.append(node.left)
            children.append(node.right)
        elif isinstance(node, UnaryOperation):
            children.append(node.operand)

        # print each child
        for i, child in enumerate(children):
            self.print_ast(child, level + 1, i == len(children) - 1, new_prefix)
