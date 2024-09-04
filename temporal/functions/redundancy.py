import numpy as np

from tree_representation import Node

def evaluate_tree(tree, test_suite):
    outputs = [tree.evaluate(inputs) for inputs in test_suite]

    return outputs

def compute_max_difference(original_outputs, modified_outputs):
    max_diff = max(np.max(np.abs(np.array(original) - np.array(modified))) for original, modified in zip(original_outputs, modified_outputs))

    return max_diff

def test_redundancy(tree: Node, test_suite, tolerance=0.001):

    original_outputs = evaluate_tree(tree, test_suite)

    redundant_subtrees = []

    for i in range(len(tree.children)):

        tree_copy = tree.copy()
        subtree = tree_copy.remove_subtree(i)

        if subtree is None:
            continue
        
        try:
            modified_outputs = evaluate_tree(tree_copy, test_suite)
            max_diff = compute_max_difference(original_outputs, modified_outputs)
        except:
            # Subtree is needed for valid solutions
            max_diff = float("inf")

        if max_diff < tolerance:
            # Subtree is redundant
            redundant_subtrees.append((subtree, True))
        else:
            # Subtree is not redundant
            redundant_subtrees.append((subtree, False))
    
    return redundant_subtrees

