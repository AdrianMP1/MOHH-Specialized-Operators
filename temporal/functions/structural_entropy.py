
# A highly balanced and symmetric tree will have lower 
# entropy compared to a highly imblanced or skewed tree

# Node-Based Entropy: Calculate the frequency of each type of node
# (or subtree pattern) and apply the entropy formula using the frequencies.

# Path-Based Entropy: Consider the path lengths from the root to each leaf
# and evaluate how uniformly distributed these lengths are.
import math
from collections import Counter

from parser import Node, parse_expression

def calculate_subtree_sizes(node):
    """
    Recursively calculate the size of each subtree rooted at the given node.
    Returns a list of subtree sizes including the current node.
    """

    if node is None:
        return []
    
    sizes = [1] # Count the current node

    for child in node.children:
        subtree_sizes = calculate_subtree_sizes(child)
        sizes.extend(subtree_sizes)
        sizes[0] += subtree_sizes[0]
    
    #sizes[0] += sum(sizes[1:]) # Add sizes of all subtrees rooted at children

    return sizes

def structural_entropy(tree):
    """
    Calculate the structural entropy of a tree based on subtree sizes.
    """

    subtree_sizes = calculate_subtree_sizes(tree)
    total_size = sum(subtree_sizes)

    # Calculate the probability of each subtree size
    size_counts = Counter(subtree_sizes)
    probabilities = [count / total_size for count in size_counts.values()]

    # Compute entropy
    entropy = - sum(p * math.log(p, 2) for p in probabilities)
    return entropy

if __name__ == "__main__":
    
    exp1 = "(x+(x+(x+(x+(x+(x))))))"
    tree = parse_expression(exp1)

    print(structural_entropy(tree))