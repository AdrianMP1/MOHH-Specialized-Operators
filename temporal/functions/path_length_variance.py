
from collections import deque
from parser import Node, parse_expression

def calculate_path_lengths(root: Node):
    """
    Compute all path lengths from the root.    
    """

    if not root:
        return []
    
    queue: deque = deque([(root, 0)])
    path_lengths: list = []

    while queue:
        node, path_length = queue.popleft()

        if not node.children:
            # If node is a terminal...
            path_lengths.append(path_length)
        
        else:
            for child in node.children:
                queue.append((child, path_length + 1))
    
    return path_lengths


def path_length_variance(path_lengths: list) -> float:
    """
    Compute the variance of the given path lengths
    """

    if not path_lengths:
        return 0
    
    num_paths: int = len(path_lengths)
    
    mean_length: float = sum(path_lengths) / num_paths
    variance: float = sum((length - mean_length) ** 2 for length in path_lengths) / num_paths
    
    return variance


def compute_path_length_variance(trees: list):
    """
    From a population, compute the variance of their path lengths.
    """

    variances = []

    for tree in trees:
        path_lengths = calculate_path_lengths(tree)
        variance = path_length_variance(path_lengths)

        variances.append(variance)

    return variances

if __name__ == "__main__":
    exp1 = "masked_cross(cos(x) + sin(y), cos(x) + sin(y))"
    exp2 = "(x+(x+(x+(x+(x+(x))))))"
    exp3 = "one_point(cos(x) + y)"
    
    trees = [parse_expression(exp1), parse_expression(exp2), parse_expression(exp3)]

    compute_path_length_variance(trees)