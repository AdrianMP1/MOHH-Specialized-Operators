# Imports
import os
import json

from mohh.generation.main import execute_generation

def read_json(data_path: str) -> dict:

    with open(data_path, "r") as f:
        data = json.load(f)
        f.close()

    return data

def make_experiment_path() -> str:

    number = 1
    experiment_path = os.path.join("results", f"Experiment_{number:03d}")

    while os.path.exists(experiment_path):
        number += 1
        experiment_path = os.path.join("results", f"Experiment_{number:03d}")
    os.makedirs(experiment_path, exist_ok=True)

    return experiment_path

def run_generation(experiment_path: str, models: list, overrides: dict = None) -> list:

    phenotypes = []

    for mo_model in models:

        # First, run generation code
        results_path, generations_path, individuals_path, elite_size = execute_generation(mo_model, experiment_path, overrides)

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
        model_phenotypes = []
        for operator_path in operator_paths:

            individual_data = read_json(operator_path)
            phenotype = individual_data["phenotype"]
            model_phenotypes.append(phenotype)

        # Save the operators
        filename = os.path.join(experiment_path, f"{mo_model}_operators.txt")
        with open(filename, "w") as file:
            for label, operator in zip(["Best", "Middle", "Worst"], model_phenotypes):
                file.write(f"{label}: {operator}\n")
            file.close()

        phenotypes.extend(model_phenotypes)

    return phenotypes

if __name__ == "__main__":

    experiment_path = make_experiment_path()
    run_generation(experiment_path, ["MOEAD"])
