import os

from handle_params import Params
from auxiliars.read_files import read_json

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


def get_num_generations() -> int:
    params = Params()
    return len(os.listdir(params["GENERATIONS_PATH"]))