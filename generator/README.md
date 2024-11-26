## Supported Operations
- `ALLOC`: Allocates space for a variable.
- `LOAD_CONST`: Loads a constant into a temporary variable.
- `LOAD`: Loads a variable’s value into a temporary variable.
- `STORE`: Stores a temporary variable’s value into a variable.
- `BINOP`: Performs a binary operation.
- `UNARY`: Performs a unary operation.
- `PRINT`: Prints a temporary variable’s value.
- `INPUT`: Reads an input from the user and stores it in a temporary variable.
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
4. Input Statement
	- Instruction: `INPUT variable_name`
	- Example:
		```
		var x;
		x = in();
		```
		Translates to:
		```
		ALLOC x
		INPUT t1
		STORE t1, x
		```
5. Arithmetic Operations
	- Instruction: `BINOP operation, temp1, temp2, result_temp`
	- Example:
		```
		x = a + b;
		```
		Translates to:
		```
		LOAD a, t1
		LOAD b, t2
		BINOP +, t1, t2, t3
		STORE t3, x
		```
6. Conditional Statements (if-else)
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
		JUMP_IF_FALSE t3, else_label_1
		LOAD_CONST "Greater", t4
		PRINT t4
		JUMP end_label_1
		LABEL else_label_1
		LOAD_CONST "Smaller", t5
		PRINT t5
		LABEL end_label_1
		```
7. Loops (while)
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
		LABEL start_label_1
		LOAD x, t1
		LOAD_CONST 10, t2
		BINOP <, t1, t2, t3
		JUMP_IF_FALSE t3, end_label_1
		LOAD x, t4
		LOAD_CONST 1, t5
		BINOP +, t4, t5, t6
		STORE t6, x
		JUMP start_label_1
		LABEL end_label_1
		```