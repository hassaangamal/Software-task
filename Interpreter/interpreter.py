from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Union
import re

# Extended Token types
class TokenType:
    INTEGER = 'INTEGER'
    PLUS = 'PLUS'
    MINUS = 'MINUS'
    MUL = 'MUL'
    DIV = 'DIV'
    POW = 'POW'
    LPAREN = 'LPAREN'
    RPAREN = 'RPAREN'
    EOF = 'EOF'
    # New token types for regex
    REGEX = 'REGEX'
    STRING = 'STRING'
    COMMA = 'COMMA'

@dataclass
class Token:
    type: str
    value: Any

    def __str__(self) -> str:
        return f'Token({self.type}, {repr(self.value)})'

# Abstract interfaces remain the same
class ILexer(ABC):
    @abstractmethod
    def get_next_token(self) -> Token:
        
        pass

class IParser(ABC):
    @abstractmethod
    def parse(self) -> 'AST':
        pass

class IInterpreter(ABC):
    @abstractmethod
    def interpret(self) -> Any:
        pass

# Extended AST nodes
class AST(ABC):
    @abstractmethod
    def accept(self, visitor: 'INodeVisitor') -> Any:
        pass

class BinOp(AST):
    def __init__(self, left: AST, op: Token, right: AST):
        """
        Initialize a BinOp node with left subtree, operator token, and right subtree.

        :param left: The left subtree
        :param op: The operator token
        :param right: The right subtree
        """
        self.left = left
        self.token = self.op = op
        self.right = right

    def accept(self, visitor: 'INodeVisitor') -> Any:
        """
        Accept a visitor and return the result of visiting this node.

        :param visitor: The visitor to accept
        :return: The result of visiting this node
        """
        return visitor.visit_binop(self)

class Num(AST):
    def __init__(self, token: Token):
        """
        Initialize a Num node with a token.

        :param token: The token containing the value of the number
        """
        self.token = token
        self.value = token.value

    def accept(self, visitor: 'INodeVisitor') -> Any:
        
        """
        Accept a visitor and return the result of visiting this node.

        :param visitor: The visitor to accept
        :return: The result of visiting this node
        """
        return visitor.visit_num(self)

class UnaryOp(AST):
    def __init__(self, op: Token, expr: AST):
        """
        Initialize a UnaryOp node with an operator and an expression.

        :param op: The operator token
        :param expr: The expression subtree
        """
        self.token = self.op = op
        self.expr = expr

    def accept(self, visitor: 'INodeVisitor') -> Any:
        """
        Accept a visitor and return the result of visiting this node.

        :param visitor: The visitor to accept
        :return: The result of visiting this node
        """
        
        return visitor.visit_unaryop(self)

# New AST node for regex operations
class RegexOp(AST):
    def __init__(self, text: AST, pattern: AST):
        """
        Initialize a RegexOp node with a text subtree and a pattern subtree.

        :param text: The text subtree
        :param pattern: The pattern subtree
        """
        self.text = text
        self.pattern = pattern

    def accept(self, visitor: 'INodeVisitor') -> Any:
        """
        Accept a visitor and return the result of visiting this node.

        :param visitor: The visitor to accept
        :return: The result of visiting this node
        """
        return visitor.visit_regex(self)

class String(AST):
    def __init__(self, token: Token):
        """
        Initialize a String node with a token.

        :param token: The token containing the string value
        """
        self.token = token
        self.value = token.value

    def accept(self, visitor: 'INodeVisitor') -> Any:
        
        """
        Accept a visitor and return the result of visiting this node.

        :param visitor: The visitor to accept
        :return: The result of visiting this node
        """
        return visitor.visit_string(self)

# Extended Visitor interface
class INodeVisitor(ABC):
    @abstractmethod
    def visit_binop(self, node: BinOp) -> Any:
        pass

    @abstractmethod
    def visit_num(self, node: Num) -> Any:
        pass

    @abstractmethod
    def visit_unaryop(self, node: UnaryOp) -> Any:
        pass

    @abstractmethod
    def visit_regex(self, node: RegexOp) -> Any:
        pass

    @abstractmethod
    def visit_string(self, node: String) -> Any:
        pass

