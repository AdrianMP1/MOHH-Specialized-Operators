
from auxiliars.tree import Node
from collections import defaultdict, deque

def subtree_sizes(node: Node) -> list:
    """
    Recursively compute the size of each subtree.
    Returns a list of subtree sizes, including the current node.
    """

    if node is None:
        return []
    
    # Count current node
    sizes = [1] 

    for child in node.children:
        child_sizes = subtree_sizes(child)
        sizes.extend(child_sizes)
        sizes[0] += child_sizes[0]
    
    return sizes


def hash_tree(node: Node) -> str:
    """
    Create a hashable representation of a subtree.
    """

    if node is None:
        return "#"
    
    return str(node)


def collect_subtrees(tree: Node) -> tuple[dict, dict, dict]:
    """
    Collect all subtrees and their depths in the tree root
    """

    # Make memory
    subtree_hashes = defaultdict(int)
    subtree_depths = defaultdict(list)
    non_terminals_depth = defaultdict(list)

    # Put in queue
    queue = deque([(tree, 0)])

    # BFS Algorithm.
    while queue:
        # Extract current.
        node, depth = queue.popleft()
        
        # Make a hash
        subtree_hash = hash_tree(node)
        
        # Save it
        subtree_hashes[subtree_hash] += 1
        subtree_depths[subtree_hash].append(depth)

        if node.children:
            non_terminals_depth[node.value].append(depth)

        # Deal with children
        for child in node.children:
            queue.append((child, depth + 1))
    
    return subtree_hashes, subtree_depths, non_terminals_depth


def population_subtrees(trees: list[Node]) -> tuple:
    """
    Compute collect subtrees for the whole population.
    """

    aggregated_hashes = defaultdict(int)
    aggregated_depths = defaultdict(list)
    aggregated_non_terminals = defaultdict(list)

    for tree in trees:
        subtree_hashes, subtree_depths, non_terminals = collect_subtrees(tree)

        # Merge hashes
        for hash_key, count in subtree_hashes.items():
            aggregated_hashes[hash_key] += count
        
        # Merge depths
        for hash_key, depths in subtree_depths.items():
            aggregated_depths[hash_key].extend(depths)

        # Merge non-terminals
        for hash_key, depths in non_terminals.items():
            aggregated_non_terminals[hash_key].extend(depths)

    return aggregated_hashes, aggregated_depths, aggregated_non_terminals
