from collections import deque


# === HELPERS ===
def is_operand_token(token):
    """Check if a token is a number or variable name."""
    if not token:
        return False
    if token.isalpha():  # variable like 'a', 'b', 'abc'
        return True
    # numeric: optional leading digits, one optional dot
    return (token[0].isdigit() or token[0] == '.') and token.count('.') <= 1 and token.replace('.', '').isdigit()


# === 1. TOKENIZER ===
class Tokenizer:
    def __init__(self, expression):
        self.expression = expression
        self.operations = set(['+', '-', '*', '/', '^', '**'])
        self.parentheses = set(['(', ')'])
        self.tokens = []
        self.char = ''
        self.parenthesis_count = 0

    def _last_token_is_operand(self):
        return self.tokens and is_operand_token(self.tokens[-1])

    def tokenize(self):
        if not self.expression:
            raise ValueError("Empty Expression")

        i = 0
        while i < len(self.expression):
            ele = self.expression[i]

            # skip spaces 
            if ele == ' ':
                i += 1
                continue

            # check for ** before 
            if i + 1 < len(self.expression) and self.expression[i:i+2] == '**':
                if self.char:
                    self.tokens.append(self.char)
                    self.char = ''
                if not self._last_token_is_operand() and (not self.tokens or self.tokens[-1] != ')'):
                    raise ValueError("Invalid placement of operator '**'")
                self.tokens.append('**')
                i += 2
                continue

            # 
            if ele.isalnum() or ele == '.':
                if ele == '.':
                    if '.' in self.char:
                        raise ValueError(f"Invalid number format at '{self.char + ele}'")
                    if not self.char:
                        self.char = '0.'
                    else:
                        self.char += ele
                else:
                    self.char += ele

            #
            elif ele in self.operations or ele in self.parentheses:
                if self.char:
                    self.tokens.append(self.char)
                    self.char = ''

                if ele in self.operations:
    
                    if self._last_token_is_operand() or (self.tokens and self.tokens[-1] == ')'):
                        self.tokens.append(ele)
                    elif not self.tokens or self.tokens[-1] == '(' or self.tokens[-1] in self.operations:
                        raise ValueError(f"Invalid placement of operator '{ele}'")
                    else:
                        self.tokens.append(ele)

                elif ele == '(':
                    self.parenthesis_count += 1
                    if not self.tokens:
                        self.tokens.append(ele)
                    elif self._last_token_is_operand():
                        self.tokens.append('*')
                        self.tokens.append(ele)
                    elif self.tokens[-1] in self.operations or self.tokens[-1] == '(':
                        self.tokens.append(ele)
                    else:
                        self.tokens.append(ele)

                else: 
                    self.parenthesis_count -= 1
                    if self.parenthesis_count < 0:
                        raise ValueError(f"Invalid placement of parenthesis '{ele}'")
                    if not self.tokens:
                        raise ValueError(f"Invalid placement of parenthesis '{ele}'")
                    if self.tokens[-1] in self.operations:
                        raise ValueError(f"Operator '{self.tokens[-1]}' has no right operand before ')'")
                    if self.tokens[-1] == '(':
                        raise ValueError("Empty parentheses '()' are not allowed")
                    self.tokens.append(ele)

            else:
                raise ValueError(f"Invalid character '{ele}' in expression")

            i += 1

        if self.parenthesis_count != 0:
            raise ValueError("Unbalanced parentheses")
        if self.char:
            self.tokens.append(self.char)

        result = self.tokens.copy()
    
        self.tokens = []
        self.char = ''
        self.parenthesis_count = 0
        return result


# 2. POSTFIX CONVERTER (Shunting-Yard) 
class PostfixConverter:
    def __init__(self, tokens):
        self.tokens = tokens
        self.precedence = {'**': 4, '^': 3, '*': 2, '/': 2, '+': 1, '-': 1}
        self.associativity = {
            '**': 'right', '^': 'right',
            '*': 'left', '/': 'left',
            '+': 'left', '-': 'left'
        }
        self.operations = set(self.precedence.keys())

    def is_operand(self, token):
        return is_operand_token(token)

    def is_operator(self, token):
        return token in self.operations

    def convert_to_postfix(self):
        output = []
        stack = deque()

        for token in self.tokens:
            if self.is_operand(token):
                output.append(token)

            elif token == '(':
                stack.append(token)

            elif token == ')':
                while stack and stack[-1] != '(':
                    output.append(stack.pop())
                if not stack:
                    raise ValueError("Mismatched closing parenthesis")
                stack.pop()  

            elif self.is_operator(token):
                while (stack and
                       stack[-1] != '(' and
                       self.is_operator(stack[-1]) and
                       (self.precedence[stack[-1]] > self.precedence[token] or
                        (self.precedence[stack[-1]] == self.precedence[token] and
                         self.associativity[token] == 'left'))):
                    output.append(stack.pop())
                stack.append(token)

        while stack:
            top = stack.pop()
            if top == '(':
                raise ValueError("Mismatched opening parenthesis")
            output.append(top)

        return output


