
import os
import numpy as np
import pandas as pd

from pymoo.indicators.hv import HV

from handle_params import Params

from auxiliars.tree import Node
from auxiliars.file_operations import read_json
from auxiliars.tree_parser import parse_expression

from metrics.structural import tree_edit_distance


def get_num_generations() -> int:
    """
    Returns the number of generations in the generations path.
    """

    params = Params()
    return len(os.listdir(params["GENERATIONS_PATH"]))


def get_general_info(current_path: str) -> dict:
    """
    Extracts the json file general_info for the current individual.
    """

    general_info_path = os.path.join(current_path, "general_info.json")
    return read_json(general_info_path)


def get_generation_files(current_generation: str) -> list[str]:

    # Get files
    generation_files: list[str] = os.listdir(current_generation)

    # Remove population and offspring pointer files.
    try:
        generation_files.remove("population.json")
        generation_files.remove("offspring.json")
    except:
        # Inexistent files, just continue.
        pass
    
    return generation_files


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
    """
    Function to rank individuals based on HV.
    """
    
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
    Re-compute hypervolumes from current generation.
    """

    # Get parameters
    params = Params()

    # Get current generation path  
    generation_path: str = params["GENERATIONS_PATH"]
    current_generation: str = os.path.join(generation_path, f"generation_{generation:04d}")
 
    # Get individuals path
    individuals_path: str = params["INDIVIDUALS_PATH"]
    
    # Get files
    generation_files: list[str] = get_generation_files(current_generation)
    
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
        best_front = np.array(consolidated["Front_000"])

        # Get nadir point
        nadir_point = best_front.max(axis=0)
        #nadir_point = consolidated["nadir_point"]

        del consolidated

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


def load_generation(generation: int) -> tuple[dict, dict]:
    """
    Loads the individuals of generation i.
    """

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
    try:
        offspring_pointers = read_json(offspring_path)
    except:
        offspring_pointers = dict()

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


def best_individual(individuals: dict[str, Node], rankings: list[list]) -> Node:
    """
    Based on ranking, returns the best individual.
    """
    
    individuals_name = list(individuals.keys())
    
    avg_rank = [sum(ranks) / len(ranks) for ranks in rankings]
    best_index = avg_rank.index(min(avg_rank))

    # Get the best individual tree
    best_tree = individuals[individuals_name[best_index]]
    return best_tree


def compute_metrics(metrics: pd.DataFrame, individuals: dict[str,Node], best_tree: Node) -> dict[str, float]:
    """
    Computes the metrics for one generation
    """

    # To allocate data.
    ## Row contains summarized data
    row = {}
    ## full_row contains raw data, N points per variable
    full_row = {}

    # Compute Tree-Edit Distance
    costs = []
    for name, tree in individuals.items():

        # Compare all individuals against the best
        cost = tree_edit_distance(tree.copy(), best_tree.copy())
        costs.append(cost)

    try:
        # Add the min, max and avg of TED.
        row["TED_min"] = min(costs)
        row["TED_max"] = max(costs)
        row["TED_med"] = np.median(costs).item()
        row["TED_avg"] = np.mean(costs).item()

        full_row["TED"] = costs

        # Get dataframe metrics
        other_row, other_full_row = compute_dataframe_metrics(metrics, list(individuals.keys()))

        # Merge both dictionaries
        row.update(other_row)
        full_row.update(other_full_row)
    
    except Exception as e:
        # If costs exists, print the error
        if costs:
            print(e)
        
        else:
            # Costs doesn't contain anything.
            # There wasn't population or offspring in this generation.
            pass

    return row, full_row


def compute_dataframe_metrics(metrics: pd.DataFrame, individuals_name: list) -> dict[str,float]:
    """
    From the individual's dataframe, compute metrics for a generation.
    """
    
    # Allocate variable
    ## Row for summarized data
    row = {}
    ## Full_row for raw data
    full_row = {}

    # Columns names
    ## Ignore first column (phenotypes)
    columns = metrics.columns[1:]

    # Filter to current generation individuals in numeric columns
    temp: pd.Series = metrics.loc[individuals_name, columns]

    # Min values
    min_values = temp.min()

    # Max values
    max_values = temp.max()

    # Median values
    med_values = temp.median()

    # Average values
    avg_values = temp.mean()

    # Append data to row
    for name in min_values.index:
        row[f"{name}_min"] = min_values[name]
        row[f"{name}_max"] = max_values[name]
        row[f"{name}_med"] = med_values[name]
        row[f"{name}_avg"] = avg_values[name]
        full_row[f"{name}"] = temp[name].tolist()
    
    return row, full_row
