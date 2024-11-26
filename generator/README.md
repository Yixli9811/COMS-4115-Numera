## Supported Operations
- `ALLOC`: Allocates space for a variable.
- `LOAD_CONST`: Loads a constant into a temporary variable.
- `LOAD`: Loads a variable’s value into a temporary variable.
- `STORE`: Stores a temporary variable’s value into a variable.
- `BINOP`: Performs a binary operation.
- `UNARY`: Performs a unary operation.
- `PRINT`: Prints a temporary variable’s value.
- `JUMP`: Unconditional jump to a label.
- `JUMP_IF_FALSE`: Conditional jump if a value is false.
- `LABEL`: Marks a position in the code.

## Translation Examples
1.	Variable Declaration: Reserves space for variables.
	- Instruction: `ALLOC variable_name`
	- Example:
		```
		var x = 10;
		```
		Translates to:
		```
		ALLOC x
		LOAD_CONST 10, t1
		STORE t1, x
		```
2. Assignment: Stores a value in a variable.
	- Instruction: `STORE temp, variable_name`
	- Example: same as above
3. Print Statement
	- Instruction: `PRINT variable_name`
	- Example:
		```
		print(x);
		```
		Translates to:
		```
		LOAD x, t1
		PRINT t1
		```
4. Arithmetic Operations
	- Instruction: `ADD temp1, temp2`
	- Example:
		```
		x = a + b;
		```
		Translates to:
		```
		LOAD a, t1
		LOAD b, t2
		ADD t1, t2
		STORE t2, x
		```
5. Conditional Statements (if-else)
	- Instruction: 
		- `JUMP_IF_FALSE condition_temp, label`
		- `JUMP label`
	- Example:
		```
		if x > 5 then
			print("Greater");
		else
			print("Smaller");
		end
		```
		Translates to:
		```
		LOAD x, t1
		LOAD_CONST 5, t2
		BINOP >, t1, t2, t3
		JUMP_IF_FALSE t3, else_label
		LOAD_CONST "Greater", t4
		PRINT t4
		JUMP end_label
		LABEL else_label
		LOAD_CONST "Smaller", t5
		PRINT t5
		LABEL end_label
		```
6. Loops (while)
	- Instruction:
		- `LABEL start_label`
		- `JUMP_IF_FALSE condition_temp, end_label`
		- `JUMP start_label`
	- Example:
		```
		while x < 10 do
			x = x + 1;
		end
		```
		Translates to:
		```
		LABEL start_label
		LOAD x, t1
		LOAD_CONST 10, t2
		BINOP <, t1, t2, t3
		JUMP_IF_FALSE t3, end_label
		LOAD x, t4
		LOAD_CONST 1, t5
		BINOP +, t4, t5, t6
		STORE t5, x
		JUMP start_label
		LABEL end_label
		```