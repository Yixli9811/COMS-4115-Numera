from parser.ast_node import *

class CodeGenerator:
    def __init__(self):
        self.instructions = []
        self.temp_counter = 0
        self.start_label_counter = 0
        self.end_label_counter = 0  
        self.else_label_counter = 0

    def new_temp(self):
        self.temp_counter += 1
        return f"t{self.temp_counter}"

    def new_start_label(self):
        self.start_label_counter += 1
        return f"start_label_{self.start_label_counter}"

    def new_end_label(self):
        self.end_label_counter += 1
        return f"end_label_{self.end_label_counter}"

    def new_else_label(self):
        self.else_label_counter += 1
        return f"else_label_{self.else_label_counter}"

    def add_instruction(self, instruction):
        self.instructions.append(instruction)

    def generate(self, node):
        if isinstance(node, Program):
            self.generate_program(node)
        elif isinstance(node, Declaration):
            self.generate_declaration(node)
        elif isinstance(node, AssignmentStatement):
            self.generate_assignment(node)
        elif isinstance(node, PrintStatement):
            self.generate_print(node)
        elif isinstance(node, IfStatement):
            self.generate_if(node)
        elif isinstance(node, WhileStatement):
            self.generate_while(node)
        elif isinstance(node, Input):
            return self.generate_input(node)
        elif isinstance(node, BinaryOperation):
            return self.generate_binary_operation(node)
        elif isinstance(node, UnaryOperation):
            return self.generate_unary_operation(node)
        elif isinstance(node, Constant):
            return self.generate_constant(node)
        elif isinstance(node, Identifier):
            return self.generate_identifier(node)
        else:
            raise ValueError(f"Unknown AST node type: {type(node)}")

    def generate_program(self, node):
        for decl in node.declarations:
            self.generate(decl)
        for stmt in node.statements:
            self.generate(stmt)

    def generate_declaration(self, node):
        self.add_instruction(f"ALLOC {node.name}")
        if node.initial_value is not None:
            temp = self.generate(node.initial_value)
            self.add_instruction(f"STORE {temp}, {node.name}")

    def generate_assignment(self, node):
        temp = self.generate(node.value)
        self.add_instruction(f"STORE {temp}, {node.target.name}")

    def generate_print(self, node):
        temp = self.generate(node.expression)
        self.add_instruction(f"PRINT {temp}")

    def generate_if(self, node):
        condition_temp = self.generate(node.condition)
        else_label = self.new_else_label()

        self.add_instruction(f"JUMP_IF_FALSE {condition_temp}, {else_label}")

        for stmt in node.then_block:
            self.generate(stmt)

        if node.else_block:
            end_label = self.new_end_label()
            self.add_instruction(f"JUMP {end_label}")
            self.add_instruction(f"LABEL {else_label}")

            for stmt in node.else_block:
                self.generate(stmt)

            self.add_instruction(f"LABEL {end_label}")
        else:
            self.add_instruction(f"LABEL {else_label}")

    def generate_while(self, node):
        start_label = self.new_start_label()
        end_label = self.new_end_label()

        self.add_instruction(f"LABEL {start_label}")
        condition_temp = self.generate(node.condition)
        self.add_instruction(f"JUMP_IF_FALSE {condition_temp}, {end_label}")

        for stmt in node.body:
            self.generate(stmt)

        self.add_instruction(f"JUMP {start_label}")
        self.add_instruction(f"LABEL {end_label}")

    def generate_input(self, node):
        temp = self.new_temp()
        self.add_instruction(f"INPUT {temp}")
        return temp

    def generate_binary_operation(self, node):
        left = self.generate(node.left)
        right = self.generate(node.right)
        temp = self.new_temp()
        self.add_instruction(f"BINOP {node.operator}, {left}, {right}, {temp}")
        return temp

    def generate_unary_operation(self, node):
        operand = self.generate(node.operand)
        temp = self.new_temp()
        self.add_instruction(f"UNARY {node.operator}, {operand}, {temp}")
        return temp

    def generate_constant(self, node):
        temp = self.new_temp()
        self.add_instruction(f"LOAD_CONST {node.value}, {temp}")
        return temp

    def generate_identifier(self, node):
        temp = self.new_temp()
        self.add_instruction(f"LOAD {node.name}, {temp}")
        return temp

    def get_code(self):
        return "\n".join(self.instructions)