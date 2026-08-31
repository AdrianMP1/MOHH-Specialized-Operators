
import os
import time
import random
import numpy as np
import pandas as pd

from tqdm import tqdm
from datetime import datetime

from itertools import product

from mohh.evaluation.params import Params, set_params
from mohh.core.utilities.instance_utils import instance_paths
from mohh.core.utilities.algorithm.MO import compute_nadir_point, compute_hypervolume, non_dominated_sorting_vectorized

from mohh.evaluation.problem.instance import Instance

from mohh.evaluation.algorithms import MOEA_Decomposition, NSGAII, SMS_MOEA, IBEA

solution_type = "Natural"

# Load an already initial population?
initial_population_path = ""

#all_mutation = ["NullMutation", "PM_Mutation"]
all_mutation = ["NullMutation", "Swap_Mutation"]

def make_experiment_paths(experiment_path: list[str]):

    # Load params
    params = Params()

    folder_name = "evaluation_results"

    dir_path = os.path.join(experiment_path, folder_name)

    for solver in params["SOLVERS"]:

        solver_path = os.path.join(dir_path, solver)

        os.makedirs(solver_path, exist_ok=True)
    
    initial_solutions_path = os.path.join(dir_path, "initial_solutions")
    os.makedirs(initial_solutions_path, exist_ok=True)

    params["RESULTS_PATH"] = dir_path
    params["FILE_PATH_INITIAL_SOLUTIONS"] = initial_solutions_path


def generate_incremental_seeds(seeds_number: int, instance_name: str) -> list:

    # Get the initial time-based seed
    start = datetime.now()
    seed = int(start.microsecond)  # Use microsecond as the base seed
    
    seeds = [seed]  # Initialize the list with the first seed
    
    for i in range(1, seeds_number):
        # Add a random increment (e.g., between 1 and 1000) to the previous seed
        increment = random.randint(1, 1000)
        new_seed = seeds[-1] + increment
        seeds.append(new_seed)

    if initial_population_path:
        try:
            old_seeds = []

            with open(os.path.join(initial_population_path, "real", instance_name, "seeds.txt"), "r") as f:
                for line in f:
                    old_seeds.append(int(line))
            
            seeds = old_seeds
        except:
            pass
    
    return seeds


def save_seeds(seeds: list, folder_path: str, instance_name: str):

    real_path = os.path.join(folder_path, "real", instance_name, "seeds.txt")
    permutation_path = os.path.join(folder_path, "permutation", instance_name, "seeds.txt")
    
    with open(real_path, "w") as f:
        
        for seed in seeds:
            f.write(str(seed) + "\n")
        f.close()

    with open(permutation_path, "w") as f:
        
        for seed in seeds:
            f.write(str(seed) + "\n")
        f.close()


def get_combinations(all_crossover):

    # Separate to deal with real and permutation operators
    regular_crossover = all_crossover[:-1]
    special_crossover = all_crossover[-1]

    # Generate combinations for regular elements using real value mutations
    # op -> [Crossover/Template, phenotype, Best/Middle/..., solver_used]
    regular_combinations = [
        (op[0], op[1], mutation, op[3], op[2])
        for op, mutation in product(regular_crossover, all_mutation)
    ]

    # Generate combinations for the permutation operators with permutation mutations.
    special_combinations = [
        (special_crossover[0], special_crossover[1], "NullMutation", special_crossover[3], special_crossover[2]),
        (special_crossover[0], special_crossover[1], "Swap_Mutation", special_crossover[3], special_crossover[2])
    ]

    # Merge combinations
    all_combinations = regular_combinations + special_combinations

    # Sort combined list
    sorted_combinations = sorted(all_combinations, key = lambda x: (x[2], x[0], x[4], x[3], x[1]))

    #combinations = [(op[0], op[1], mutation, op[3], op[2]) for op, mutation in product(all_crossover, all_mutation)]

    #sorted_combinations = sorted(combinations, key = lambda x: (x[2], x[0], x[4], x[3], x[1]))
    return sorted_combinations


