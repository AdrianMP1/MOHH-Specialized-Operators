
import os
import time
import random
import pandas as pd

from tqdm import tqdm
from datetime import datetime

from params import Params, set_params
from utilities.instance_utils import instance_paths
from utilities.algorithm.MO import compute_nadir_point, compute_hypervolume, non_dominated_sorting_vectorized

from problem.instance import Instance

from algorithms import MOEA_Decomposition, NSGAII, IBEA

n_experiments = 10
solution_type = "Real"

my_operator = "masked_cross(y,sin(sin(sin(x))))"

def make_experiment_paths():

    # Load params
    params = Params()

    folder_name = params["TIME_STAMP"]

    dir_path = os.path.join("results_evaluation", folder_name)
    initial_solutions_path = os.path.join(dir_path, "initial_solutions")

    os.makedirs(dir_path, exist_ok=True)
    os.makedirs(initial_solutions_path, exist_ok=True)

    params["RESULTS_PATH"] = dir_path
    params["FILE_PATH_INITIAL_SOLUTIONS"] = initial_solutions_path


def generate_incremental_seeds(seeds_number: int) -> list:

    # Get the initial time-based seed
    start = datetime.now()
    seed = int(start.microsecond)  # Use microsecond as the base seed
    
    seeds = [seed]  # Initialize the list with the first seed
    
    for i in range(1, seeds_number):
        # Add a random increment (e.g., between 1 and 1000) to the previous seed
        increment = random.randint(1, 1000)
        new_seed = seeds[-1] + increment
        seeds.append(new_seed)
    
    return seeds

def run_experiments():

    # Set the parameters
    set_params()

    # Make folders
    make_experiment_paths()

    # Load parameters
    params = Params()

    # Get instances
    instances = instance_paths()

    for instance_path in instances:

        # Instance time
        instance_start = time.time()

        # Initiate an instance object
        instance = Instance(params["MO_POPULATION_SIZE"], params["SOLUTION_TYPE"])

        # Get instance name
        instance_name = instance_path.split("/")[-1]
        instance_name = instance_name.removesuffix(".txt")

        # Load problem & Create initial population for MO for all experiments
        instance.load_problem(params["PROBLEM_NAME"], instance_path, n_experiments)

        # Make seeds
        seeds = generate_incremental_seeds(n_experiments)

        # Make a consolidated for instance
        consolidated = set()

        # To store fronts for that instance-operators-model
        fronts_model_level = {}

        # For each algorithm...
        for operator_kind in ["Our_withMutation", "Our_noMutation", "Standar"]:

            if operator_kind == "Our_withMutation":
                # Load operator
                operator_type = "operator_template"
                cross_operator = my_operator
                mutation_operator = "PM_Mutation"

            elif operator_kind == "Our_noMutation":
                # Load operator
                operator_type = "operator_template"
                cross_operator = my_operator
                mutation_operator = "NullMutation"

            else:
                operator_type = "crossover"
                cross_operator = "SBX_Cross"
                mutation_operator = "PM_Mutation"

            for algorithm_name in ["NSGAII", "MOEAD"]:

                # Make solver
                if algorithm_name == "MOEAD":
                    solver = MOEA_Decomposition()
                    cross_prob = params["MOEAD_CROSSOVER_PROBABILITY"]
                    mutation_prob = params["MOEAD_MUTATION_PROBABILITY"]

                elif algorithm_name == "NSGAII":
                    solver = NSGAII()
                    cross_prob = params["NSGA_CROSSOVER_PROBABILITY"]
                    mutation_prob = params["NSGA_MUTATION_PROBABILITY"]
                
                if "Our" in operator_kind:
                    solver.load_operator(operator_type, "HH_Operator",
                                         operator=cross_operator,
                                         solution_type=solution_type,
                                         prob=cross_prob)
                    
                else:
                    solver.load_operator(operator_type, cross_operator,
                                          prob=cross_prob)
                    
                solver.load_operator("mutation", mutation_operator,
                                         prob=mutation_prob)

                # To store pareto fronts for that instance-operators-model-experiment
                fronts_exp_level = {}

                # Perform N experiments with this configuration
                for i in tqdm(range(1, n_experiments+1), desc=f"{algorithm_name}_{operator_kind}"):

                    # Set initial population for MO
                    instance.set_initial_solutions(experiment=i)

                    # Get seed
                    seed = seeds[i-1]

                    # Send the instance to the MO solver
                    solver.load_instance(instance)
                    # Start the model
                    solver.start_model(seed)

                    # Solve the instance
                    results = solver.solve_instance()

                    # Extract results
                    pareto_set, pareto_front = results[:2]

                    # Store results
                    fronts_exp_level[f"Experiment {i:03d}"] = pareto_front

                    # Update consolidated
                    consolidated = consolidated.union([tuple(point) for point in pareto_front.tolist()])

                    #* Note: Each iteration of this loop, returns a pareto_front
                
                fronts_model_level[f"{algorithm_name}_{operator_kind}"] = fronts_exp_level

                #* At this point, we have N pareto fronts for that model
                #* with those operators in that instance.
            
            #* Here we end with M (number of models) * N pareto fronts
            #* for all models with those operators.

        #* Now we have 3 * M * N pareto fronts for all models all comb of operators
        #* For one instance.

        #* We need to create a consolidated here, get its nadir.
        #* Compute HVs for all comb of operators, for all models and all experiments.

        #* Make a dataframe for that instance

        # Get the best front
        best_front = non_dominated_sorting_vectorized(consolidated)[0]

        # Compute Nadir point
        nadir_point = compute_nadir_point(set(best_front))

        # Dataframe data
        data = {}

        for model_operators in fronts_model_level.keys():

            column_data = []

            for experiment in fronts_model_level[model_operators].keys():

                front = fronts_model_level[model_operators][experiment]

                hv = compute_hypervolume(nadir_point, front)

                column_data.append(hv)

            data[model_operators] = column_data

        dataframe = pd.DataFrame(data)
        dataframe.insert(0, "Experiment", range(1, n_experiments + 1))

        # Save dataframe
        new_path = os.path.join(params["RESULTS_PATH"], instance_name + ".csv")
        dataframe.to_csv(new_path, index=False)

        # Instance total time
        instance_time = time.time() - instance_start
        instance_minutes = round(instance_time / 60, 2)
        instance_hours = round(instance_time / 3600, 2)
        
        print(f"\nInstance: {instance_name}, Minutes: {instance_minutes}, Hours: {instance_hours}\n")

    # * Now, we have K dataframes, one for each instance.


if __name__ == "__main__":
    run_experiments()