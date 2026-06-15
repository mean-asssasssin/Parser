
# interpreter.py
# COMP 141 Phase 3.1 - Lexp interpreter (driver)
# Uses scanner.scan_line and parser.Parser
# Contains evaluator implementing pre-order stack reduction defined in PR3.1

import sys
from scanner import scan_line, ScannerError, Token
from parser import Parser, ParserError, Number, Identifier, Op

class EvaluatorError(Exception):
    pass

def ast_preorder_lines(node, indent=0):
    """
    Pre-order formatted lines that mimic the project example.
    operator line, then left subtree, blank line, right subtree (for grouping)
    """
    pad = '  ' * indent
    lines = []
    if isinstance(node, Op):
        lines.append(f"{pad}{node.op} : SYMBOL")
        lines.extend(ast_preorder_lines(node.left, indent+1))
        lines.append('')  # blank line to separate children as in example
        lines.extend(ast_preorder_lines(node.right, indent+1))
    elif isinstance(node, Number):
        lines.append(f"{pad}{node.value} : NUMBER")
    elif isinstance(node, Identifier):
        lines.append(f"{pad}{node.name} : IDENTIFIER")
    else:
        lines.append(f"{pad}UNKNOWN_NODE")
    return lines

def preorder_push_and_evaluate(root):
    """
    Implements the evaluator: pre-order traversal pushing operator (str) and numbers (int)
    After each push attempt to reduce top 3 items when pattern (op(str), int, int) occurs.
    Division: integer division (floor for non-negative ints). Division by zero -> error.
    Subtraction: if left < right => 0 (no negatives).
    """
    stack = []

    def apply_op(op, left, right):
        if op == '+':
            return left + right
        elif op == '*':
            return left * right
        elif op == '-':
            return 0 if left < right else left - right
        elif op == '/':
            if right == 0:
                raise EvaluatorError("Division by zero")
            return left // right
        else:
            raise EvaluatorError(f"Unknown operator '{op}'")

    def attempt_reduce():
        reduced = True
        while reduced:
            reduced = False
            if len(stack) >= 3:
                a, b, c = stack[-3], stack[-2], stack[-1]
                if isinstance(a, str) and isinstance(b, int) and isinstance(c, int):
                    stack.pop(); stack.pop(); stack.pop()
                    res = apply_op(a, b, c)
                    stack.append(res)
                    reduced = True

    def visit(node):
        if isinstance(node, Op):
            stack.append(node.op)
            attempt_reduce()
            visit(node.left)
            visit(node.right)
        elif isinstance(node, Number):
            stack.append(node.value)
            attempt_reduce()
        elif isinstance(node, Identifier):
            raise EvaluatorError(f"Identifier '{node.name}' encountered; identifiers unsupported in this phase")
        else:
            raise EvaluatorError("Unknown AST node type during evaluation")

    visit(root)
    # final reductions (in case)
    # attempt_reduce()  # attempt_reduce already called during pushes; calling again is harmless
    if len(stack) != 1 or not isinstance(stack[0], int):
        raise EvaluatorError(f"Evaluation ended with unexpected stack: {stack}")
    return stack[0]

def main(argv):
    if len(argv) != 3:
        print("Usage: python interpreter.py input.txt output.txt")
        return 1
    input_path = argv[1]
    output_path = argv[2]

    # Read input (join lines into a single expression)
    try:
        with open(input_path, 'r') as f:
            content = f.read()
    except Exception as e:
        print(f"Error opening input file: {e}")
        return 1

    expr = content.strip()
    if expr == '':
        with open(output_path, 'w') as out:
            out.write("Error: empty input\n")
        print("Empty input; wrote output file.")
        return 0

    # Prepare output content
    out_lines = []
    out_lines.append("Tokens:\n\n")

    # Scanner
    try:
        tokens = scan_line(expr)
    except ScannerError as e:
        with open(output_path, 'w') as out:
            out.write(f"Scanner Error: {e}\n")
            out.write(f"Input line: {expr}\n")
        print("Scanner error; wrote output file.")
        return 0
    except Exception as e:
        with open(output_path, 'w') as out:
            out.write(f"Scanner unexpected error: {e}\n")
            out.write(f"Input line: {expr}\n")
        print("Scanner unexpected error; wrote output file.")
        return 0

    for t in tokens:
        out_lines.append(f"{t.lexeme} : {t.typ}\n")
    out_lines.append("\nAST:\n\n")

    # Parser
    parser = Parser(tokens)
    try:
        ast = parser.parse()
    except ParserError as e:
        with open(output_path, 'w') as out:
            out.write(f"Parser Error: {e}\n")
            next_t = parser.peek()
            if next_t:
                out.write(f"Token causing error: {next_t.lexeme}\n")
            else:
                out.write("Token causing error: end of input\n")
        print("Parser error; wrote output file.")
        return 0
    except Exception as e:
        with open(output_path, 'w') as out:
            out.write(f"Parser unexpected error: {e}\n")
        print("Parser unexpected error; wrote output file.")
        return 0

    # AST formatted
    ast_lines = ast_preorder_lines(ast)
    for line in ast_lines:
        out_lines.append(line + "\n")

    # Evaluate
    out_lines.append("\nOutput: ")
    try:
        value = preorder_push_and_evaluate(ast)
        out_lines.append(str(value) + "\n")
    except EvaluatorError as e:
        with open(output_path, 'w') as out:
            out.write(f"Evaluator Error: {e}\n")
        print("Evaluator error; wrote output file.")
        return 0
    except Exception as e:
        with open(output_path, 'w') as out:
            out.write(f"Evaluator unexpected error: {e}\n")
        print("Evaluator unexpected error; wrote output file.")
        return 0

    # Write final output
    try:
        with open(output_path, 'w') as out:
            out.writelines(out_lines)
    except Exception as e:
        print(f"Cannot write output file: {e}")
        return 1

    print(f"Done. Output written to {output_path}")
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
