import os
from evaluation.main import execute_experiments

#solver_names = ["MOEAD", "NSGAII", "SMSEMOA"]
solver_names = ["MOEAD"]

def extract_operators(experiment_path: str):

    operators = []

    for solver in solver_names:

        file_path = os.path.join(experiment_path, solver + "_operators.txt")

        with open(file_path, "r") as f:
            for line in f:
                label, operator = line.split(":", 1)
                operator = operator.strip()

                operators.append(operator)

    return operators


if __name__ == "__main__":

    operators = extract_operators("results/Experiment_007")

    execute_experiments("results/Experiment_007", "", operators)