def build_solver(solver_name, cross_type, crossover, mutation):

    params = Params()
    
    if solver_name == "MOEAD":
        solver = MOEA_Decomposition()
        cross_prob = params["MOEAD_CROSSOVER_PROBABILITY"]
        mutation_prob = params["MOEAD_MUTATION_PROBABILITY"]
    
    elif solver_name == "NSGAII":
        solver = NSGAII()
        cross_prob = params["NSGA_CROSSOVER_PROBABILITY"]
        mutation_prob = params["NSGA_MUTATION_PROBABILITY"]
                
    elif solver_name == "SMSEMOA":
        solver = SMS_MOEA()
        cross_prob = params["SMS_CROSSOVER_PROBABILITY"]
        mutation_prob = params["SMS_MUTATION_PROBABILITY"]
    
    else:
        raise(ValueError)
    
    # LOAD CROSSOVER
    if cross_type == "operator_template":
        solver.load_operator(cross_type, "HH_Operator",
                             operator=crossover,
                             solution_type=solution_type,
                             prob=cross_prob)
    else:
        solver.load_operator(cross_type, crossover, prob=cross_prob)
    
    # LOAD MUTATION
    solver.load_operator("mutation", mutation, prob=mutation_prob)

    return solver


def normalize(data: np.ndarray):

    if data.shape[1] > 1:
        return (data - np.min(data, axis=0)) / (np.max(data, axis=0) - np.min(data, axis=0))
    
    else:
        return (data - min(data)) / (max(data) - min(data))


def normalize_values(data: np.ndarray, vmin: float, vmax: float):

    return (data - vmin) / (vmax - vmin)


def write_front(front: np.ndarray, file_path: str):
    """
    Take a 2D numpy array and write it in disk
    
    Params
    """
    
    # Get the shape of the array
    N, M = front.shape

    # Open file to write
    with open(file_path, "w") as file:

        # Write header
        file.write(f"# {N} {M}\n")

        # Write each row
        for row in front:
            # Format numbers to scientific notation
            formatted_point = " ".join(f"{num:1.6e}" for num in row)
            file.write(f"{formatted_point}\n")
    
        file.close()


