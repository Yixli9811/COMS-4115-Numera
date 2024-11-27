
# Execute Class Interpreter

---

## Class Definition and Initialization

### 1. `__init__` Method
- **Purpose**: Initializes the interpreter.
- **Parameters**:
  - `code`: A string containing the pseudo-code.
- **Functionality**:
  - Splits the code into lines and stores them in `instructions`.
  - Initializes variable storage (`variables` and `temp_vars`).
  - Scans and stores labels (`labels`).
  - Sets the program counter (`pc`) to 0.

```python
def __init__(self, code):
    self.instructions = code.split('\n')
    self.variables = {}
    self.temp_vars = {}
    self.labels = {}
    self.pc = 0

    self._scan_labels()
```

---

### 2. `_scan_labels` Method
- **Purpose**: Scans the code for labels and stores their corresponding line numbers.
- **Workflow**:
  - Iterates over each line of code.
  - Identifies lines starting with `LABEL` and stores the label name and its position in the `labels` dictionary.

```python
def _scan_labels(self):
    for index, instruction in enumerate(self.instructions):
        parts = instruction.strip().split()
        if parts and parts[0] == 'LABEL':
            label = parts[1]
            self.labels[label] = index
```

---

## Core Execution Logic

### 3. `run` Method
- **Purpose**: Interprets and executes the code line by line.
- **Workflow**:
  1. Iterates through `instructions` using the `pc`.
  2. Skips empty lines or lines starting with `#` (comments).
  3. Uses `re` to split the instruction into parts.
  4. Identifies the opcode and calls the corresponding private method (e.g., `_execute_alloc`).
  5. Raises an error if the opcode is unrecognized.

```python
def run(self):
    while self.pc < len(self.instructions):
        instruction = self.instructions[self.pc].strip()
        if not instruction or instruction.startswith('#'):
            self.pc += 1
            continue

        parts = re.findall(r'"[^"]*"|[^\s,]+', instruction)
        opcode = parts[0]

        method_name = f'_execute_{opcode.lower()}'
        method = getattr(self, method_name, None)
        if method:
            method(parts)
        else:
            raise ValueError(f"unknown method: {opcode}")

        self.pc += 1
```

---

## Instruction Execution Methods

### 4. `_execute_alloc`
- **Purpose**: Allocates a variable and initializes it to 0.
- **Syntax**: `ALLOC var_name`

```python
def _execute_alloc(self, parts):
    var_name = parts[1]
    self.variables[var_name] = 0
```

---

### 5. `_execute_store`
- **Purpose**: Stores a value from a temporary variable into a declared variable.
- **Syntax**: `STORE temp, var_name`

```python
def _execute_store(self, parts):
    temp = parts[1]
    var_name = parts[2]
    value = self._get_value(temp)
    self.variables[var_name] = value
```

---

### 6. `_execute_print`
- **Purpose**: Prints the value of a temporary variable.
- **Syntax**: `PRINT temp`

```python
def _execute_print(self, parts):
    temp = parts[1]
    value = self._get_value(temp)
    print(value)
```

---

### 7. `_execute_jump_if_false`
- **Purpose**: Jumps to a label if a temporary variable's value is false (0 or equivalent).
- **Syntax**: `JUMP_IF_FALSE temp, label`

```python
def _execute_jump_if_false(self, parts):
    temp = parts[1]
    label = parts[2]
    value = self._get_value(temp)
    if not value:
        if label in self.labels:
            self.pc = self.labels[label]
        else:
            raise ValueError(f"unknown label: {label}")
```

---

### 8. `_execute_jump`
- **Purpose**: Jumps unconditionally to a specified label.
- **Syntax**: `JUMP label`

```python
def _execute_jump(self, parts):
    label = parts[1]
    if label in self.labels:
        self.pc = self.labels[label]
    else:
        raise ValueError(f"label not found: {label}")
```

---

### 9. `_execute_input`
- **Purpose**: Reads input from the user and stores it in a temporary variable.
- **Syntax**: `INPUT temp`

```python
def _execute_input(self, parts):
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
```

---

### 10. `_execute_binop`
- **Purpose**: Performs a binary operation (e.g., addition, subtraction) on two operands and stores the result in a temporary variable.
- **Syntax**: `BINOP operator, left, right, temp`

```python
def _execute_binop(self, parts):
    operator = parts[1]
    left = parts[2]
    right = parts[3]
    temp = parts[4]
    left_val = self._get_value(left)
    right_val = self._get_value(right)
    result = self._apply_binop(operator, left_val, right_val)
    self.temp_vars[temp] = result
```

---

## Utility Methods

### 11. `_get_value`
- **Purpose**: Retrieves the value of a variable or literal.
- **Parameters**: `operand` (can be a temporary variable, declared variable, or literal).

```python
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
```

---

## Conclusion

This interpreter demonstrates how to parse and execute a basic pseudo-code format. Each opcode corresponds to a private method responsible for executing the specific operation.