# Enhanced Lexer
class SimpleLexer(ILexer):
    def __init__(self, text: str):
        """
        Initialize the SimpleLexer with the input text.

        :param text: The input string to be tokenized by the lexer.
        """
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos] if text else None

    def error(self):
        raise Exception('Invalid character')

    def advance(self):
        """
        Advance the lexer to the next character in the input string.

        :return: None
        """
        self.pos += 1
        if self.pos > len(self.text) - 1:
            self.current_char = None
        else:
            self.current_char = self.text[self.pos]

    def peek(self):
        """
        Peek the next character in the input string without advancing the lexer.

        :return: The next character in the input string, or None if the end of the string has been reached.
        """
        peek_pos = self.pos + 1
        if peek_pos > len(self.text) - 1:
            return None
        return self.text[peek_pos]

    def skip_whitespace(self):
        """
        Skip whitespace characters in the input string by advancing the lexer position
        until a non-whitespace character is encountered.

        :return: None
        """
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def integer(self) -> int:
        """
        Return the integer value of the sequence of digits starting at the current
        position of the lexer.

        :return: The integer value of the sequence of digits
        """
        result = ''
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()
        return int(result)

    def string(self) -> str:
        """
        Extract a string literal from the input starting at the current position.

        The method assumes that the current character is the opening quote of the string
        literal. It advances past the opening quote, collects all characters until the
        closing quote is encountered, and advances past the closing quote.

        :return: The extracted string literal, without the surrounding quotes.
        """
        result = ''
        self.advance()  # Skip the opening quote
        while self.current_char is not None and self.current_char != '"':
            result += self.current_char
            self.advance()
        self.advance()  # Skip the closing quote
        return result

    def get_next_token(self) -> Token:
        """
        Return the next token in the input string, or Token(TokenType.EOF, None) if the end
        of the string has been reached.

        :return: The next token in the input string
        """
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char.isdigit():
                return Token(TokenType.INTEGER, self.integer())

            if self.current_char == '"':
                return Token(TokenType.STRING, self.string())

            if self.current_char == 'R' and self.peek() == 'e':
                text = ''
                while self.current_char is not None and self.current_char.isalpha():
                    text += self.current_char
                    self.advance()
                if text == 'Regex':
                    return Token(TokenType.REGEX, text)

            token_map = {
                '+': (TokenType.PLUS, '+'),
                '-': (TokenType.MINUS, '-'),
                '*': (TokenType.MUL, '*'),
                '/': (TokenType.DIV, '/'),
                '^': (TokenType.POW, '^'),
                '(': (TokenType.LPAREN, '('),
                ')': (TokenType.RPAREN, ')'),
                ',': (TokenType.COMMA, ',')
            }

            if self.current_char in token_map:
                char = self.current_char
                self.advance()
                token_type, value = token_map[char]
                return Token(token_type, value)

            self.error()

        return Token(TokenType.EOF, None)

# Enhanced Parser
class SimpleParser(IParser):
    def __init__(self, lexer: ILexer):
        """
        Initialize the SimpleParser with a lexer.

        :param lexer: The lexer instance used to tokenize the input string.
        """
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()

    def error(self):
        raise Exception('Invalid syntax')

    def eat(self, token_type: str):
        """
        Consume the current token if it matches the given token type.

        :param token_type: The token type to be matched
        :raises Exception: If the current token does not match the given token type
        """
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error()

    def factor(self) -> AST:
        """
        Parse a factor node.

        A factor can be either a unary operation, a number, a string, a regex operation, or a parenthesized expression.

        :return: The AST node representing the parsed factor
        """
        token = self.current_token
        if token.type in (TokenType.PLUS, TokenType.MINUS):
            self.eat(token.type)
            return UnaryOp(token, self.factor())
        elif token.type == TokenType.INTEGER:
            self.eat(TokenType.INTEGER)
            return Num(token)
        elif token.type == TokenType.STRING:
            self.eat(TokenType.STRING)
            return String(token)
        elif token.type == TokenType.LPAREN:
            self.eat(TokenType.LPAREN)
            node = self.expr()
            self.eat(TokenType.RPAREN)
            return node
        elif token.type == TokenType.REGEX:
            self.eat(TokenType.REGEX)
            self.eat(TokenType.LPAREN)
            text = self.expr()
            self.eat(TokenType.COMMA)
            pattern = self.expr()
            self.eat(TokenType.RPAREN)
            return RegexOp(text, pattern)
        self.error()

    def power(self) -> AST:
        """
        Parse a power node.

        A power node is a factor node that has been raised to some power by
        a unary '^' operator. This node can have multiple '^' operators
        applied to it.

        :return: The AST node representing the parsed power
        """
        node = self.factor()
        while self.current_token.type == TokenType.POW:
            token = self.current_token
            self.eat(TokenType.POW)
            node = BinOp(left=node, op=token, right=self.factor())
        return node

    def term(self) -> AST:
        """
        Parse a term node.

        A term node is a power node that has been optionally modified by
        a '*' or '/' operator. This node can have multiple '*' or '/' operators
        applied to it.

        :return: The AST node representing the parsed term
        """
        node = self.power()
        while self.current_token.type in (TokenType.MUL, TokenType.DIV):
            token = self.current_token
            self.eat(token.type)
            node = BinOp(left=node, op=token, right=self.power())
        return node

    def expr(self) -> AST:
        """
        Parse an expression node.

        An expression node is a term node that can be optionally modified by
        a '+' or '-' operator. This node can have multiple '+' or '-' operators
        applied to it.

        :return: The AST node representing the parsed expression
        """
        node = self.term()
        while self.current_token.type in (TokenType.PLUS, TokenType.MINUS):
            token = self.current_token
            self.eat(token.type)
            node = BinOp(left=node, op=token, right=self.term())
        return node

    def parse(self) -> AST:
        """
        Parse an expression node from the input string.

        The expression can be a factor node that has been optionally modified by
        a '+' or '-' operator. This node can have multiple '+' or '-' operators
        applied to it.

        :return: The AST node representing the parsed expression
        """
        node = self.expr()
        if self.current_token.type != TokenType.EOF:
            self.error()
        return node

