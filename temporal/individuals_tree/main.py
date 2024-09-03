import os
import json

from tqdm import tqdm
from tree import Tree
from params import Params, set_params
from parser import parse_expression
from graph_creator import make_visual_tree, render_tree


def map_all_individuals(experiment_dir: str):

    # Get paths
    individuals_path = os.path.join("results", exp_folder_name, "individuals")
    num_individuals = len(os.listdir(individuals_path))

    # Verify if the individuals have already been mapped into trees.
    if os.path.exists(os.path.join(individuals_path, "all_ready_trees.json")):
        # If it exists, don't do anything
        return
    
    # If not, loop over every individual
    for individual in tqdm(os.listdir(individuals_path)):
        
        current_path = os.path.join(individuals_path, individual)

        # Load individual information
        with open(os.path.join(current_path, "general_info.json"), "r") as f:
            
            data = json.load(f)
            f.close()

        #genome = data["genome"]
        phenotype = data["phenotype"]

        syntax_tree = parse_expression(phenotype)

        graph = make_visual_tree(syntax_tree)

        render_tree(graph, current_path, individual, expr=phenotype)

    # make notification file to avoid re-runs
    with open(os.path.join(individuals_path, "all_ready_trees.json"), "w") as f:
        f.close()

def load_generation(experiment_folder: str, generation: int):

    # Get generations and populations paths
    generation_path = os.path.join("results", experiment_folder, "generations")
    population_path = os.path.join(generation_path, f"generation_{generation:04d}", "population.json")

    # Open population pointers file
    with open(population_path, "r") as f:
        population_pointers = json.load(f)
        f.close()

    # Create variables
    genomes = {}
    phenotypes_to_verify = {}

    # Get individuals path
    individuals_path = os.path.join("results", experiment_folder, "individuals")

    # For each individual...
    for individual in population_pointers:
        
        # Get general info path
        ind_path = os.path.join(individuals_path, str(individual))
        general_info_path = os.path.join(ind_path, "general_info.json")

        # Load data
        with open(general_info_path, "r") as f:
            ind_data = json.load(f)
            f.close()
        
        # Append data
        genomes[individual] = ind_data["genome"]
        phenotypes_to_verify[individual] = ind_data["phenotype"]
    
    return genomes, phenotypes_to_verify
    
def map_genomes_to_trees(genomes: dict, start_expr: str, non_terminals: dict, save_path: str):

    for i, (name, genome) in enumerate(genomes.items()):

        # Instantiate a tree object
        tree = Tree(start_expr, None)

        # Build Tree
        output, used_codons, nodes, depth, max_depth, invalid = \
            genome_to_tree_map(tree, genome, [], 0, 0, 0, 0)
        
        # Get information
        effective_genome, output, _, tree_depth, num_nodes = tree.get_tree_info(non_terminals, [], [])

        phenotype = "".join(output)

        syntax_tree = parse_expression(phenotype)

        graph = make_visual_tree(syntax_tree)

        render_tree(graph, save_path, name, expr=phenotype)


if __name__ == "__main__":

    # Paths
    save_path = "individual_analysis"
    exp_folder_name = "DESKTOP-E3F66CS_2024_8_26_2217_148643"

    # Initiate parameters
    set_params()

    # Load parameters
    params = Params()

    # Import libraries
    from create_tree_figures import genome_to_tree_map

    # Get useful variables for grammar
    start_expr = str(params["BNF_GRAMMAR"].start_rule["symbol"])
    non_terminals = params["BNF_GRAMMAR"].non_terminals
    
    # DONE: First loop per all individuals, and append the image just in the results/individuals/individual_XXXX
    # DONE: Each time this code runs, it verify first if individuals have their tree already or not.
    
    map_all_individuals(exp_folder_name)

    # TODO: Once all individuals have their tree, loop over generations and compute more metrics

    # Get the number of generations
    num_generations = len(os.listdir(os.path.join("results", exp_folder_name, "generations")))

    for gen in range(num_generations):

        genomes, phenotypes = load_generation(exp_folder_name, generation=gen)

        # Create new directory for the tree representation
        new_save_path = os.path.join(save_path, f"generation_{gen:04d}")

        os.makedirs(new_save_path, exist_ok=True)

        map_genomes_to_trees(genomes, start_expr, non_terminals, save_path=new_save_path)
    
