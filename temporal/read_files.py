
# Note: The code will need some functionalities from the QAP to decode the initial solutions.
# More like the instance class. 
import os
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

from instance import QuadraticAssignment


# TODO: Initial Solutions: DONE
# TODO: Generations      : 
# TODO: Individuals      : 

def extract_initial_solutions(file_path):

    with open(file_path, "r") as f:
        data = f.readlines()

        solutions = np.zeros((len(data), len(eval(data[0]))))

        for i, line in enumerate(data):
            solutions[i] = eval(line)
        
    return solutions

def extract_qap_parameters(file_name: str):
        """
        Extract parameters from file names.
        """
        # Get instance file name
        instance_name = file_name.removesuffix(".txt")

        # Extract parameters from the file_name
        parameters: list = instance_name.split("-")

        # Number of variables
        n_variables: int = int(parameters[0][2:])

        # Number of objectives
        k_objectives: int = int(parameters[1][:-2])

        # Instance Id
        identification: int = int(parameters[2][:-2])

        # Type of distribution
        kind: str = parameters[2][1:]

        return n_variables, k_objectives

if __name__ == "__main__":

    instance_path = "datasets/mqap/train/"

    initial_solutions_path = "results/DESKTOP-E3F66CS_2024_8_26_2217_148643/initial_solutions"
    initial_solutions_names = os.listdir(initial_solutions_path)
    
    generations_path = "results/DESKTOP-E3F66CS_2024_8_26_2217_148643/generations"
    generations = os.listdir(generations_path)

    # Extract initial solutions
    initial_solutions = {}
    for instance_name in initial_solutions_names:

        solutions = extract_initial_solutions(initial_solutions_path + "/" + instance_name)

        n_var, k_obj = extract_qap_parameters(instance_name)

        problem = QuadraticAssignment(n_var, k_obj, instance_path + instance_name, "real")

        # Decode solutions
        solutions = np.array([problem.decode_random_keys(solutions[i,:].copy()) for i in range(len(solutions))])

        # Evaluate solutions
        front = np.array([[problem.cost_of_solution(k, solution) for k in range(k_obj)] for solution in solutions])

        #if k_obj == 2:
        #    fig, ax = plt.subplots(1,1)
        #    ax.scatter(front[:,0], front[:,1])
        #    plt.show()
    
        ## ---------------
        # Read the consolidated front per generation.

        if k_obj == 2:
            fig = plt.figure(figsize=(10,5))

            # Make subplots
            gs = gridspec.GridSpec(2, 2, width_ratios=[3,1])
            ax_fronts = fig.add_subplot(gs[:, 0])
            ax_fronts.set_title("Fronts")

            ax_hypervolumes = fig.add_subplot(gs[0, 1])
            ax_hypervolumes.set_title("Hypervolume (First front)")
            
            ax_sizes = fig.add_subplot(gs[1, 1])
            ax_sizes.set_title("Number of points (First front)")

            # Get limits (Expensive)
            limits = [[float("inf"), float("-inf")], [float("inf"), float("-inf")]]
            for gen in generations:
                gen_path = generations_path + "/" + gen + "/" + "Instance_Fronts_" + instance_name.replace(".txt", ".json")

                # Extract data from json file
                with open(gen_path, "r") as f:
                    data = json.load(f)
                    f.close()
                
                num_fronts = len(data.keys()) - 5
                
                for i in range(num_fronts):
                    actual_front = np.array(data[f"Front_{i:03d}"])

                    max_values = np.max(actual_front, axis=0)
                    min_values = np.min(actual_front, axis=0)

                    for j in range(len(max_values)):
                        if limits[j][1] < max_values[j]:
                            limits[j][1] = float(max_values[j])
                        
                        if limits[j][0] > min_values[j]:
                            limits[j][0] = min_values[j]
                    
        for gen in generations:
            gen_path = generations_path + "/" + gen + "/" + "Instance_Fronts_" + instance_name.replace(".txt", ".json")

            # Extract data from json file
            with open(gen_path, "r") as f:
                data = json.load(f)
                f.close()
            
            # Plot fronts
            if data["num_objectives"] == 2:

                num_fronts = len(data.keys()) - 5
                nadir_point = data["nadir_point"]

                for i in range(1):
                    actual_front = np.array(data[f"Front_{i:03d}"])

                    random_color = np.random.random(3)

                    ax_fronts.scatter(actual_front[:,0], actual_front[:,1], s=20, color=random_color)
            
                ax_fronts.scatter(nadir_point[0], nadir_point[1], c="r", label="Nadir Point")

                ax_fronts.set_xlim(limits[0][0]*0.95, limits[0][1]*1.05)
                ax_fronts.set_ylim(limits[1][0]*0.95, limits[1][1]*1.05)

                fig.suptitle(gen)
                ax_fronts.legend()

                plt.tight_layout()
                plt.pause(0.5)
                ax_fronts.cla()
            
        plt.show()
            
