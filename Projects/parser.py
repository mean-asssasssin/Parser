
# COMP 141 - Phase 2.1
# parser.py
#
# Usage:
#   python parser.py input.txt output.txt

import re
import sys

# ---------------------------
# Token classes / utilities
# ---------------------------

class Token:
    def __init__(self, value, typ, pos=None):
        self.value = value
        self.type = typ  # 'NUMBER', 'IDENTIFIER', 'SYMBOL'
        self.pos = pos   # optional: index in input

    def __repr__(self):
        return f"Token({self.value!r}, {self.type}, pos={self.pos})"

# ---------------------------
# Scanner
# ---------------------------

SYMBOLS = {"+", "-", "*", "/", "(", ")"}

identifier_re = re.compile(r'[A-Za-z][A-Za-z0-9]*')
number_re     = re.compile(r'[0-9]+')

def scan_line(line):
    """
    Tokenize a single line according to the scanner spec.
    Returns: list of Token objects
    On scanner error, raises ScannerError with message.
    """
    tokens = []
    i = 0
    n = len(line)

    while i < n:
        ch = line[i]

        # Skip whitespace
        if ch.isspace():
            i += 1
            continue

        # Symbol (single-character)
        if ch in SYMBOLS:
            tokens.append(Token(ch, 'SYMBOL', pos=i))
            i += 1
            continue

        # Number
        if ch.isdigit():
            m = number_re.match(line, i)
            if m:
                val = m.group(0)
                tokens.append(Token(val, 'NUMBER', pos=i))
                i = m.end()
                continue
            else:
                # shouldn't happen due to regex, but keep safe
                raise ScannerError(f"Invalid number token starting at position {i}", line)

        # Identifier
        if ch.isalpha():
            m = identifier_re.match(line, i)
            if m:
                val = m.group(0)
                tokens.append(Token(val, 'IDENTIFIER', pos=i))
                i = m.end()
                continue
            else:
                raise ScannerError(f"Invalid identifier starting at position {i}", line)

        # Anything else is a scanner error (unknown character)
        raise ScannerError(f"Invalid character '{ch}' at position {i}", line)

    return tokens

class ScannerError(Exception):
    def __init__(self, message, line):
        super().__init__(message)
        self.line = line
        self.message = message

# ---------------------------
# AST Node
# ---------------------------

class ASTNode:
    def __init__(self, value, type_, left=None, right=None):
        self.value = value      # '+' , '-' , '*' , '/' or literal value (like '3' or 'x')
        self.type = type_       # 'SYMBOL', 'NUMBER', 'IDENTIFIER'
        self.left = left
        self.right = right

# ---------------------------
# Parser (recursive descent)
# Grammar:
# expression ::= term { + term }
# term       ::= factor { - factor }
# factor     ::= piece { / piece }
# piece      ::= element { * element }
# element    ::= ( expression ) | NUMBER | IDENTIFIER
# ---------------------------

