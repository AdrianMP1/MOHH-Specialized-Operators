
import numpy as np

from mohh.core.params import Params
from collections import deque


def mapper(genome: list):
    """
    Maps a genome into a phenotype, via the grammar.

    @param genome: Individual's genome.
    """

    # Make a copy
    genome = list(genome)

    phenotype, genome, tree, nodes, invalid, depth, \
    used_codons = map_ind_from_genome(genome)

    if invalid:
        # Set values for invalid individuals
        phenotype, nodes, depth, used_codons = None, np.nan, np.nan, np.nan

    return phenotype, genome, tree, nodes, invalid, depth, used_codons

def map_ind_from_genome(genome: list) -> tuple:
    """
    Code adapted from PonyGE2 (github.com/PonyGE/PonyGE2).

    Making use of the genome, create an individual.
    """

    # Load parameters
    params = Params()

    max_tree_depth, max_wraps = params["MAX_TREE_DEPTH"], params["MAX_WRAPS"]
    bnf_grammar = params["BNF_GRAMMAR"]

    n_input = len(genome)

    # Initialize variables
    used_input, current_depth, max_depth, nodes, wraps = 0, 1, 1, 1, -1

    # Initialize output as empty deque list
    output = deque()

    # Initialize the list of unexpanded non-terminals with the start rule.
    unexpanded_symbols = deque([(bnf_grammar.start_rule, 1)])

    while (wraps < max_wraps) and unexpanded_symbols:
        # While there are unexpanded non-terminals, and it is below
        # the wrapping limit, continue the map.

        if max_tree_depth and (max_depth > max_tree_depth):
            # The map breached the maximum tree depth limit.
            break

        if used_input % n_input == 0 and \
            used_input > 0 and \
            any([i[0]["type"] == "NT" for i in unexpanded_symbols]):
            # If we have reached the end of the genome and unexpanded
            # non-terminals remain, then we need to wrap back to the start
            # of the genome again. Can break the while loop.
            wraps += 1

        # Expand a production from the list of unexpanded non-terminals.
        current_item = unexpanded_symbols.popleft()
        current_symbol, current_depth = current_item[0], current_item[1]

        if max_depth < current_depth:
            # Set the new maximum depth.
            max_depth = current_depth

        # Set output if it is a terminal.
        if current_symbol["type"] != "NT":
            output.append(current_symbol["symbol"])

        else:
            # Current item is a new non-terminal. Find associated production
            # choices.
            production_choices = bnf_grammar.rules[current_symbol[
                "symbol"]]["choices"]
            no_choices = bnf_grammar.rules[current_symbol["symbol"]][
                "no_choices"]

            # Select a production based on the next available codon in the
            # genome.
            current_production = genome[used_input % n_input] % no_choices

            # Use an input
            used_input += 1

            # Initialise children as empty deque list.
            children = deque()
            nt_count = 0

            for prod in production_choices[current_production]['choice']:
                # iterate over all elements of chosen production rule.

                child = [prod, current_depth + 1]

                # Extendleft reverses the order, thus reverse adding.
                children.appendleft(child)
                if child[0]["type"] == "NT":
                    nt_count += 1

            # Add the new children to the list of unexpanded symbols.
            unexpanded_symbols.extendleft(children)

            if nt_count > 0:
                nodes += nt_count
            else:
                nodes += 1

    # Generate phenotype string.
    output = "".join(output)

    if len(unexpanded_symbols) > 0:
        # All non-terminals have not been completely expanded, invalid
        # solution.
        return None, genome, None, nodes, True, max_depth, used_input

    return output, genome, None, nodes, False, max_depth, used_input

