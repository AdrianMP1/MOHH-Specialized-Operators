import os
from mohh.evaluation.main import execute_experiments

def extract_operators(experiment_path: str, solver_names: list):

    operators = []

    for solver in solver_names:

        file_path = os.path.join(experiment_path, solver + "_operators.txt")

        with open(file_path, "r") as f:
            for line in f:
                label, operator = line.split(":", 1)
                operator = operator.strip()

                operators.append(operator)

    return operators