class ParserError(Exception):
    def __init__(self, message, token):
        super().__init__(message)
        self.token = token
        self.message = message

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def current(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def advance(self):
        if self.pos < len(self.tokens):
            self.pos += 1
            return True
        return False

    def match_symbol(self, sym):
        t = self.current()
        if t and t.type == 'SYMBOL' and t.value == sym:
            self.advance()
            return True
        return False

    def expect_symbol(self, sym):
        t = self.current()
        if t and t.type == 'SYMBOL' and t.value == sym:
            self.advance()
            return t
        raise ParserError(f"Expected symbol '{sym}' but found", t)

    def parse(self):
        """
        Parse starting from expression nonterminal.
        Returns AST root node.
        If unexpected tokens remain at the end, raises ParserError.
        """
        if not self.tokens:
            raise ParserError("No tokens to parse", None)
        root = self.parse_expression()
        if self.current() is not None:
            # Extra token after valid expression
            raise ParserError("Extra token after end of expression", self.current())
        return root

    # expression ::= term { + term }
    def parse_expression(self):
        node = self.parse_term()
        while True:
            t = self.current()
            if t and t.type == 'SYMBOL' and t.value == '+':
                self.advance()
                right = self.parse_term()
                node = ASTNode('+', 'SYMBOL', left=node, right=right)
            else:
                break
        return node

    # term ::= factor { - factor }
    def parse_term(self):
        node = self.parse_factor()
        while True:
            t = self.current()
            if t and t.type == 'SYMBOL' and t.value == '-':
                self.advance()
                right = self.parse_factor()
                node = ASTNode('-', 'SYMBOL', left=node, right=right)
            else:
                break
        return node

    # factor ::= piece { / piece }
    def parse_factor(self):
        node = self.parse_piece()
        while True:
            t = self.current()
            if t and t.type == 'SYMBOL' and t.value == '/':
                self.advance()
                right = self.parse_piece()
                node = ASTNode('/', 'SYMBOL', left=node, right=right)
            else:
                break
        return node

    # piece ::= element { * element }
    def parse_piece(self):
        node = self.parse_element()
        while True:
            t = self.current()
            if t and t.type == 'SYMBOL' and t.value == '*':
                self.advance()
                right = self.parse_element()
                node = ASTNode('*', 'SYMBOL', left=node, right=right)
            else:
                break
        return node

    # element ::= ( expression ) | NUMBER | IDENTIFIER
    def parse_element(self):
        t = self.current()
        if t is None:
            raise ParserError("Unexpected end of input in element", t)

        if t.type == 'SYMBOL' and t.value == '(':
            self.advance()
            node = self.parse_expression()
            # Expect closing ')'
            if not (self.current() and self.current().type == 'SYMBOL' and self.current().value == ')'):
                raise ParserError("Expected ')'", self.current())
            self.advance()  # consume ')'
            return node
        elif t.type == 'NUMBER':
            self.advance()
            return ASTNode(t.value, 'NUMBER')
        elif t.type == 'IDENTIFIER':
            self.advance()
            return ASTNode(t.value, 'IDENTIFIER')
        else:
            raise ParserError("Unexpected token in element", t)

# ---------------------------
# AST printing (preorder) with indentation
# ---------------------------

def print_ast(node, file, level=0):
    if node is None:
        return
    indent = "  " * level
    print(f"{indent}{node.value} : {node.type}", file=file)
    # preorder: print node then children
    # But to visually match example (operators followed by operands),
    # we print left subtree then right subtree with extra blank lines to separate sections in some cases.
    if node.left:
        print_ast(node.left, file, level + 1)
    if node.right:
        print_ast(node.right, file, level + 1)

# ---------------------------
# Main driver: read, scan, parse, write output
# ---------------------------

def main():
    if len(sys.argv) != 3:
        print("Usage: python parser.py input.txt output.txt")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            # The spec says input program consists of a single expression.
            # Read entire file and join lines into one input line.
            content = f.read()
    except Exception as e:
        print(f"Error reading input file: {e}")
        sys.exit(1)

    # Trim leading/trailing whitespace but preserve internal spacing for tokenization
    line = content.strip()

    # Prepare output
    try:
        out_f = open(output_path, 'w', encoding='utf-8')
    except Exception as e:
        print(f"Error opening output file: {e}")
        sys.exit(1)

    # Scan
    try:
        tokens = scan_line(line)
    except ScannerError as se:
        print("Scanner Error:", se.message, file=out_f)
        print(se.line, file=out_f)
        out_f.close()
        sys.exit(0)

    # Print tokens header
    print("Tokens:\n", file=out_f)
    for t in tokens:
        print(f"{t.value} : {t.type}", file=out_f)
    print("\nAST:\n", file=out_f)

    # Parse
    parser = Parser(tokens)
    try:
        ast_root = parser.parse()
    except ParserError as pe:
        # Print parser error and offending token (if any)
        if pe.token is None:
            print("Parser Error:", pe.message, file=out_f)
        else:
            tok = pe.token
            print(f"Parser Error: {pe.message} {tok.value} : {tok.type}", file=out_f)
        out_f.close()
        sys.exit(0)

    # Print AST (preorder with indentation)
    print_ast(ast_root, file=out_f)

    out_f.close()

if __name__ == "__main__":
    main()
