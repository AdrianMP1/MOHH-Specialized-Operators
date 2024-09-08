
from auxiliars.tree import Node
from structural import compute_path_lengths
from subtree_characteristics import subtree_sizes

def path_length_variance(path_lengths: list) -> float:
    """
    Compute the variance of the given path lenghts
    """

    if not path_lengths:
        return 0
    
    num_paths: int = len(path_lengths)

    mean_length: float = sum(path_lengths) / num_paths
    variance: float = sum((length - mean_length)**2 for length in path_lengths) / num_paths

    return variance


def population_path_length_variance(trees: list[Node]) -> list:
    """
    From a population, compute the variance of their path lengths.
    """

    variances = []

    for tree in trees:
        path_lengths = compute_path_lengths(tree)
        variance = path_length_variance(path_lengths)

        variances.append(variance)
    
    return variances


def find_node_by_path(tree: Node, path: list) -> Node:
    """
    Find a node by its path (a sequence of indices) from the root.
    For example, path [0, 1] means the second child of the first child of the root.
    """

    current_node = tree

    for index in path:
    
        if not current_node or index >= len(current_node.children):
            return None
    
        current_node = current_node.children[index]

    return current_node


def test_tree(tree: Node, test_suite: list[list]) -> list[list]:
    """
    Evaluate the tree with all test instances.
    """

    outputs: list[list] = [tree.evaluate(inputs) for inputs in test_suite]

    return outputs


def get_max_diff(original: list[list], modified: list[list]) -> float:

    max_diff = 0.0

    for i in range(len(original)):
        current_max = max([abs(x - y) for x,y in zip(original[i], modified[i])])

        if current_max > max_diff:
            max_diff = current_max
    
    return max_diff


def detect_redundancy(tree: Node, test_suite: list[list], tolerance: float=0.01) -> list:
    """
    Remove subtrees and check if they are redundant.
    """

    # Evaluate the original tree in the test_suite.
    original_outputs = test_tree(tree, test_suite)

    # Make local memory for redundant subtrees
    redundant_subtrees = []

    def is_redundant(tree_copy: Node) -> bool:

        try:
            # Evaluate pruned tree
            modified_outputs = test_tree(tree_copy, test_suite)
            max_diff = get_max_diff(original_outputs, modified_outputs)
        
        except:
            # Pruned subtree was necessary.
            max_diff = float("inf")
        
        return max_diff < tolerance
    
    def check_redundancy(node: Node, index: list) -> None:
        nonlocal redundant_subtrees

        # If terminal...
        if not node.children:
            return
        
        # Special case: binary non_terminals
        # TODO: Hardcoded, fix it.
        if node.value in {'+', '-', 'masked_cross', 'one_point', 'convolution'}:

            # Duplicate original tree
            tree_copy = tree.copy()
            # Make a reference from tree_copy to the current parent.
            # If parent copy is modified, tree copy is also modified...
            parent_copy: Node = find_node_by_path(tree_copy, index)

            # Get left and right
            left_subtree: Node = parent_copy.children[0].copy()
            right_subtree: Node = parent_copy.children[1].copy()

            # Remove current non_terminal, and try with left subtree only
            parent_copy.value = left_subtree.value
            parent_copy.children = left_subtree.children

            # Verify redundancy
            redundant = is_redundant(tree_copy)
            if redundant:
                # Right side was redundant, left side achieved the same as original.
                redundant_subtrees.append((f"{node.value}({str(right_subtree)})", True))
            else:
                # Right side was not redundant.
                redundant_subtrees.append((f"{node.value}({str(right_subtree)})", False))

            # Verify if left subtree has any redundant children recursively  
            check_redundancy(left_subtree, index + [0])

            # Try with right subtree only now.
            parent_copy.value = right_subtree.value
            parent_copy.children = right_subtree.children

            # Verify redundancy
            redundant = is_redundant(tree_copy)
            if redundant:
                # Left side was redundant, right side achieved the same as original.
                redundant_subtrees.append((f"{node.value}({str(left_subtree)})", True))
            else:
                # Left side was not redundant
                redundant_subtrees.append((f"{node.value}({str(left_subtree)})", False))
            
        else:
            # Regular subtree

            for i in range(len(node.children)):
                
                # Copy current subtree
                subtree: Node = node.children[i].copy()

                # Duplicate original tree
                tree_copy = tree.copy()
                parent_copy: Node = find_node_by_path(tree_copy, index)

                # Remove subtree
                removed_subtree = parent_copy.children.pop(i)

                # Verify redundancy
                redundant = is_redundant(tree_copy)
                if redundant:
                    # Removed subtree was not necessary
                    redundant_subtrees.append((str(removed_subtree), True))
                else:
                    # Removed subtree was necessary
                    redundant_subtrees.append((str(removed_subtree), False))
                
                check_redundancy(subtree, index + [i])
    
    # Verify redundancy in the tree
    check_redundancy(tree, [])

    # Filter all terminals that are not redundant
    redundant_subtrees = [subtree for subtree in redundant_subtrees if not((subtree[0] in ["x()","y()"]) and not(subtree[1]))]

    return redundant_subtrees


def population_redundancy(population: list[Node], test_suite: list[list]) -> list[float]:

    redundancy = []

    for tree in population:
        # Get the number of subtrees
        num_subtrees = len(subtree_sizes(tree))

        # Get analyzed subtrees
        subtrees = detect_redundancy(tree, test_suite)

        # Filter to only redundant
        redundant_subtrees = [element[0] for element in subtrees if element[1]]

        # Compute metric and save it
        redundancy.append(len(redundant_subtrees) / num_subtrees)

    return redundancy
