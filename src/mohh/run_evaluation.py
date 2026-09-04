import os

def discover_models(experiment_path: str) -> list:
    """
    Generation models that actually produced operators in this experiment,
    found from the *_operators.txt files mohh-generate writes.
    """

    suffix = "_operators.txt"

    return sorted(f[:-len(suffix)] for f in os.listdir(experiment_path) if f.endswith(suffix))

def extract_operators(experiment_path: str, model_names: list):

    operators = []

    for model in model_names:

        file_path = os.path.join(experiment_path, model + "_operators.txt")

        with open(file_path, "r") as f:
            for line in f:
                label, operator = line.split(":", 1)
                operator = operator.strip()

                operators.append(operator)

    return operators