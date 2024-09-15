import os
import numpy as np
import pandas as pd

from handle_params import Params

from auxiliars.tree import Node
from auxiliars.file_operations import write_json
from auxiliars.tree_parser import parse_expression

from auxiliars.individuals_auxiliars import phenotypes_to_trees, best_individual
from auxiliars.individuals_auxiliars import load_generation, get_generation_files
from auxiliars.individuals_auxiliars import get_num_generations, get_general_info
from auxiliars.individuals_auxiliars import compute_hypervolumes, compute_metrics

from metrics.complexity import path_length_variance 
from metrics.structural import structural_entropy
from metrics.structural import compute_balance_skewness, compute_path_lengths
from metrics.subtree_characteristics import collect_subtrees
from metrics.expansion_rate import compute_expansion_rate





def individual_metrics_dataframe() -> pd.DataFrame:
    """
    Computes for all individuals and writes a pandas dataframe
    Structural Metrics, Entropy and Path Length Variance.
    """

    # Get parameters
    params = Params()

    # Get paths
    experiment_path = params["EXPERIMENT_PATH"]
    individuals_path = params["INDIVIDUALS_PATH"]

    # Get generation paths
    final_generation = get_num_generations() - 1
    final_generation_path = os.path.join(params["GENERATIONS_PATH"],
                                f"generation_{final_generation:04d}")
    instance_files: list[str] = get_generation_files(final_generation_path)
     
    # Extract all phenotypes
    individuals:dict[str, str] = dict()
    for name in os.listdir(individuals_path):

        if name in ["all_ready_trees.json"]:
            continue

        current_path: str = os.path.join(individuals_path, name)
        general_info: dict = get_general_info(current_path)

        phenotype: str = general_info["phenotype"]
        individuals[name] = phenotype

    # Compute HVs for all individuals with the last nadir point.
    _, hypervolumes = compute_hypervolumes(individuals, generation=final_generation)

    # Transform HVs with log2, and 8 decimal places of precision.
    transformed_hv = np.round(np.log2(np.array(hypervolumes)), 8)
   
    # Compute metrics
    names = list(individuals.keys())
    phenotypes = list(individuals.values())
   
    whole_sizes = []
    whole_balance = []
    whole_skewness = []
    whole_maxdepth = []

    entropies = []
    variances = []

    for name, phenotype in individuals.items():
        
        # Get syntax tree from phenotype
        syntax_tree: Node = parse_expression(phenotype)
        
        # Structural Metrics
        depth, _, _, balance, skewness, num_nodes = compute_balance_skewness(syntax_tree.copy())
        whole_sizes.append(num_nodes)
        whole_balance.append(balance)
        whole_skewness.append(skewness)
        whole_maxdepth.append(depth)

        # Entropy
        entropy = structural_entropy(syntax_tree.copy())
        entropies.append(entropy)
        
        # Path length variance
        path_lengths = compute_path_lengths(syntax_tree.copy())
        variance = path_length_variance(path_lengths)
        variances.append(variance)

    # Make dictionary for dataframe
    data = {"Name":names, "Phenotype":phenotypes, "Balance":whole_balance,
             "Skewness":whole_skewness, "MaxDepth":whole_maxdepth, "Size":whole_sizes,
             "Entropy":entropies, "PathLengthVariance":variances}
    
    # Add Hypervolumes
    for i, instance in enumerate(instance_files):

        # Get instance HVs
        instance_hvs = transformed_hv[:,i].tolist()
        
        # Make string key
        instance = instance.replace("Instance_Fronts", "Instance")
        instance = instance.removesuffix(".json")
        instance_key = f"{instance}_log2(HV)"

        # Add the list to the data dictionary.
        data[instance_key] = instance_hvs

    # Make dataframe
    df = pd.DataFrame(data)

    # Round numeric columns
    columns = ["Entropy", "PathLengthVariance"]
    df.loc[:,columns] = df.loc[:,columns].round(4)

    # Save it in disk
    df.to_csv(os.path.join(experiment_path, "individuals_metrics.csv"), index=False)
    
    return df


def individual_metrics_json() -> dict:
    """
    """

    # Get parameters
    params = Params()

    # Get paths
    individuals_path = params["INDIVIDUALS_PATH"]

    # Compute metrics
    for name in os.listdir(individuals_path):

        if name in ["all_ready_trees.json"]:
            continue

        # Get individual information
        current_path: str = os.path.join(individuals_path, name)
        general_info: dict = get_general_info(current_path)

        # Extract phenotype
        phenotype: str = general_info["phenotype"]

        # Get syntax tree from phenotype
        syntax_tree: Node = parse_expression(phenotype)

        # Compute subtrees [dict, dict, dict]
        subtrees, subtrees_depths, non_terminals_depths = collect_subtrees(syntax_tree.copy())
        
        # Get non-terminals frequency
        non_terminals: dict = compute_expansion_rate(syntax_tree.copy())

        # Make files
        write_json(os.path.join(current_path, f"subtrees_frequency.json"), subtrees)
        write_json(os.path.join(current_path, f"subtrees_depths.json"), subtrees_depths)
        
        write_json(os.path.join(current_path, f"non_terminals_frequency.json"), non_terminals)
        write_json(os.path.join(current_path, f"non_terminals_depth.json"), non_terminals_depths)


def generational_metrics(metrics: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """    
    Compute generation dependent metrics.
    """

    # Get parameters
    params = Params()

    # Get number of generations
    num_generations: int = get_num_generations()

    # Data (list of dictionaries)
    pop_data = []
    off_data = []

    # Change name to index
    metrics.set_index("Name", inplace=True)

    # Loop over generations
    for gen in range(num_generations):

        # Get the current generation phenotypes.
        pop_phenotypes, off_phenotypes = load_generation(gen)

        # Compute HVs and rankings
        rankings, hypervolumes = compute_hypervolumes(pop_phenotypes, gen)

        # Map phenotypes into trees
        pop_trees = phenotypes_to_trees(pop_phenotypes)
        off_trees = phenotypes_to_trees(off_phenotypes)

        # Get the best individual tree
        pop_best_tree = best_individual(pop_trees, rankings)

        # Compute metrics
        pop_row = compute_metrics(metrics, pop_trees, pop_best_tree)
        off_row = compute_metrics(metrics, off_trees, pop_best_tree)

        # Append row to form dataframe
        pop_data.append(pop_row)
        off_data.append(off_row)

        # Do something for subtrees.

    # Make data to dataframe
    pop_df = pd.DataFrame(pop_data)
    off_df = pd.DataFrame(off_data[:-1])

    # Round values
    pop_df = pop_df.round(decimals=6)
    off_df = off_df.round(decimals=6)

    # Add generations column
    pop_df.insert(0, "Generation", range(0, len(pop_df)))
    off_df.insert(0, "Generation", range(0, len(off_df)))

    # Save it to disk
    experiment_path = params["EXPERIMENT_PATH"]
    pop_df.to_csv(os.path.join(experiment_path, "population_generation_data.csv"), index=False)
    off_df.to_csv(os.path.join(experiment_path, "offspring_generation_data.csv"), index=False)
    
    return pop_df, off_df
