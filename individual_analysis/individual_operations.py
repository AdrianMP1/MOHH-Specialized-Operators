import os
import numpy as np

from pymoo.indicators.hv import HV

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


def phenotypes_to_trees(individuals: dict[str,str]) -> dict[str,Node]:
    """
    Parse the phenotypes[str] to trees[Nodes].
    """

    trees = dict()

    for name, phenotype in individuals.items():
        tree = parse_expression(phenotype)   
        trees[name] = tree
    
    return trees


def compute_rank(hypervolumes: list) -> list:

    # Sort hypervolumes in descending order.
    sorted_values = sorted(hypervolumes, reverse=True)

    # Calculate ranks
    ranks = dict()
    for i, value in enumerate(sorted_values):
        temp = ranks.get(value, [])
        temp.append(i+1)
        ranks[value] = temp

    # Calculate the average rank for each value
    average_ranks = {value: sum(rank) / len(rank) for value, rank in ranks.items()}

    # Map the average ranks back to the original list
    ranked_values = [average_ranks[value] for value in hypervolumes]

    return ranked_values


def compute_hypervolumes(individuals: dict[str,str], generation: int):
    """
    """

    # Get parameters
    params = Params()

    # Get current generation path  
    generation_path: str = params["GENERATIONS_PATH"]
    current_generation: str = os.path.join(generation_path, f"generation_{generation:04d}")
 
    # Get individuals path
    individuals_path: str = params["INDIVIDUALS_PATH"]
    
    # Get files
    generation_files: list[str] = os.listdir(current_generation)
    
    # Substract 2 files: offspring and population pointers.
    generation_files.remove("offspring.json")
    generation_files.remove("population.json")
    
    # Get number of instances.
    num_instances = len(generation_files)
    num_individuals = len(individuals)

    rankings = [[0]*num_instances for _ in range(num_individuals)]
    hypervolumes = [[0]*num_instances for _ in range(num_individuals)]

    for i, instance in enumerate(generation_files):

        # Read Consolidated Front
        consolidated_path: str = os.path.join(current_generation, instance)
        consolidated = read_json(consolidated_path)

        # Get primary front
        best_front = consolidated["Front_000"]

        # Get nadir point
        nadir_point = consolidated["nadir_point"]

        # Initialize HV
        metric = HV(ref_point=nadir_point)

        # Change instance name to match individual format
        instance = instance.removeprefix("Instance_Fronts")
        instance = "instance" + instance

        # HV memory
        hvs = []

        # Loop over individuals to get their fronts
        for name, phenotype in individuals.items():
            
            # Make individual path to current instance
            current_individual_path = os.path.join(individuals_path, name, instance)

            # Read json
            individual_data: dict = read_json(current_individual_path)

            # Extract front
            front = np.array(individual_data["front"])

            # Compute HV
            hv = metric(front)
            hvs.append(hv)
        
        ranks = compute_rank(hvs)

        for j in range(num_individuals):
            rankings[j][i] = ranks[j]
            hypervolumes[j][i] = hvs[j]
    
    return rankings, hypervolumes


def compute_metrics(individuals: dict[str, Node], rankings: list[list], hypervolumes: list[list]):
    """
    """

    # Recompute fitness, verify ranking.
    # TODO: ALREADY IN ARGUMENTS.

    # Get the best individual index & name
    individuals_names = list(individuals.keys())
    avg_rank = [sum(ranks) / len(ranks) for ranks in rankings]
    best_index = avg_rank.index(min(avg_rank))

    # Get the best individual tree
    best_tree = individuals[individuals_names[best_index]]

    # Create variables
    edit_costs = dict()
    entropies = dict()
    balances = dict()
    skewness = dict()
    depths = dict()
    node_sizes = dict()

    for name, tree in individuals.items():
        
        # Tree Edit Distance
        ## Compare all individuals against the best
        cost = tree_edit_distance(tree.copy(), best_tree.copy())
        edit_costs[name] = cost

        # Structural Entropy
        entropy = structural_entropy(tree.copy(), kind="subtree_sizes")
        entropies[name] = entropy

        # Balance and Skewness
        # TODO: Balance and Skewness is not working right for unary trees.
        # TODO: Binary trees are fine, but unary trees gave preference to left side
        # TODO: Making it unbalance.
        depth, abs_balance, abs_skewness, \
        dir_balance, dir_skewness, num_nodes = compute_balance_skewness(tree.copy())
        depths[name] = depth
        node_sizes[name] = num_nodes
        balances[name] = [abs_balance, dir_balance]
        skewness[name] = [abs_skewness, dir_skewness]

    # Subtree Frequency & Depth Distribution
    subtrees, subtrees_sizes, num_nonterminals = population_subtrees(individuals)

    # Path Length Variance
    path_variances = population_path_length_variance(individuals)

    # Redundancy
    redundancies = population_redundancy(individuals)

    # Expansion Rate
    non_terminals = population_expansion_rate(individuals)

    # Compute correlations, find patterns
