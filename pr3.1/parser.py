
# parser.py
# COMP 141 - Phase 3.1 - Lexp parser (recursive descent)
# Exports: Parser class which takes list[Token] and parse() -> AST root
# AST node types: Number, Identifier, Op

class ParserError(Exception):
    pass

# AST nodes
class ASTNode:
    pass

class Number(ASTNode):
    def __init__(self, value):
        self.value = int(value)
    def __repr__(self):
        return f"Number({self.value})"

class Identifier(ASTNode):
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return f"Identifier({self.name})"

class Op(ASTNode):
    def __init__(self, op, left, right):
        self.op = op  # '+', '-', '*', '/'
        self.left = left
        self.right = right
    def __repr__(self):
        return f"Op({self.op}, {self.left}, {self.right})"

class Parser:
    """
    Expects tokens: list of objects with .typ and .lexeme (scanner.Token)
    Grammar:
      expression ::= term { + term }
      term ::= factor { - factor }
      factor ::= piece { / piece }
      piece ::= element { * element }
      element ::= ( expression ) | NUMBER | IDENTIFIER
    """
    def __init__(self, tokens):
        self.tokens = tokens
        self.i = 0

    def peek(self):
        return self.tokens[self.i] if self.i < len(self.tokens) else None

    def consume(self, expected_lexeme=None):
        t = self.peek()
        if t is None:
            raise ParserError("Unexpected end of input")
        if expected_lexeme is not None and t.lexeme != expected_lexeme:
            raise ParserError(f"Expected '{expected_lexeme}', found '{t.lexeme}'")
        self.i += 1
        return t

    def parse(self):
        node = self.parse_expression()
        if self.peek() is not None:
            raise ParserError(f"Unexpected token after end of expression: '{self.peek().lexeme}'")
        return node

    def parse_expression(self):
        node = self.parse_term()
        while True:
            t = self.peek()
            if t and t.typ == 'SYMBOL' and t.lexeme == '+':
                self.consume('+')
                right = self.parse_term()
                node = Op('+', node, right)
            else:
                break
        return node

    def parse_term(self):
        node = self.parse_factor()
        while True:
            t = self.peek()
            if t and t.typ == 'SYMBOL' and t.lexeme == '-':
                self.consume('-')
                right = self.parse_factor()
                node = Op('-', node, right)
            else:
                break
        return node

    def parse_factor(self):
        node = self.parse_piece()
        while True:
            t = self.peek()
            if t and t.typ == 'SYMBOL' and t.lexeme == '/':
                self.consume('/')
                right = self.parse_piece()
                node = Op('/', node, right)
            else:
                break
        return node

    def parse_piece(self):
        node = self.parse_element()
        while True:
            t = self.peek()
            if t and t.typ == 'SYMBOL' and t.lexeme == '*':
                self.consume('*')
                right = self.parse_element()
                node = Op('*', node, right)
            else:
                break
        return node

    def parse_element(self):
        t = self.peek()
        if t is None:
            raise ParserError("Unexpected end of input in element")
        if t.typ == 'SYMBOL' and t.lexeme == '(':
            self.consume('(')
            node = self.parse_expression()
            if self.peek() is None or not (self.peek().typ == 'SYMBOL' and self.peek().lexeme == ')'):
                raise ParserError("Expected closing ')'")
            self.consume(')')
            return node
        elif t.typ == 'NUMBER':
            self.consume()
            return Number(t.lexeme)
        elif t.typ == 'IDENTIFIER':
            self.consume()
            return Identifier(t.lexeme)
        else:
            raise ParserError(f"Unexpected token in element: '{t.lexeme}'")

# quick self-test when run directly
if __name__ == "__main__":
    from scanner import scan_line
    import sys
    if len(sys.argv) < 2:
        print("Usage: python parser.py \"expression\"")
        sys.exit(1)
    s = sys.argv[1]
    toks = scan_line(s)
    p = Parser(toks)
    try:
        ast = p.parse()
        print("AST:", ast)
    except ParserError as e:
        print("ParserError:", e)
