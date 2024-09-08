import os

from handle_params import Params

from auxiliars.tree import Node
from auxiliars.read_files import read_json
from auxiliars.tree_parser import parse_expression

from metrics.structural import tree_edit_distance, structural_entropy, compute_balance_skewness
from metrics.subtree_characteristics import population_subtrees
from metrics.complexity import population_path_length_variance, population_redundancy 
from metrics.expansion_rate import population_expansion_rate

def get_num_generations() -> int:
    params = Params()
    return len(os.listdir(params["GENERATIONS_PATH"]))


def load_generation(generation: int) -> tuple[dict, dict]:

    # Get parameters
    params = Params()

    # Get paths
    generation_path = params["GENERATIONS_PATH"]
    individuals_path = params["INDIVIDUALS_PATH"]

    offspring_path = os.path.join(generation_path, f"generation_{generation:04d}", "offspring.json")
    population_path = os.path.join(generation_path, f"generation_{generation:04d}", "population.json")
    

    # Open population pointer files
    population_pointers = read_json(population_path)

    # Open offspring pointer files
    offspring_pointers = read_json(offspring_path)

    # Create variables
    pop_phenotypes = {}
    off_phenotypes = {}

    for individual in population_pointers:

        # Get general info
        ind_path = os.path.join(individuals_path, str(individual))
        general_info_path = os.path.join(ind_path, "general_info.json")

        # Load data
        data = read_json(general_info_path)
        
        # Append data
        pop_phenotypes[individual] = data["phenotype"]

    for individual in offspring_pointers:

        # Get general info
        ind_path = os.path.join(individuals_path, str(individual))
        general_info_path = os.path.join(ind_path, "general_info.json")

        # Load data
        data = read_json(general_info_path)
        
        # Append data
        off_phenotypes[individual] = data["phenotype"]
    
    return pop_phenotypes, off_phenotypes


def phenotypes_to_trees(individuals: dict[str,str]) -> list[Node]:
    """
    Parse the phenotypes[str] to trees[Nodes].
    """

    trees = dict()

    for name, phenotype in individuals.items():
        tree = parse_expression(phenotype)   
        trees[name] = tree
    
    return trees


def compute_metrics(individuals: dict[str, Node]):
    """
    """

    # Recompute fitness, verify ranking.


    # Tree Edit Distance
    ## Get the best individual
    
    ## Compare all individuals against the best
    edit_costs = dict()
    for name, tree in individuals.items():
        cost = tree_edit_distance(tree, best_tree)
        edit_costs[name] = cost

    # Structural Entropy
    entropies = dict()
    for name, tree in individuals.items():
        entropy = structural_entropy(tree, kind="subtree_sizes")
        entropies[name] = entropy
    
    # Balance and Skewness
    balances = dict()
    skewness = dict()
    depths = dict()
    node_sizes = dict()
    for name, tree in individuals.items():
        depth, abs_balance, abs_skewness, \
        dir_balance, dir_skewness, num_nodes = compute_balance_skewness()
       
        depths[name] = depth
        node_sizes[name] = num_nodes  
       
        balances[name] = [abs_balance, dir_balance]
        skewness[name] = [abs_skewness, dir_skewness]

    # Subtree Frequency & Depth Distribution
    subtrees, subtress_sizes, num_nonterminals = population_subtrees(individuals)

    # Path Length Variance
    path_variances = population_path_length_variance(individuals)

    # Redundancy
    redundancies = population_redundancy(individuals)

    # Expansion Rate
    non_terminals = population_expansion_rate(individuals)

    # Compute correlations, find patterns
