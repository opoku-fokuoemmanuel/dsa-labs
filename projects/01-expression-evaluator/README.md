# 🧮 Expression Evaluator

A fully functional mathematical expression evaluator built from scratch — no `eval()`, no shortcuts. Just a clean compiler pipeline implemented in Python.

```
"2.5 + 3 * (4 - 1)"  →  11.5
"2 ^ 3"              →  8.0
"10 / 2"             →  5.0
".5 + 1.5"           →  2.0
```

---

## Pipeline

```
Raw String
    ↓
[Tokenizer]          →  ['2.5', '+', '3', '*', '(', '4', '-', '1', ')']
    ↓
[PostfixConverter]   →  ['2.5', '3', '4', '1', '-', '*', '+']   (Shunting-Yard)
    ↓
[ExpressionTree]     →  builds a binary tree from the postfix tokens
    ↓
[Evaluator]          →  recursively evaluates the tree → 11.5
```

This is the same pipeline used in real language interpreters and compilers. The only difference is that real ones have more token types (strings, booleans, keywords) and more complex AST nodes.

---

## How it works

### Stage 1 — Tokenizer
Walks the raw string character by character, grouping digits into numbers, catching decimals, handling implicit multiplication like `2(x+1)` → `2 * (x+1)`, and rejecting malformed input with descriptive errors.

### Stage 2 — Shunting-Yard Algorithm (Postfix Conversion)
Converts infix notation (the way humans write math) into postfix notation (the way machines evaluate it cleanly). Uses a stack to manage operator precedence and associativity — `^` is right-associative, everything else is left-associative.

Infix:   `2 + 3 * 4`
Postfix: `2 3 4 * +`

The key insight: in postfix, you never need parentheses. Precedence is baked into the order.

### Stage 3 — Expression Tree
Builds a binary tree from the postfix tokens. Operands become leaf nodes. Operators become internal nodes with a left and right child. The tree structure encodes the evaluation order perfectly.

```
        +
       / \
     2.5   *
           / \
          3   -
             / \
            4   1
```

### Stage 4 — Evaluator
Recursively walks the tree. Leaf nodes return their numeric value. Internal nodes apply their operator to the results of their left and right subtrees. Clean, simple, elegant.

---

## Supported

- Integer and float operands (`3`, `2.5`, `.5`)
- Operators: `+`, `-`, `*`, `/`, `^`
- Parentheses with proper precedence
- Implicit multiplication: `2(3+1)` → `2 * (3+1)`
- Descriptive error messages for invalid input

## Planned
- Variable support: define `a=2, b=3` then evaluate `a*b+1`
- Unary minus: `-3 + 5`
- Functions: `sqrt(9)`, `sin(0)`

---

## Run it

```bash
git clone https://github.com/opoku-fokuoemmanuel/dsa-labs
cd dsa-labs/projects/expression-evaluator
python expression_evaluator.py
```

No dependencies — standard library only.

---

## DSA concepts used

| Concept | Where |
|---------|-------|
| Stack | Shunting-Yard operator management |
| Binary Tree | Expression Tree structure |
| Recursion | Tree traversal in the Evaluator |
| String Parsing | Tokenizer |

---

*Part of the [dsa-labs](https://github.com/opoku-fokuoemmanuel/dsa-labs) marathon.*
