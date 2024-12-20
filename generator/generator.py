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
        self.expr_cache = {}  # Cache for common subexpressions

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

    def get_expr_key(self, operator, operands):
        commutative_ops = {'+', '*', '==', '!=', '<=', '>=', 'and', 'or'}
        if operator in commutative_ops:
            operands = sorted(operands)
        return (operator, tuple(operands))

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
        # Optimize
        self.optimize()

    def generate_declaration(self, node):
        self.add_instruction(f"ALLOC {node.name}")
        if node.name not in self.var_assignments:
            self.var_assignments[node.name] = []
        if node.initial_value is not None:
            temp = self.generate(node.initial_value)
            self.add_instruction(f"STORE {temp}, {node.name}")
            self.var_assignments[node.name].append(len(self.instructions) - 1)
            # Invalidate expressions involving this variable
            self.invalidate_expr_cache(node.name)

    def generate_assignment(self, node):
        temp = self.generate(node.value)
        self.add_instruction(f"STORE {temp}, {node.target.name}")
        if node.target.name not in self.var_assignments:
            self.var_assignments[node.target.name] = []
        self.var_assignments[node.target.name].append(len(self.instructions) - 1)
        # Invalidate expressions involving this variable
        self.invalidate_expr_cache(node.target.name)

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
            
            expr_key = self.get_expr_key(node.operator, [left, right])
            
            if expr_key in self.expr_cache:
                return self.expr_cache[expr_key]
            else:
                temp = self.new_temp()
                self.add_instruction(f"BINOP {node.operator}, {left}, {right}, {temp}")
                self.expr_cache[expr_key] = temp
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
            raise ValueError(f"unknown binop: {operator}")

    def generate_unary_operation(self, node):
        operand = self.generate(node.operand)
        
        expr_key = self.get_expr_key(node.operator, [operand])
        
        if expr_key in self.expr_cache:
            return self.expr_cache[expr_key]
        else:
            temp = self.new_temp()
            self.add_instruction(f"UNARY {node.operator}, {operand}, {temp}")
            self.expr_cache[expr_key] = temp
            return temp

    def generate_constant(self, node):
        temp = self.new_temp()
        if isinstance(node.value, str):
            value = f'"{node.value}"' 
        else:
            value = node.value
        self.add_instruction(f"LOAD_CONST {value}, {temp}")
        return temp

    def generate_identifier(self, node):
        temp = self.new_temp()
        self.add_instruction(f"LOAD {node.name}, {temp}")
        self.var_usage[node.name] = self.var_usage.get(node.name, 0) + 1
        return temp

    def invalidate_expr_cache(self, var_name):
        keys_to_remove = []
        for expr_key, temp in self.expr_cache.items():
            operator, operands = expr_key
            for operand in operands:
                for instr in self.instructions:
                    tokens = tokenize_instruction(instr)
                    if tokens and tokens[0] == "LOAD" and tokens[1] == var_name and tokens[2] == operand:
                        keys_to_remove.append(expr_key)
                        break
        for key in keys_to_remove:
            del self.expr_cache[key]

    def optimize(self):
        print("Optimizing...")
        self.common_elimination()
        self.propagate_constants()
        self.remove_dead_code()
        self.optimize_strength_reduction()

        self.expr_cache.clear()


    def common_elimination(self):
        pass

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
        code = "\n".join(self.instructions)
        print("Generated Instructions:\n" + code) 
        return code
    

    def remove_dead_code(self):
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


    def propagate_constants(self):
        print("Performing constant propagation...")
        constant_values = {}
        temp_constant_values = {}
        new_instructions = []

        for instr in self.instructions:
            tokens = tokenize_instruction(instr)
            if not tokens:
                new_instructions.append(instr)
                continue

            op = tokens[0]

            if op == "LOAD_CONST":
                value, temp = tokens[1], tokens[2]
                if value.startswith('"') and value.endswith('"'):
                    parsed_value = value.strip('"')
                elif '.' in value:
                    parsed_value = float(value)
                else:
                    try:
                        parsed_value = int(value)
                    except ValueError:
                        parsed_value = value  
                temp_constant_values[temp] = parsed_value
                new_instructions.append(instr)
            elif op == "STORE":
                src, dest = tokens[1], tokens[2]
                if src.startswith("t") and src in temp_constant_values:
                    constant_values[dest] = temp_constant_values[src]
                elif src.startswith('"') and src.endswith('"'):
                    constant_values[dest] = src.strip('"')
                else:
                    constant_values.pop(dest, None)
                new_instructions.append(instr)
            elif op == "BINOP":
                operator, left, right, dest = tokens[1], tokens[2], tokens[3], tokens[4]
                left_val = None
                right_val = None

                if left.startswith("t") and left in temp_constant_values:
                    left_val = temp_constant_values[left]
                elif left.startswith('"') and left.endswith('"'):
                    left_val = left.strip('"')
                else:
                    try:
                        left_val = int(left)
                    except ValueError:
                        try:
                            left_val = float(left)
                        except ValueError:
                            pass

                if right.startswith("t") and right in temp_constant_values:
                    right_val = temp_constant_values[right]
                elif right.startswith('"') and right.endswith('"'):
                    right_val = right.strip('"')
                else:
                    try:
                        right_val = int(right)
                    except ValueError:
                        try:
                            right_val = float(right)
                        except ValueError:
                            pass

                if left_val is not None and right_val is not None:
                    result = self.evaluate_binop(operator, left_val, right_val)
                    new_instr = f"LOAD_CONST {result}, {dest}"
                    new_instructions.append(new_instr)
                    temp_constant_values[dest] = result
                else:
                    temp_constant_values.pop(dest, None)
                    new_instructions.append(instr)
            elif op == "UNARY":
                operator, operand, dest = tokens[1], tokens[2], tokens[3]
                operand_val = None

                if operand.startswith("t") and operand in temp_constant_values:
                    operand_val = temp_constant_values[operand]
                elif operand.startswith('"') and operand.endswith('"'):
                    operand_val = operand.strip('"')
                else:
                    try:
                        operand_val = int(operand)
                    except ValueError:
                        try:
                            operand_val = float(operand)
                        except ValueError:
                            pass

                if operand_val is not None:
                    result = self.evaluate_unop(operator, operand_val)
                    new_instr = f"LOAD_CONST {result}, {dest}"
                    new_instructions.append(new_instr)
                    temp_constant_values[dest] = result
                else:
                    temp_constant_values.pop(dest, None)
                    new_instructions.append(instr)
            elif op == "LOAD":
                var, temp = tokens[1], tokens[2]
                if var in constant_values:
                    const_value = constant_values[var]
                    if isinstance(const_value, str):
                        const_value = f'"{const_value}"'  # Ensure strings are quoted
                    new_instr = f"LOAD_CONST {const_value}, {temp}"
                    new_instructions.append(new_instr)
                    temp_constant_values[temp] = const_value
                else:
                    new_instructions.append(instr)
                    temp_constant_values.pop(temp, None)
            elif op == "JUMP_IF_FALSE":
                condition, label = tokens[1], tokens[2]
                cond_val = None

                if condition.startswith("t") and condition in temp_constant_values:
                    cond_val = temp_constant_values[condition]
                elif condition.startswith('"') and condition.endswith('"'):
                    cond_val = condition.strip('"')
                else:
                    try:
                        cond_val = int(condition)
                    except ValueError:
                        try:
                            cond_val = float(condition)
                        except ValueError:
                            pass

                if cond_val is not None:
                    if not cond_val:
                        new_instr = f"JUMP {label}"
                        new_instructions.append(new_instr)
                    else:
                        pass 
                else:
                    new_instructions.append(instr)
            elif op == "JUMP":
                new_instructions.append(instr)
            elif op == "LABEL":
                new_instructions.append(instr)
                constant_values = {}
                temp_constant_values = {}
            elif op == "PRINT":
                new_instructions.append(instr)
            elif op == "INPUT":
                new_instructions.append(instr)
            elif op == "ALLOC":
                new_instructions.append(instr)
            else:
                new_instructions.append(instr)

        self.instructions = new_instructions
        self.constant_values = constant_values

    def evaluate_unop(self, operator, operand):
        if operator == '-':
            return -operand
        elif operator == '!':
            return int(not operand)
        elif operator == 'not': 
            return int(not operand)
        else:
            raise ValueError(f"Unknown unary operator: {operator}")

    def optimize_strength_reduction(self):
        print("Performing strength reduction optimizations...")
        optimized_instructions = []
        for instr in self.instructions:
            tokens = tokenize_instruction(instr)
            if tokens and tokens[0] == "BINOP" and tokens[1] == "*":
                x = tokens[2]
                n = tokens[3]
                dest = tokens[4]
                if self.is_power_of_two(n):
                    shift_amount = int(math.log2(int(n)))
                    # change with shift left
                    new_instr = f"SHIFT_LEFT {x}, {shift_amount}, {dest}"
                    optimized_instructions.append(new_instr)
                    continue 
            optimized_instructions.append(instr)
        self.instructions = optimized_instructions

    def is_power_of_two(self, n):
        try:
            num = int(n)
            return num > 0 and (num & (num - 1)) == 0
        except ValueError:
            return False
        
    
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
        code = "\n".join(self.instructions)
        return code
    
