
# scanner.py
# COMP 141 - Phase 3.1 - Lexp scanner


import re

TOKEN_REGEX = [
    ('WHITESPACE', r'[ \t\r\n]+'),
    ('NUMBER',     r'[0-9]+'),
    ('IDENTIFIER', r'[A-Za-z][A-Za-z0-9]*'),
    ('SYMBOL',     r'[\+\-\*\/\(\)]'),
    ('UNKNOWN',    r'.')
]

_master_re = re.compile('|'.join('(?P<%s>%s)' % pair for pair in TOKEN_REGEX))

class ScannerError(Exception):
    pass

class Token:
    def __init__(self, typ, lexeme):
        self.typ = typ   # 'NUMBER', 'IDENTIFIER', 'SYMBOL'
        self.lexeme = lexeme
    def __repr__(self):
        return f"{self.lexeme} : {self.typ}"

def scan_line(s):
    """
    Tokenize a single-line expression string according to PR3.1 rules.
    Returns a list of Token objects.
    Raises ScannerError on invalid character/token.
    """
    tokens = []
    pos = 0
    while pos < len(s):
        m = _master_re.match(s, pos)
        if not m:
            raise ScannerError(f"Scanner internal error at pos {pos}")
        kind = m.lastgroup
        lex = m.group(kind)
        pos = m.end()
        if kind == 'WHITESPACE':
            continue
        if kind == 'UNKNOWN':
            raise ScannerError(f"Invalid character '{lex}' in input")
        # Normalize to the token types the rest of the project expects
        if kind == 'NUMBER':
            tokens.append(Token('NUMBER', lex))
        elif kind == 'IDENTIFIER':
            tokens.append(Token('IDENTIFIER', lex))
        elif kind == 'SYMBOL':
            tokens.append(Token('SYMBOL', lex))
    return tokens

# quick self-test when run directly
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python scanner.py \"expression\"")
        sys.exit(1)
    expr = sys.argv[1]
    try:
        toks = scan_line(expr)
        for t in toks:
            print(repr(t))
    except ScannerError as e:
        print("ScannerError:", e)
