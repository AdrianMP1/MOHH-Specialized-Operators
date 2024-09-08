
from auxiliars.tree import Node

def compute_expansion_rate(tree: Node) -> dict:
    """
    Get all the non-terminals number of appearance.
    """

    non_terminals = {}

    def count_specific_expansions(node: Node):
        """
        Recursively traverse the tree and mark
        the non-terminals.
        """
        if not node.children:
            return
        
        # Increment counter
        non_terminals[node.value] = non_terminals.get(node.value, 0) + 1

        for child in node.children:
            count_specific_expansions(child)
        
    count_specific_expansions(tree)

    return non_terminals

def population_expansion_rate(population: list[Node]) -> dict:
    """
    Compute the expansion rate of non-terminals
    for the whole population.
    """

    pop_non_terminals = dict()

    for individual in population:

        non_terminals = compute_expansion_rate(individual)

        pop_non_terminals = {key: pop_non_terminals.get(key, 0) + \
                             non_terminals.get(key, 0) for key in \
                            set(pop_non_terminals) | set(non_terminals)}
    
    return pop_non_terminals
