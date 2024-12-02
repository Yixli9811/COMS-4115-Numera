# CodeGenerator.py
import re
from parser.ast_node import *

def tokenize_instruction(instr):
    return re.findall(r'"[^"]*"|[^\s,]+', instr)

class CodeGenerator:
    def __init__(self):
        self.instructions = []
        self.temp_counter = 0
        self.start_label_counter = 0
        self.end_label_counter = 0  
        self.else_label_counter = 0
        self.var_usage = {}
        self.var_assignments = {}

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
        # optimize
        self.optimize()

    def generate_declaration(self, node):
        self.add_instruction(f"ALLOC {node.name}")
        if node.initial_value is not None:
            temp = self.generate(node.initial_value)
            self.add_instruction(f"STORE {temp}, {node.name}")
        if node.name not in self.var_assignments:
            self.var_assignments[node.name] = []
        self.var_assignments[node.name].append(len(self.instructions) - 1)

    def generate_assignment(self, node):
        temp = self.generate(node.value)
        self.add_instruction(f"STORE {temp}, {node.target.name}")
        if node.target.name not in self.var_assignments:
            self.var_assignments[node.target.name] = []
        self.var_assignments[node.target.name].append(len(self.instructions) - 1)

    def generate_print(self, node):
        temp = self.generate(node.expression)
        self.add_instruction(f"PRINT {temp}")

    def generate_if(self, node):
        if isinstance(node.condition, Constant):
            condition_val = node.condition.value
            if condition_val:
                for stmt in node.then_block:
                    self.generate(stmt)
            else:
                if node.else_block:
                    for stmt in node.else_block:
                        self.generate(stmt)
            return

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
        if isinstance(node.condition, Constant):
            condition_val = node.condition.value
            if not condition_val:
                return
            start_label = self.new_start_label()
            self.add_instruction(f"LABEL {start_label}")
            for stmt in node.body:
                self.generate(stmt)
            self.add_instruction(f"JUMP {start_label}")
            return

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
        if isinstance(node.left, Constant) and isinstance(node.right, Constant):
            left_val = node.left.value
            right_val = node.right.value
            result = self.evaluate_binop(node.operator, left_val, right_val)
            return self.generate_constant(Constant(result))
        else:
            left = self.generate(node.left)
            right = self.generate(node.right)
            temp = self.new_temp()
            self.add_instruction(f"BINOP {node.operator}, {left}, {right}, {temp}")
            return temp

    def evaluate_binop(self, operator, left, right):
        if operator == '+':
            return left + right
        elif operator == '-':
            return left - right
        elif operator == '*':
            return left * right
        elif operator == '/':
            return left / right
        elif operator == '==':
            return int(left == right)
        elif operator == '!=':
            return int(left != right)
        elif operator == '<':
            return int(left < right)
        elif operator == '<=':
            return int(left <= right)
        elif operator == '>':
            return int(left > right)
        elif operator == '>=':
            return int(left >= right)
        else:
            raise ValueError(f"unknow binop: {operator}")

    def generate_unary_operation(self, node):
        operand = self.generate(node.operand)
        temp = self.new_temp()
        self.add_instruction(f"UNARY {node.operator}, {operand}, {temp}")
        return temp

    def generate_constant(self, node):
        temp = self.new_temp()
        if isinstance(node.value, str):
            value = f'"{node.value}"'  #add ""
        else:
            value = node.value
        self.add_instruction(f"LOAD_CONST {value}, {temp}")
        return temp

    def generate_identifier(self, node):
        temp = self.new_temp()
        self.add_instruction(f"LOAD {node.name}, {temp}")
        self.var_usage[node.name] = self.var_usage.get(node.name, 0) + 1
        return temp

    def optimize(self):
        print("Optimizing...")
        to_remove = set()

        for var, assignments in self.var_assignments.items():
            usage = self.var_usage.get(var, 0)
            if usage == 0:
                to_remove.update(assignments)
                for idx, instr in enumerate(self.instructions):
                    tokens = tokenize_instruction(instr)
                    if tokens and tokens[0] == "ALLOC" and tokens[1] == var:
                        to_remove.add(idx)
            elif usage < len(assignments):
                to_remove.update(assignments[:-1])

        self.instructions = [
            instr for idx, instr in enumerate(self.instructions)
            if idx not in to_remove
        ]

        to_remove = set()
        temp_usage = self.analyze_temp_usage()

        for idx, instr in enumerate(self.instructions):
            tokens = tokenize_instruction(instr)
            if tokens and tokens[0] == "LOAD_CONST":
                _, _, temp = tokens
                if temp not in temp_usage:
                    to_remove.add(idx)

        self.instructions = [
            instr for idx, instr in enumerate(self.instructions)
            if idx not in to_remove
        ]

    def analyze_temp_usage(self):
        temp_usage = set()
        for instr in self.instructions:
            tokens = tokenize_instruction(instr)
            if len(tokens) > 1 and tokens[0] not in ["LOAD", "LOAD_CONST"]:
                for token in tokens[1:]:
                    if token.startswith("t"):
                        temp_usage.add(token)
        return temp_usage

    def get_code(self):
        return "\n".join(self.instructions)
