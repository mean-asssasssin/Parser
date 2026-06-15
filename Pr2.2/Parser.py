# parser.py

import sys
from Scanner import tokenize, Token
from dataclasses import dataclass
from typing import List, Optional

# ---------- AST node types ----------
@dataclass
class Node: pass
@dataclass
class BinOp(Node): op:str; left:Node; right:Node
@dataclass
class Assign(Node): name:str; expr:Node
@dataclass
class IfNode(Node): cond:Node; then_b:Node; else_b:Node
@dataclass
class WhileNode(Node): cond:Node; body:Node
@dataclass
class Skip(Node): pass
@dataclass
class Identifier(Node): name:str
@dataclass
class Number(Node): value:str

# ---------- Parser core ----------
class ParseError(Exception):
    def __init__(self, msg, token=None): super().__init__(msg); self.token=token

class Stream:
    def __init__(self, toks:List[Token]): self.toks=toks; self.i=0
    def peek(self): return self.toks[self.i] if self.i<len(self.toks) else None
    def advance(self): 
        t=self.peek()
        if t: self.i+=1
        return t
    def expect(self, typ,val=None):
        t=self.peek()
        if not t: raise ParseError(f"Expected {typ} but found end", None)
        if t.type!=typ or (val and t.value!=val):
            raise ParseError(f"Expected {val or typ}, found {t.type} {t.value}", t)
        self.advance(); return t

# ---------- Grammar functions ----------
def parse_statement(s:Stream):
    node=parse_base(s)
    while s.peek() and s.peek().type=="SYMBOL" and s.peek().value==";":
        s.advance()
        node=BinOp(";",node,parse_base(s))
    return node

def parse_base(s:Stream):
    t=s.peek()
    if not t: raise ParseError("Unexpected end",t)
    if t.type=="IDENTIFIER":
        name=t.value; s.advance(); s.expect("SYMBOL",":=")
        return Assign(name,parse_expression(s))
    if t.type=="KEYWORD":
        if t.value=="if": return parse_if(s)
        if t.value=="while": return parse_while(s)
        if t.value=="skip": s.advance(); return Skip()
    raise ParseError("Bad base statement",t)

def parse_if(s:Stream):
    s.expect("KEYWORD","if")
    cond=parse_expression(s)
    s.expect("KEYWORD","then")
    then_b=parse_statement(s)
    s.expect("KEYWORD","else")
    else_b=parse_statement(s)
    s.expect("KEYWORD","endif")
    return IfNode(cond,then_b,else_b)

def parse_while(s:Stream):
    s.expect("KEYWORD","while")
    cond=parse_expression(s)
    s.expect("KEYWORD","do")
    body=parse_statement(s)
    s.expect("KEYWORD","endwhile")
    return WhileNode(cond,body)

# Expression hierarchy
def parse_expression(s):   # expression ::= term { + term }
    n=parse_term(s)
    while s.peek() and s.peek().type=="SYMBOL" and s.peek().value=="+":
        s.advance(); n=BinOp("+",n,parse_term(s))
    return n

def parse_term(s):         # term ::= factor { - factor }
    n=parse_factor(s)
    while s.peek() and s.peek().type=="SYMBOL" and s.peek().value=="-":
        s.advance(); n=BinOp("-",n,parse_factor(s))
    return n

def parse_factor(s):       # factor ::= piece { / piece }
    n=parse_piece(s)
    while s.peek() and s.peek().type=="SYMBOL" and s.peek().value=="/":
        s.advance(); n=BinOp("/",n,parse_piece(s))
    return n

def parse_piece(s):        # piece ::= element { * element }
    n=parse_element(s)
    while s.peek() and s.peek().type=="SYMBOL" and s.peek().value=="*":
        s.advance(); n=BinOp("*",n,parse_element(s))
    return n

def parse_element(s):      # element ::= (expr) | NUMBER | IDENTIFIER
    t=s.peek()
    if not t: raise ParseError("Missing element",t)
    if t.type=="SYMBOL" and t.value=="(":
        s.advance(); n=parse_expression(s); s.expect("SYMBOL",")"); return n
    if t.type=="NUMBER": s.advance(); return Number(t.value)
    if t.type=="IDENTIFIER": s.advance(); return Identifier(t.value)
    raise ParseError("Bad element",t)

# ---------- Printing ----------
def print_ast(node, out, ind=0):
    p="  "*ind
    if isinstance(node,BinOp):
        out.write(f"{p}SYMBOL {node.op}\n")
        print_ast(node.left,out,ind+1)
        print_ast(node.right,out,ind+1)
    elif isinstance(node,Assign):
        out.write(f"{p}SYMBOL :=\n{p}  IDENTIFIER {node.name}\n")
        print_ast(node.expr,out,ind+1)
    elif isinstance(node,IfNode):
        out.write(f"{p}IF-STATEMENT\n")
        print_ast(node.cond,out,ind+1)
        print_ast(node.then_b,out,ind+1)
        print_ast(node.else_b,out,ind+1)
    elif isinstance(node,WhileNode):
        out.write(f"{p}WHILE-LOOP\n")
        print_ast(node.cond,out,ind+1)
        print_ast(node.body,out,ind+1)
    elif isinstance(node,Skip):
        out.write(f"{p}KEYWORD skip\n")
    elif isinstance(node,Identifier):
        out.write(f"{p}IDENTIFIER {node.name}\n")
    elif isinstance(node,Number):
        out.write(f"{p}NUMBER {node.value}\n")

# ---------- Driver ----------
def main():
    if len(sys.argv)!=3:
        print("Usage: python parser.py input.txt output.txt"); sys.exit(1)
    in_f,out_f=sys.argv[1],sys.argv[2]
    try:
        text=open(in_f).read()
        toks=[]
        for line in text.splitlines():
            toks+=tokenize(line)
    except ValueError as e:
        open(out_f,"w").write("Scanner error: "+str(e)+"\n"); sys.exit(1)

    with open(out_f,"w") as o:
        o.write("Tokens:\n")
        for t in toks: o.write(f"{t.type} {t.value}\n")
        o.write("\nAST:\n")
        try:
            root=parse_statement(Stream(toks))
            print_ast(root,o)
        except ParseError as e:
            tok=f"{e.token.type} {e.token.value}" if e.token else "EOF"
            o.write(f"Parser error: {e} at {tok}\n")

if __name__=="__main__": main()
