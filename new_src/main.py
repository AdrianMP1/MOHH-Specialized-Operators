# Imports
import os
import json

from generation.main import execute_generation
from evaluation.main import execute_experiments

test_individuals = True

def read_json(data_path: str) -> dict:

    with open(data_path, "r") as f:
        data = json.load(f)
        f.close()

    return data

if __name__ == "__main__":

    # MO_Models to try
    models = ["NSGAII", "SMSEMOA"]

    for mo_model in models:

        # First, run generation code
        experiment_path, generations_path, individuals_path, elite_size = execute_generation(mo_model)

        # Evaluate best, middle and worst individuals
        if test_individuals:

            # Get the last generation
            last_generation_path = os.path.join(generations_path, os.listdir(generations_path)[-1], "population.json")
            last_population = read_json(last_generation_path)

            # Indices for the selected operators
            indices = [0, (elite_size-1)//2, elite_size-1]

            # Get operators ids
            operators = [last_population[index] for index in indices]

            # Get operators paths
            operators_paths = [os.path.join(individuals_path, operator, "general_info.json") for operator in operators]

            # Load jsons and extract phenotypes
            phenotypes = []
            for operator_path in operators_paths:

                individual_data = read_json(operator_path)
                phenotype = individual_data["phenotype"]
                phenotypes.append(phenotype)

            # Run the evaluation
            experiment_path_components = experiment_path.split("\\")
            experiment_path = "\\".join(experiment_path_components[:-1])
            execute_experiments(experiment_path, phenotypes)
