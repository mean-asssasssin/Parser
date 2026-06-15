COMP 141 – Phase 3.1
Lexp Interpreter
---------------------------------------

This project implements the scanner, parser, and evaluator for the Lexp
expression language described in the Phase 3.1 specification. The project
is written in Python and is separated into modules as required:

    scanner.py     – tokenizes the input string into NUMBER / IDENTIFIER / SYMBOL
    parser.py      – builds an Abstract Syntax Tree (AST) according to the grammar
    interpreter.py – main driver; imports scanner & parser and performs evaluation
    test_input.txt – example input expression

The evaluator uses the pre-order, stack-based evaluation algorithm specified
in the assignment. Subtraction that results in a negative number returns 0, and
division is integer division. Division by zero produces an evaluator error.


---------------------------------------
REQUIREMENTS
---------------------------------------

• Python 3.8 or newer
• All files must be in the same folder:
      scanner.py
      parser.py
      interpreter.py
      test_input.txt

No additional libraries or modules are required.


---------------------------------------
HOW TO RUN
---------------------------------------

Open a terminal or command prompt and navigate to the folder containing all
project files. Example:

    cd C:\Users\YourName\Desktop\lexp_project

Run the interpreter using:

    python interpreter.py test_input.txt test_output.txt

This command takes:

    argument 1 → input file containing a single Lexp expression
    argument 2 → output file to write tokens, AST, and final value

The interpreter will:

1. Read the input expression from test_input.txt
2. Run the scanner to produce tokens
3. Run the parser to build the AST
4. Evaluate the AST using the required pre-order stack algorithm
5. Write the following to test_output.txt:
       - Tokens
       - AST (pre-order format)
       - Final evaluated result
       - Or an error message if scanner/parser/evaluator fails


---------------------------------------
ERROR HANDLING
---------------------------------------

The program follows project specifications:

• Scanner errors:
      Writes “Scanner Error: …” and the input line, then stops.

• Parser errors:
      Writes “Parser Error: …” and the token causing the error, then stops.

• Evaluator errors:
      Writes “Evaluator Error: …” (e.g., division by zero), then stops.


---------------------------------------
TESTING
---------------------------------------

A complex test expression is provided in test_input.txt:

    12*(3+4/2-5)+100/(3*2)-(7-10/3*2)+8*(2+3*(4-1))

More test expressions may be added as long as they contain only valid Lexp
tokens and follow the specification.


---------------------------------------
END OF README
---------------------------------------
