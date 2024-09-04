
from collections import defaultdict, deque
from parser import Node, parse_expression

def hash_tree(node: Node):
    """
    Create a hashable representation of a subtree rooted at node.
    """

    if node is None:
        return "#"
    return str(node)

def collect_subtrees_and_depths(root):
    """
    Collect all subtrees and their depths in tree root.
    """

    subtree_hashes = defaultdict(int)
    subtree_depths = defaultdict(list)
    queue = deque([(root, 0)])

    while queue:
        node, depth = queue.popleft()
        subtree_hash = hash_tree(node)
        subtree_hashes[subtree_hash] += 1
        subtree_depths[subtree_hash].append(depth)

        for child in node.children:
            queue.append((child, depth + 1))
    
    return subtree_hashes, subtree_depths

def aggregate_results(trees):
    """
    Agregate results from multiple trees into single dictionaries.
    """
    
    aggregated_hashes = defaultdict(int)
    aggregated_depths = defaultdict(list)

    for tree in trees:
        subtree_hashes, subtree_depths = collect_subtrees_and_depths(tree)

        # Merge the hashes
        for hash_key, count in subtree_hashes.items():
            aggregated_hashes[hash_key] += count
        
        # Merge the depths
        for hash_key, depths in subtree_depths.items():
            aggregated_depths[hash_key].extend(depths)
    
    return aggregated_hashes, aggregated_depths

if __name__ == "__main__":

    exp1 = "masked_cross(cos(x) + sin(y), cos(x) + sin(y))"
    exp2 = "(x+(x+(x+(x+(x+(x))))))"
    exp3 = "one_point(cos(x) + y)"
    
    trees = [parse_expression(exp1), parse_expression(exp2), parse_expression(exp3)]

    aggregate_results(trees)