# Enhanced Interpreter
class SimpleInterpreter(IInterpreter, INodeVisitor):
    def __init__(self, parser: IParser):
        self.parser = parser

    def visit_binop(self, node: BinOp) -> Union[int, str]:
        """
        Visit a binary operation node.

        The binary operation node is a node that represents a binary operation
        such as addition, subtraction, multiplication, division, or exponentiation.
        The node contains two children that are the left and right operands of the
        operation, and an operator token that represents the operation to
        perform.

        :param node: The binary operation node to visit
        :return: The result of the binary operation
        """
        operations = {
            TokenType.PLUS: lambda x, y: x + y,
            TokenType.MINUS: lambda x, y: x - y,
            TokenType.MUL: lambda x, y: x * y,
            TokenType.DIV: lambda x, y: x // y,
            TokenType.POW: lambda x, y: x ** y,
        }
        operation = operations.get(node.op.type)
        if operation is None:
            raise ValueError(f"Unknown operator: {node.op.type}")
        return operation(node.left.accept(self), node.right.accept(self))

    def visit_num(self, node: Num) -> int:
        """
        Visit a number node.

        This method retrieves the value of a number node in the AST.
        It simply returns the value associated with the number node.

        :param node: The number node to visit
        :return: The integer value of the number node
        """
        return node.value

    def visit_string(self, node: String) -> str:
        """
        Visit a string node.

        This method retrieves the value of a string node in the AST.
        It simply returns the value associated with the string node.

        :param node: The string node to visit
        :return: The string value of the string node
        """
        return node.value

    def visit_unaryop(self, node: UnaryOp) -> int:
        """
        Visit a unary operation node.

        This method evaluates a unary operation node in the AST.
        It supports unary plus and minus operators.

        :param node: The unary operation node to visit
        :return: The integer result of the unary operation
        :raises ValueError: If the operator is not recognized
        """
        op = node.op.type
        if op == TokenType.PLUS:
            return +node.expr.accept(self)
        elif op == TokenType.MINUS:
            return -node.expr.accept(self)
        raise ValueError(f"Unknown unary operator: {op}")

    def visit_regex(self, node: RegexOp) -> bool:
        """
        Visit a regex operation node.

        This method evaluates a regex operation node in the AST.
        It takes the left and right subtrees of the node, converts them to
        strings, and checks if the pattern matches the text.

        :param node: The regex operation node to visit
        :return: True if the pattern matches the text, False otherwise
        """
        text = str(node.text.accept(self))
        pattern = str(node.pattern.accept(self))
        return bool(re.search(pattern, text))

    def interpret(self) -> Any:
        """
        Interpret a given string as a mathematical expression.

        This method takes a string as input, tokenizes it, parses it into an
        abstract syntax tree, and then evaluates the tree to produce a result.
        The result is returned as the result of this method.

        :return: The result of interpreting the expression
        """
        tree = self.parser.parse()
        if tree is None:
            return ''
        return tree.accept(self)

# Helper functions
def create_interpreter(text: str) -> IInterpreter:
    """
    Create an interpreter instance to interpret a given string as a mathematical expression.

    This function creates a SimpleLexer instance to tokenize the input string, a
    SimpleParser instance to parse the tokens into an abstract syntax tree, and
    a SimpleInterpreter instance to evaluate the tree to produce a result.

    :param text: The input string to interpret
    :return: The interpreter instance
    """
    lexer = SimpleLexer(text)
    parser = SimpleParser(lexer)
    return SimpleInterpreter(parser)

def main():
    while True:
        try:
            text = input('spi> ')
        except EOFError:
            break
        if not text:
            continue

        interpreter = create_interpreter(text)
        try:
            result = interpreter.interpret()
            print(result)
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == '__main__':
    main()