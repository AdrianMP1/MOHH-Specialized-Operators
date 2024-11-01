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

    # Experiments path
    number = 1
    experiment_path = os.path.join("results", f"Experiment_{number:03d}")

    while os.path.exists(experiment_path):
        number += 1
        experiment_path = os.path.join("results", f"Experiment_{number:03d}")
    os.makedirs(experiment_path, exist_ok=True)

    # MO_Models to try
    models = ["MOEAD", "NSGAII", "SMSEMOA"]

    phenotypes = []

    results_paths = []

    for mo_model in models:

        # First, run generation code
        results_path, generations_path, individuals_path, elite_size = execute_generation(mo_model, experiment_path)

        # Get the last generation
        last_generation_path = os.path.join(generations_path, os.listdir(generations_path)[-1], "population.json")
        last_population = read_json(last_generation_path)
        
        # Indices for the selected operators
        indices = [0, (elite_size - 1) // 2, elite_size - 1]

        # Get operators ids
        operators = [last_population[index] for index in indices]

        # Get operators paths
        operator_paths = [os.path.join(individuals_path, operator, "general_info.json") for operator in operators]

        # Load jsons and extract phenotypes
        for operator_path in operator_paths:

            individual_data = read_json(operator_path)
            phenotype = individual_data["phenotype"]
            phenotypes.append(phenotype)
        
        # Get experiment paths
        results_path_components = results_path.split("\\")
        results_path = "\\".join(results_path_components[:-1])
        results_paths.append(results_path)

    # Save the operators
    groups = [phenotypes[i:i+3] for i in range(0, len(phenotypes), 3)]

    for index, model in enumerate(models):
        filename = os.path.join(experiment_path, f"{model}_operators.txt")
        with open(filename, "w") as file:
            for label, operator in zip(["Best", "Middle", "Worst"], groups[index]):
                file.write(f"{label}: {operator}\n")
            file.close()
     
    execute_experiments(experiment_path, results_paths, phenotypes)
