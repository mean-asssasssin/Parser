# scanner.py


import re
from dataclasses import dataclass
from typing import List

KEYWORDS = {"if", "then", "else", "endif", "while", "do", "endwhile", "skip"}
SYMBOLS = {"+", "-", "*", "/", "(", ")", ":=", ";"}

@dataclass
class Token:
    type: str   # IDENTIFIER, NUMBER, KEYWORD, SYMBOL
    value: str

    def __repr__(self):
        return f"{self.type} {self.value}"

# regular expressions for tokens
_token_spec = [
    ("NUMBER",   r"\d+"),
    ("ID",       r"[A-Za-z][A-Za-z0-9]*"),
    ("SYMBOL",   r":=|[+\-\*/\(\);]"),
    ("WS",       r"[ \t\n\r]+"),
    ("MISMATCH", r"."),
]
_token_re = re.compile("|".join(f"(?P<{n}>{p})" for n, p in _token_spec))

def tokenize(line: str) -> List[Token]:
    tokens = []
    pos = 0
    while pos < len(line):
        m = _token_re.match(line, pos)
        if not m:
            raise ValueError(f"Bad token near: {line[pos:]}")
        kind, text = m.lastgroup, m.group(m.lastgroup)
        if kind == "NUMBER":
            tokens.append(Token("NUMBER", text))
        elif kind == "ID":
            tokens.append(Token("KEYWORD", text) if text in KEYWORDS else Token("IDENTIFIER", text))
        elif kind == "SYMBOL":
            tokens.append(Token("SYMBOL", text))
        elif kind == "WS":
            pass
        else:
            raise ValueError(f"Scanner: unexpected char '{text}'")
        pos = m.end()
    return tokens
