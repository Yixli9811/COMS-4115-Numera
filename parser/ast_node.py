from dataclasses import dataclass
from typing import List, Optional, Union

@dataclass
class Node:
    pass

@dataclass
class Program(Node):
    declarations: List['Declaration']
    statements: List['Statement']

@dataclass
class Declaration(Node):
    name: str
    initial_value: Optional['Expression'] = None

@dataclass
class Statement(Node):
    pass

@dataclass
class IfStatement(Statement):
    condition: 'Expression'
    then_block: List[Statement]
    else_block: Optional[List[Statement]] = None

@dataclass
class WhileStatement(Statement):
    condition: 'Expression'
    body: List[Statement]

@dataclass
class PrintStatement(Statement):
    expression: 'Expression'

@dataclass
class AssignmentStatement(Statement):
    target: 'Identifier'
    value: 'Expression'

@dataclass
class Expression(Node):
    pass

@dataclass
class BinaryOperation(Expression):
    left: Expression
    operator: str
    right: Expression

@dataclass
class UnaryOperation(Expression):
    operator: str
    operand: Expression

@dataclass
class Identifier(Expression):
    name: str

@dataclass
class Constant(Expression):
    value: Union[int, str]

@dataclass
class Input(Expression):
    pass