
GRAMMAR = {
    '<exp>': ['(<exp> <op> <exp>)', '<binary_func>(<expr>,<expr>)', '<unary_func>(<expr>)', '<var>'],
    '<op>': ['+', '-'],
    '<binary_func>': ['convolution', 'one_point', 'masked_cross'],
    '<unary_func>': ['sin', 'cos'],
    '<var>': ['x', 'y']
}

class Node:
    def __init__(self, value):
        self.value = value
        self.children = []

    def __repr__(self):
        return f"{self.value}({', '.join(map(str, self.children))})"
    

def search_operators(expression, grammar):
    level = 1
    indices = []
    for i, char in enumerate(expression):
        if char == "(":
            level += 1
        elif char == ")":
            level -= 1
        
        elif level == 1 and char in grammar["<op>"]:
            indices.append(i)
    
    return indices


def parse_expression(expression, grammar=GRAMMAR):
    expression = expression.replace(' ', '')

    if expression in grammar['<var>']:
        return Node(expression)
    
    # Search operators that are outside parenthesis
    indices = search_operators(expression, grammar)

    if indices:
        element = indices[0]
        node = Node(expression[element])

        # Split expression in left and right
        left = expression[:element]
        right = expression[element+1:]
        left_child = parse_expression(left, grammar)
        right_child = parse_expression(right, grammar)

        node.children.extend([left_child, right_child])
        return node
    
    for func in grammar['<binary_func>']:
        if expression.startswith(func + '(') and expression.endswith(')'):
            node = Node(func)
            inner_expr = expression[len(func) + 1:-1]
            
            inner_exprs = split_args(inner_expr)
            for expr in inner_exprs:
                child = parse_expression(expr, grammar)
                node.children.append(child)
            
            return node

    for func in grammar['<unary_func>']:
        if expression.startswith(func + '(') and expression.endswith(')'):
            node = Node(func)
            inner_expr = expression[len(func) + 1:-1]
            child = parse_expression(inner_expr, grammar)
            node.children.append(child)
            return node

    if expression.startswith('(') and expression.endswith(')'):
        expression = expression[1:-1]
        return parse_expression(expression)

    raise ValueError(f"Invalid expression: {expression}")

def split_args(expression):
    level = 0
    args = []
    start = 0
    for i, char in enumerate(expression):
        if char == '(':
            level += 1
        elif char == ')':
            level -= 1
        elif char == ',' and level == 0:
            args.append(expression[start:i])
            start = i + 1
    args.append(expression[start:])
    return args