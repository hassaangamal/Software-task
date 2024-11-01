# Calculator with Regex - Technical Documentation

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [SOLID Principles Implementation](#solid-principles)
3. [Design Patterns](#design-patterns)
4. [Component Details](#component-details)
5. [Usage Examples](#usage-examples)

## Architecture Overview

The calculator is implemented as an interpreter for mathematical expressions and regex operations. It follows a three-phase process:
1. Lexical Analysis (Tokenization)
2. Syntactic Analysis (Parsing)
3. Semantic Analysis (Interpretation)

### High-Level Architecture Diagram
![](https://i.imgur.com/704WBck.png)


## SOLID Principles

### 1. Single Responsibility Principle (SRP)
Each class has a single, well-defined responsibility:
- `SimpleLexer`: Handles only tokenization of input
- `SimpleParser`: Focuses solely on parsing tokens into AST
- `SimpleInterpreter`: Dedicated to interpreting the AST
- `Token`: Represents a single token with its type and value
- Various AST nodes (Num, BinOp, etc.): Each represents a specific type of operation

### 2. Open/Closed Principle (OCP)
**"Software entities should be open for extension but closed for modification"**

The code follows OCP through:

1. Abstract Base Classes:
```python
class ILexer(ABC):
    @abstractmethod
    def get_next_token(self) -> Token:
        pass
```

2. The AST Visitor Pattern:
```python
class AST(ABC):
    @abstractmethod
    def accept(self, visitor: 'INodeVisitor') -> Any:
        pass
```

You can extend functionality by:
- Creating new token types
- Adding new AST node types
- Implementing new visitors
- Creating new lexer/parser/interpreter implementations

without modifying existing code.

### 3. Liskov Substitution Principle (LSP)
**"Objects should be replaceable with their subtypes"**

LSP is followed through consistent interfaces:

```python
class AST(ABC):
    @abstractmethod
    def accept(self, visitor: 'INodeVisitor') -> Any:
        pass

class BinOp(AST):
    def accept(self, visitor: 'INodeVisitor') -> Any:
        return visitor.visit_binop(self)

class Num(AST):
    def accept(self, visitor: 'INodeVisitor') -> Any:
        return visitor.visit_num(self)
```

All AST nodes:
- Inherit from the same base class
- Implement the same interface
- Can be used interchangeably where an AST node is expected

### 4. Interface Segregation Principle (ISP)
**"Clients should not be forced to depend on interfaces they do not use"**

ISP is followed by separating interfaces:

```python
class ILexer(ABC):
    @abstractmethod
    def get_next_token(self) -> Token:
        pass

class IParser(ABC):
    @abstractmethod
    def parse(self) -> 'AST':
        pass

class INodeVisitor(ABC):
    @abstractmethod
    def visit_binop(self, node: BinOp) -> Any:
        pass
    # ...
```

Each interface is focused and minimal:
- `ILexer`: Only token-related methods
- `IParser`: Only parsing methods
- `INodeVisitor`: Only visitor pattern methods

### 5. Dependency Inversion Principle (DIP)
**"Depend on abstractions, not concretions"**

DIP is followed through:

1. Constructor Injection:
```python
class SimpleParser(IParser):
    def __init__(self, lexer: ILexer):  # Depends on ILexer interface
        self.lexer = lexer

class SimpleInterpreter(IInterpreter, INodeVisitor):
    def __init__(self, parser: IParser):  # Depends on IParser interface
        self.parser = parser
```

2. Abstract Base Classes:
- All major components depend on interfaces rather than concrete classes
- Components can be swapped out without affecting other parts
- Testing is easier as components can be mocked

## Design Patterns

### 1. Visitor Pattern
Primary pattern used for AST traversal and evaluation:
```python
class INodeVisitor(ABC):
    @abstractmethod
    def visit_binop(self, node: BinOp) -> Any:
        pass
    # ... other visit methods
```

Benefits:
- Separates algorithms from object structures
- makes adding new operations easier
- Maintains clean separation of concerns

### 2. Interpreter Pattern
Used for parsing and evaluating expressions:
- Grammar rules are encoded in Parser methods
- AST represents the parsed expression
- Interpreter evaluates the AST

### 3. Factory Pattern
Simple factory method used for creating interpreter instances:
```python
def create_interpreter(text: str) -> IInterpreter:
    lexer = SimpleLexer(text)
    parser = SimpleParser(lexer)
    return SimpleInterpreter(parser)
```

### 4. Composite Pattern
Used in AST structure:
- `AST` as component interface
- `BinOp`, `UnaryOp` as composites
- `Num`, `String` as leaves

## Component Details

### Lexical Analysis
The `SimpleLexer` breaks input into tokens:
- Handles arithmetic operators `(+, -, *, /, ^)`
- Recognizes parentheses
- Processes integers and strings
- Supports Regex keyword and comma separator

Example:
```python
"2 + 3" → [Token(INTEGER, 2), Token(PLUS, '+'), Token(INTEGER, 3)]
```

### Parsing
The `SimpleParser` creates an AST following operator precedence:
1. Parentheses
2. Power (^)
3. Multiplication/Division
4. Addition/Subtraction

Grammar rules:
```
expr   : term ((PLUS | MINUS) term)*
term   : power ((MUL | DIV) power)*
power  : factor (POW factor)*
factor : INTEGER | LPAREN expr RPAREN | PLUS factor | MINUS factor
       | STRING | REGEX LPAREN expr COMMA expr RPAREN
```

### Interpretation
The `SimpleInterpreter` evaluates the AST using the visitor pattern:
- Arithmetic operations return numeric results
- String operations return strings
- Regex operations return boolean results

## Usage Examples

### 1. Arithmetic Operations
```python
spi> 2 + 3 * 4
14
spi> (2 + 3) * 4
20
spi> 2 ^ 3
8
```

### 2. Regex Operations
```python
spi> Regex("hello world", "world")
True
spi> Regex("123", "\d+")
True
```


## Best Practices

1. **Error Handling**
   - Each component has specific error handling
   - Meaningful error messages
   - Graceful error recovery

2. **Type Safety**
   - Type hints throughout the code
   - Clear interface definitions
   - Runtime type checking where needed

3. **Code Organization**
   - Logical component separation
   - Clear class hierarchies
   - Consistent naming conventions
   - Added Docstring to each function 

