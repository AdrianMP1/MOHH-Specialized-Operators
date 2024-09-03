# Note: This file must be a prototype to tree creation and figure creation of the trees.

#import networkx
import numpy as np
import matplotlib.pyplot as plt

from params import Params
from tree import Tree

params = Params()

def genome_to_tree_map(tree, genome, output, index, depth, max_depth, nodes, invalid=False):
    """
    Recursive function which builds a tree using production rules from a genome.
    """

    if not invalid and index < len(genome) * (params["MAX_WRAPS"] + 1):

        if params["MAX_TREE_DEPTH"] and (max_depth > params["MAX_TREE_DEPTH"]):

            invalid = True
        
        nodes += 1
        depth += 1
        tree.id, tree.depth = nodes, depth

        productions = params["BNF_GRAMMAR"].rules[tree.root]["choices"]
        no_choices = params["BNF_GRAMMAR"].rules[tree.root]["no_choices"]

        tree.codon = genome[index % len(genome)]

        selection = tree.codon % no_choices

        chosen_prod = productions[selection]

        index += 1

        tree.children = []

        for symbol in chosen_prod["choice"]:

            if symbol["type"] == "T":
                tree.children.append(Tree(symbol["symbol"], tree))
                output.append(symbol["symbol"])

            elif symbol["type"] == "NT":
                tree.children.append(Tree(symbol["symbol"], tree))

                output, index, nodes, d, max_depth, invalid = \
                    genome_to_tree_map(tree.children[-1], genome, output,
                                       index, depth, max_depth, nodes,
                                       invalid=invalid)
    
    else:
        return output, index, nodes, depth, max_depth, True
    
    NT_kids = [kid for kid in tree.children if kid.root in
               params["BNF_GRAMMAR"].non_terminals]
    
    if not NT_kids:
        depth += 1
        nodes += 1

    if not invalid:

        if depth > max_depth:
            max_depth = depth
        
        if params["MAX_TREE_DEPTH"] and (max_depth > params["MAX_TREE_DEPTH"]):
            invalid = True
    
    return output, index, nodes, depth, max_depth, invalid