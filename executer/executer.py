import re

class Execute:
    def __init__(self, code):
        self.instructions = code.split('\n')
        self.variables = {}
        self.temp_vars = {}
        self.labels = {}
        self.pc = 0

        self._scan_labels()

    def _scan_labels(self):
        for index, instruction in enumerate(self.instructions):
            parts = instruction.strip().split()
            if parts and parts[0] == 'LABEL':
                label = parts[1]
                self.labels[label] = index

    def run(self):
        while self.pc < len(self.instructions):
            instruction = self.instructions[self.pc].strip()
            if not instruction or instruction.startswith('#'):
                self.pc += 1
                continue

            # parts = instruction.split()
            parts = re.findall(r'"[^"]*"|[^\s,]+', instruction)
            #print(parts)
            opcode = parts[0]

            method_name = f'_execute_{opcode.lower()}'
            method = getattr(self, method_name, None)
            if method:
                method(parts)
            else:
                raise ValueError(f"unkown method: {opcode}")

            self.pc += 1

    def _execute_alloc(self, parts):
        # ALLOC var_name
        var_name = parts[1]
        self.variables[var_name] = 0

    def _execute_store(self, parts):
        # STORE temp, var_name
        temp = parts[1]
        var_name = parts[2]
        value = self._get_value(temp)
        self.variables[var_name] = value

    def _execute_print(self, parts):
        # PRINT temp
        temp = parts[1]
        value = self._get_value(temp)
        print(value)

    def _execute_jump_if_false(self, parts):
        # JUMP_IF_FALSE temp, label
        temp = parts[1]
        label = parts[2]
        value = self._get_value(temp)
        if not value:
            if label in self.labels:
                self.pc = self.labels[label]
            else:
                raise ValueError(f"unknow label: {label}")

    def _execute_jump(self, parts):
        # JUMP label
        label = parts[1]
        if label in self.labels:
            self.pc = self.labels[label]
        else:
            raise ValueError(f"label not found: {label}")

    def _execute_label(self, parts):
        pass

    def _execute_input(self, parts):
        # INPUT temp
        temp = parts[1]
        user_input = input()
        try:
            value = int(user_input)
        except ValueError:
            try:
                value = float(user_input)
            except ValueError:
                value = user_input
        self.temp_vars[temp] = value

    def _execute_binop(self, parts):
        # BINOP operator, left, right, temp
        operator = parts[1]
        left = parts[2]
        right = parts[3]
        temp = parts[4]
        left_val = self._get_value(left)
        right_val = self._get_value(right)
        result = self._apply_binop(operator, left_val, right_val)
        self.temp_vars[temp] = result

    def _execute_unary(self, parts):
        # UNARY operator, operand, temp
        operator = parts[1]
        operand = parts[2]
        temp = parts[3]
        operand_val = self._get_value(operand)
        result = self._apply_unary(operator, operand_val)
        self.temp_vars[temp] = result

    def _execute_load_const(self, parts):
        # LOAD_CONST value, temp
        value = parts[1].strip('"')
        temp = parts[2]
        if value.isdigit():
            value = int(value)
        else:
            try:
                value = float(value)
            except ValueError:
                pass
        self.temp_vars[temp] = value

    def _execute_load(self, parts):
        # LOAD var_name, temp
        var_name = parts[1]
        temp = parts[2]
        if var_name in self.variables:
            self.temp_vars[temp] = self.variables[var_name]
        else:
            raise ValueError(f"var not declared: {var_name}")

    def _get_value(self, operand):
        if operand.startswith('t'):
            if operand in self.temp_vars:
                return self.temp_vars[operand]
            else:
                raise ValueError(f"operand not declared: {operand}")
        elif operand in self.variables:
            return self.variables[operand]
        else:
            try:
                if '.' in operand:
                    return float(operand)
                else:
                    return int(operand)
            except ValueError:
                return operand

    def _apply_binop(self, operator, left, right):
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
            raise ValueError(f"unknow bunop op: {operator}")

    def _apply_unary(self, operator, operand):
        if operator == '-':
            return -operand
        elif operator == '!':
            return int(not operand)
        elif operator == 'not':
            return int(not operand)
        else:
            raise ValueError(f"unkonw unary op: {operator}")