# 3. EXPRESSION TREE
class Node:
    def __init__(self, data, left=None, right=None):
        self.data = data
        self.left = left
        self.right = right

    def is_leaf(self):
        """A leaf node is an operand (number or variable)."""
        return self.left is None and self.right is None


class ExpressionTree:
    def __init__(self, postfix):
        self.postfix = postfix
        self.root = None

    def build_tree(self):
        stack = deque()
        for token in self.postfix:
            if is_operand_token(token):
                stack.append(Node(token))
            else:
                if len(stack) < 2:
                    raise ValueError(f"Not enough operands for operator '{token}'")
                right = stack.pop()
                left = stack.pop()
                stack.append(Node(token, left, right))

        if not stack:
            raise ValueError("Empty expression tree")
        self.root = stack.pop()

        if stack:
            raise ValueError("Too many operands — malformed expression")

        return self.root


# 4. EVALUATOR 
class Evaluator:
    def __init__(self, tree, variables=None):
        self.root = tree.root
        
        self.variables = variables or {}

    def evaluate(self):
        return self._eval(self.root)

    def _eval(self, node):
        if node.is_leaf():
            
            try:
                return float(node.data)
            except ValueError:
                if node.data in self.variables:
                    return float(self.variables[node.data])
                raise ValueError(f"Undefined variable: '{node.data}'")

        left_val = self._eval(node.left)
        right_val = self._eval(node.right)

        op = node.data
        if op == '+':  return left_val + right_val
        if op == '-':  return left_val - right_val
        if op == '*':  return left_val * right_val
        if op == '/':
            if right_val == 0:
                raise ZeroDivisionError("Division by zero")
            return left_val / right_val
        if op in ('^', '**'):  return left_val ** right_val

        raise ValueError(f"Unknown operator: '{op}'")


# 5. CALCULATOR 
class Calculator:
    def calculate(self, expression, variables=None):
        """
        Evaluate a mathematical expression string.

        Args:
            expression: e.g. "2.5 + 3 * (4 - 1)"
            variables:  optional dict e.g. {'a': 2, 'b': 3}

        Returns:
            float result, or an error string if something went wrong.
        """
        try:
            tokens = Tokenizer(expression).tokenize()
            postfix = PostfixConverter(tokens).convert_to_postfix()
            tree = ExpressionTree(postfix)
            tree.build_tree()
            result = Evaluator(tree, variables).evaluate()
            return result
        except (ValueError, ZeroDivisionError, IndexError) as e:
            return f"Error: {e}"


# === TESTS ===
if __name__ == "__main__":
    calc = Calculator()

    tests = [
        ("2.5 + 3 * (4 - 1)",   11.5),   # basic precedence
        ("10 / 2",               5.0),   # division
        (".5 + 1.5",             2.0),   # leading decimal
        ("2 ^ 3",                8.0),   # caret exponent
        ("2 ** 3",               8.0),   # Python-style exponent
        ("(2 + 3) * (4 - 1)",   15.0),   # nested parens
        ("2 ** 3 ** 2",        512.0),   # right-associativity: 2^(3^2) = 2^9
        ("10 / 0",            "Error"),  # division by zero
        ("",                  "Error"),  # empty expression
    ]

    print("=== Expression Evaluator Tests ===\n")
    all_passed = True
    for expr, expected in tests:
        result = calc.calculate(expr)
        if isinstance(expected, float):
            passed = isinstance(result, float) and abs(result - expected) < 1e-9
        else:
            passed = isinstance(result, str) and result.startswith("Error")
        status = "✅" if passed else "❌"
        if not passed:
            all_passed = False
        print(f"{status}  {repr(expr):<30}  →  {result}  (expected {expected})")

    print(f"\n{'All tests passed!' if all_passed else 'Some tests failed.'}")

    # Variable support demo
    print("\n=== Variable Support ===\n")
    result = calc.calculate("a + b * 2", variables={'a': 3, 'b': 4})
    print(f"a=3, b=4 → 'a + b * 2' = {result}")  # → 11.0
