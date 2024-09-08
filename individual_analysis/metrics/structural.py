
import math

from auxiliars.tree import Node
from collections import Counter, deque
from subtree_characteristics import subtree_sizes

def compute_path_lengths(tree: Node):
    """
    Compute all path lengths from the root.
    """

    if not tree:
        return []

    queue: deque = deque([(tree, 0)])
    path_lengths: list = []

    while queue:
        node, path_length = queue.popleft()

        if not node.children:
            # Node is a terminal
            path_lengths.append(path_length)
        
        else:
            for child in node.children:
                queue.append((child, path_length + 1))
    
    return path_lengths


def tree_edit_distance(tree1: Node, tree2: Node) -> int:
    """
    Compare tree1 against tree2.
    """

    # Base cases
    if not tree1 and not tree2:
        return 0
    
    if not tree1:
        return sum(tree_edit_distance(None, child) for child in tree2.children) + 1
    
    if not tree2:
        return sum(tree_edit_distance(child, None) for child in tree1.children) + 1
    
    # Cost for substituting current nodparse_expressiones
    cost_substitution: int = 0 if tree1.value == tree2.value else 1

    # Initialize the DP table
    dp = [[0] * (len(tree2.children) + 1) for _ in range(len(tree1.children) + 1)]

    # Fill in the first row and column of the DP table (deletion/insertion)
    for i in range(1, len(tree1.children) + 1):
        dp[i][0] = dp[i-1][0] + tree_edit_distance(tree1.children[i-1], None)
    
    for j in range(1, len(tree2.children) + 1):
        dp[0][j] = dp[0][j-1] + tree_edit_distance(None, tree2.children[j-1])

    # Fill in the DP table
    for i in range(1, len(tree1.children) + 1):
        for j in range(1, len(tree2.children) + 1):
            cost_delete = dp[i-1][j] + tree_edit_distance(tree1.children[i-1], None)
            cost_insert = dp[i][j-1] + tree_edit_distance(None, tree2.children[j-1])
            cost_match = dp[i-1][j-1] + tree_edit_distance(tree1.children[i-1], tree2.children[j-1])
            dp[i][j] = min(cost_delete, cost_insert, cost_match)
    
    # Total cost includes the substitution of root nodes plus the edit distance of their subtrees
    return cost_substitution + dp[-1][-1]


def structural_entropy(tree: Node, kind: str = "subtree_sizes") -> float:
    """
    Calculate the structural entropy of a tree based on subtree sizes.
    """

    if kind == "subtree_sizes":
        sizes = subtree_sizes(tree)

    total_size = sum(sizes)

    # Calculate the probability of each subtree size
    size_counts = Counter(sizes)
    probabilities = [count / total_size for count in size_counts.values()]

    # Compute entropy
    entropy: float = - sum(p * math.log(p, 2) for p in probabilities)
    return entropy


def compute_balance_skewness(node: Node) -> tuple[int, int, int, int, int, int]:
    """
    Compute the balance and skewness of a tree.
    """
    if not node or not node.children:
        #(depth, abs_balance, abs_skweness, dir_balance, dir_skewness, count)
        return 0, 0, 0, 0, 0, 1
    
    # Initialize values

    left_depth, left_count = 0, 0
    left_balance = [0, 0] # (absolute, directional)
    left_skewness = [0, 0] # (absolute, directional)
    
    right_depth, right_count = 0, 0
    right_balance = [0, 0] # (absolute, directional)
    right_skewness = [0, 0] # (absolute, directional)

    # Assign left and right
    if len(node.children) > 0:
        left_depth, left_balance[0], left_skewness[0], left_balance[1], left_skewness[1], left_count = compute_balance_skewness(node.children[0])
    if len(node.children) > 1:
        right_depth, right_balance[0], right_skewness[0], right_balance[1], right_skewness[1], right_count = compute_balance_skewness(node.children[1])
    
    # Calculate depth of the current node
    depth: int = 1 + max(left_depth, right_depth)

    # Calculate absolute and directional balance
    abs_balance: int = abs(left_depth - right_depth)
    dir_balance: int = right_depth - left_depth # Positive if right is deeper, else negative.

    # Calculate absolute and directional skewness
    abs_skewness: int = abs(left_count - right_count)
    dir_skewness: int = right_count - left_count # Positive if right has more nodes, else negative.

    # Aggregate values
    total_abs_balance: int = abs_balance + left_balance[0] + right_balance[0]
    total_abs_skewness: int = abs_skewness + left_skewness[0] + right_skewness[0]

    # Count total nodes including the current node
    total_count: int = left_count + right_count + 1

    # Pass upward the directional metrics; no need to accumulate since they are contextual
    return depth, total_abs_balance, total_abs_skewness, dir_balance, dir_skewness, total_count

#if __name__ == "__main__":
#    from tree_parser import parse_expression

#    exp = "masked_cross(one_point(x,cos(cos(y))), one_point(x,y) + cos(x))"
#    tree = parse_expression(exp)

#    print(compute_balance_skewness(tree))