def run_experiments(experiment_path, results_paths, operators, overrides: dict = None) -> str:

    # Set the parameters
    set_params(overrides)

    # Load parameters
    params = Params()
    solver_names = params["SOLVERS"]
    n_experiments = params["N_EXPERIMENTS"]

    # Set operators
    # Best, middle, worst

    all_crossover = []

    for i in range(0, len(operators), 3):

        solver_name = solver_names[i // 3]

        all_crossover.append(("operator_template", operators[i],   solver_name, "Best"))
        all_crossover.append(("operator_template", operators[i+1], solver_name, "Middle"))
        all_crossover.append(("operator_template", operators[i+2], solver_name, "Worst"))

    #all_crossover.append(("crossover", "SBX_Cross", "None", "Standard"))
    all_crossover.append(("crossover", "PMX_Cross", "None", "Standard"))
    all_crossover.append(("crossover", "CX_Cross", "None", "Standard"))

    # Make folders
    make_experiment_paths(experiment_path)

    # Get instances
    instances = instance_paths(train=False)

    # Total time
    program_time = time.time()

    for instance_path in instances:

        # Instance time
        instance_start = time.time()

        # Initiate an instance object
        instance = Instance(params["MO_POPULATION_SIZE"], params["SOLUTION_TYPE"])

        # Get instance name
        instance_name = instance_path.replace("\\", "/").split("/")[-1]
        instance_name = instance_name.removesuffix(".txt")

        # Load problem & Create initial population for MO for all experiments
        instance.load_problem(params["PROBLEM_NAME"], instance_path, n_experiments, initial_population_path)

        # Make seeds
        seeds = generate_incremental_seeds(n_experiments, instance_name)
        save_seeds(seeds, params["FILE_PATH_INITIAL_SOLUTIONS"], instance_name)

        # Make a consolidated for instance
        consolidated_10k = set()
        consolidated_30k = set()
        consolidated_50k = set()

        # To store fronts for that instance-operators-model
        fronts_model_level = {"10k":{},
                              "30k":{},
                              "50k":{}}

        # For each operators combination
        for combination in get_combinations(all_crossover):

            cross_type = combination[0]
            cross_operator = combination[1]
            mutation_operator = combination[2]
            combination_name = combination[3]
            solver_used = combination[4]

            #kind = "real" if cross_operator != "PMX_Cross" else "permutation"
            kind = "permutation"

            for solver_name in solver_names:

                # Get solver
                solver = build_solver(solver_name, cross_type, cross_operator, mutation_operator)

                # To store pareto fronts for that instance-operators-model-experiment
                fronts_exp_level = {"10k":{},
                                    "30k":{},
                                    "50k":{}}

                # Perform N experiments with this configuration
                with_crossover = "Own" if cross_type == "operator_template" else "SBX"
                with_mutation = "NM" if mutation_operator == "NullMutation" else "WM"

                for i in tqdm(range(1, n_experiments+1), desc=f"{solver_used} {combination_name} {with_mutation} {solver_name}"):
                    
                    # Set initial population for MO
                    instance.set_initial_solutions(experiment=i, kind=kind)

                    # Get seed
                    seed = seeds[i-1]
                    random.seed(seed)
                    np.random.seed(seed)

                    # Send the instance to the solver
                    solver.load_instance(instance)

                    # Start model
                    solver.start_model(seed)

                    # Solve
                    results = solver.solve_instance()

                    # Extract results
                    pareto_front_10k = results["10k"]
                    pareto_front_30k = results["30k"]
                    pareto_front_50k = results["50k"]
                    #_, pareto_front = results[:2]

                    # Store results
                    fronts_exp_level["10k"][f"Experiment {i:03d}"] = pareto_front_10k
                    fronts_exp_level["30k"][f"Experiment {i:03d}"] = pareto_front_30k
                    fronts_exp_level["50k"][f"Experiment {i:03d}"] = pareto_front_50k
                    #fronts_exp_level[f"Experiment {i:03d}"] = pareto_front

                    # Update consolidated
                    consolidated_10k = consolidated_10k.union([tuple(point) for point in pareto_front_10k.tolist()])
                    consolidated_30k = consolidated_30k.union([tuple(point) for point in pareto_front_30k.tolist()])
                    consolidated_50k = consolidated_50k.union([tuple(point) for point in pareto_front_50k.tolist()])
                    
                    #consolidated = consolidated.union([tuple(point) for point in pareto_front.tolist()])

                    #* Note: Each iteration of this loop, returns a pareto_front

                if combination_name == "Standard" and cross_operator == "SBX_Cross":
                    combination_name = "SBX"
                elif combination_name == "Standard" and cross_operator == "PMX_Cross":
                    combination_name = "PMX"
                elif combination_name == "Standard" and cross_operator == "CX_Cross":
                    combination_name = "CX"

                fronts_model_level["10k"][f"{solver_name}_{combination_name}_{with_mutation}_{solver_used}"] = fronts_exp_level["10k"]
                fronts_model_level["30k"][f"{solver_name}_{combination_name}_{with_mutation}_{solver_used}"] = fronts_exp_level["30k"]
                fronts_model_level["50k"][f"{solver_name}_{combination_name}_{with_mutation}_{solver_used}"] = fronts_exp_level["50k"]
                #fronts_model_level[f"{solver_name}_{combination_name}_{with_mutation}_{solver_used}"] = fronts_exp_level

                del solver

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
        best_front_10k = non_dominated_sorting_vectorized(consolidated_10k)[0]
        best_front_30k = non_dominated_sorting_vectorized(consolidated_30k)[0]
        best_front_50k = non_dominated_sorting_vectorized(consolidated_50k)[0]
        #best_front = non_dominated_sorting_vectorized(consolidated)[0]

        # Ensure nadir is not computed from a best_front that dominates every other point.
        def comprobate(front, consol):
            while len(front) <= 2:
                for point in front:
                    consol.remove(point)
                front = non_dominated_sorting_vectorized(consol)[0]

            return front

        best_front_10k = comprobate(best_front_10k, consolidated_10k)
        best_front_30k = comprobate(best_front_30k, consolidated_30k)
        best_front_50k = comprobate(best_front_50k, consolidated_50k)

        min_10k, max_10k = np.min(best_front_10k, axis=0), np.max(best_front_10k, axis=0)
        min_30k, max_30k = np.min(best_front_30k, axis=0), np.max(best_front_30k, axis=0)
        min_50k, max_50k = np.min(best_front_50k, axis=0), np.max(best_front_50k, axis=0)
        boundaries = {"10k": [min_10k, max_10k],
                      "30k": [min_30k, max_30k],
                      "50k": [min_50k, max_50k]}

        best_front_10k_norm = normalize_values(best_front_10k, min_10k, max_10k)
        best_front_30k_norm = normalize_values(best_front_30k, min_30k, max_30k)
        best_front_50k_norm = normalize_values(best_front_50k, min_50k, max_50k)

        #while len(best_front) <= 2:
        #    for point in best_front:
        #        consolidated.remove(point)
        #    best_front = non_dominated_sorting_vectorized(consolidated)[0]

        # Compute Nadir point
        nadir_point = np.array([1.1, 1.1])
        #nadir_point = compute_nadir_point(set(best_front))

        for evals in ["10k", "30k", "50k"]:
            # Dataframe data
            data = {}

            front_save_path = os.path.join(params["RESULTS_PATH"], solver_name, evals, "fronts", instance_name)
            os.makedirs(front_save_path, exist_ok=True)

            for model_operators in fronts_model_level[evals].keys():

                column_data = []

                for experiment in fronts_model_level[evals][model_operators].keys():
                
                    front = fronts_model_level[evals][model_operators][experiment]

                    front = normalize_values(front, boundaries[evals][0], boundaries[evals][1])

                    hv = compute_hypervolume(nadir_point, front)

                    column_data.append(hv)
                
                median_value = np.median(column_data)
                median_indx = column_data.index(median_value) + 1
                median_front = fronts_model_level[evals][model_operators][f"Experiment {median_indx:03d}"]
                median_front_norm = normalize_values(median_front, boundaries[evals][0], boundaries[evals][1])

                # Save median front
                
                write_front(median_front, os.path.join(front_save_path, f"{model_operators}.pof"))
                write_front(median_front_norm, os.path.join(front_save_path, f"{model_operators}_norm.pof"))

                data[model_operators] = column_data
            
            # Write the best front
            if evals == "10k":
                best = best_front_10k
                best_norm = best_front_10k_norm
            elif evals == "30k":
                best = best_front_30k
                best_norm = best_front_30k_norm
            elif evals == "50k":
                best = best_front_50k
                best_norm = best_front_50k_norm

            write_front(np.array(best), os.path.join(front_save_path, f"best_front_consolidated.pof"))
            write_front(np.array(best_norm), os.path.join(front_save_path, f"best_front_consolidated_norm.pof"))

            # Make dataframe
            dataframe = pd.DataFrame(data)
            dataframe.insert(0, "Experiment", range(1, n_experiments + 1))

            # Get columns
            columns = dataframe.columns

            # Get columns that are not generated operators
            standard_columns = [col for col in columns if col.endswith("None")]

            # Save dataframe
            for solver_name in solver_names:

                new_path = os.path.join(params["RESULTS_PATH"], solver_name, evals)
                os.makedirs(new_path, exist_ok=True)
                save_path = os.path.join(new_path, instance_name + ".csv")

                # Get the columns for that specific solver
                subset_columns = [col for col in columns if col.endswith(solver_name)]

                # Add the columns for the standard operators
                subset_columns.extend(standard_columns)
                subset_columns = ["Experiment"] + subset_columns

                subset_df = dataframe[subset_columns]
                subset_df.to_csv(save_path, index=False)

        #new_path = os.path.join(params["RESULTS_PATH"], instance_name + ".csv")
        #dataframe.to_csv(new_path, index=False)

        # Instance total time
        instance_time = time.time() - instance_start
        instance_minutes = round(instance_time / 60, 2)
        instance_hours = round(instance_time / 3600, 2)
        
        print(f"\nInstance: {instance_name}, Minutes: {instance_minutes}, Hours: {instance_hours}\n")

    # * Now, we have K dataframes, one for each instance.

    program_total_time = time.time() - program_time
    minutes = round(program_total_time /60 , 4)
    hours = round(program_total_time / 3600, 4)

    print(f"\nProgram Time - Minutes: {minutes}, Hours: {hours}\n")

    return params["RESULTS_PATH"]


if __name__ == "__main__":
    
    # First execute the experiments, and generate data from it
    run_experiments()
