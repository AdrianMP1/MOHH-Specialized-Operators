
import os
import time
import random
import pandas as pd

from tqdm import tqdm
from datetime import datetime

from itertools import product

from evaluation.params import Params, set_params
from evaluation.utilities.instance_utils import instance_paths
from evaluation.utilities.algorithm.MO import compute_nadir_point, compute_hypervolume, non_dominated_sorting_vectorized

from evaluation.problem.instance import Instance

from evaluation.algorithms import MOEA_Decomposition, NSGAII, SMS_MOEA, IBEA

n_experiments = 2
solution_type = "Real"

# Load an already initial population?
initial_population_path = ""

# Solvers
solver_names = ["MOEAD", "NSGAII", "SMSEMOA"]

all_mutation = ["NullMutation", "PM_Mutation"]

def make_experiment_paths(experiment_path: list[str]):

    # Load params
    params = Params()

    folder_name = "evaluation_results"

    dir_path = os.path.join(experiment_path, folder_name)

    for solver in solver_names:

        solver_path = os.path.join(dir_path, solver)

        os.makedirs(solver_path, exist_ok=True)
    
    initial_solutions_path = os.path.join(dir_path, "initial_solutions")
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

    if initial_population_path:
        try:
            old_seeds = []

            with open(os.path.join(initial_population_path, "seeds.txt"), "r") as f:
                for line in f:
                    old_seeds.append(int(line))
            
            seeds = old_seeds
        except:
            pass
    
    return seeds

def save_seeds(seeds: list, folder_path: str):

    file_path = os.path.join(folder_path, "seeds.txt")

    with open(file_path, "w") as f:
        
        for seed in seeds:
            f.write(seed)
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


def run_experiments(experiment_path, results_paths, operators) -> str:

    # Set operators
    # Best, middle, worst

    all_crossover = []

    for i in range(0, len(operators), 3):

        solver_name = solver_names[i // 3]

        all_crossover.append(("operator_template", operators[i],   solver_name, "Best"))
        all_crossover.append(("operator_template", operators[i+1], solver_name, "Middle"))
        all_crossover.append(("operator_template", operators[i+2], solver_name, "Worst"))

    all_crossover.append(("crossover", "SBX_Cross", "None", "Standard"))
    all_crossover.append(("crossover", "PMX_Cross", "None", "Standard"))

    # Set the parameters
    set_params()

    # Make folders
    make_experiment_paths(experiment_path)

    # Load parameters
    params = Params()

    # Get instances
    instances = instance_paths()

    # Total time
    program_time = time.time()

    for instance_path in instances:

        # Instance time
        instance_start = time.time()

        # Initiate an instance object
        instance = Instance(params["MO_POPULATION_SIZE"], params["SOLUTION_TYPE"])

        # Get instance name
        instance_name = instance_path.split("\\")[-1]
        instance_name = instance_name.removesuffix(".txt")

        # Load problem & Create initial population for MO for all experiments
        instance.load_problem(params["PROBLEM_NAME"], instance_path, n_experiments, initial_population_path)

        # Make seeds
        seeds = generate_incremental_seeds(n_experiments)
        save_seeds(seeds, params["FILE_PATH_INITIAL_SOLUTIONS"])

        # Make a consolidated for instance
        consolidated = set()

        # To store fronts for that instance-operators-model
        fronts_model_level = {}

        # For each operators combination
        for combination in get_combinations(all_crossover):

            cross_type = combination[0]
            cross_operator = combination[1]
            mutation_operator = combination[2]
            combination_name = combination[3]
            solver_used = combination[4]

            kind = "real" if cross_operator != "PMX_Cross" else "permutation"

            for solver_name in solver_names:

                # Get solver
                solver = build_solver(solver_name, cross_type, cross_operator, mutation_operator)

                # To store pareto fronts for that instance-operators-model-experiment
                fronts_exp_level = {}

                # Perform N experiments with this configuration
                with_crossover = "Own" if cross_type == "operator_template" else "SBX"
                with_mutation = "NM" if mutation_operator == "NullMutation" else "WM"

                for i in tqdm(range(1, n_experiments+1), desc=f"{solver_used} {combination_name} {with_mutation} {solver_name}"):
                    
                    # Set initial population for MO
                    instance.set_initial_solutions(experiment=i, kind=kind)

                    # Get seed
                    seed = seeds[i-1]

                    # Send the instance to the solver
                    solver.load_instance(instance)

                    # Start model
                    solver.start_model(seed)

                    # Solve
                    results = solver.solve_instance()

                    # Extract results
                    _, pareto_front = results[:2]

                    # Store results
                    fronts_exp_level[f"Experiment {i:03d}"] = pareto_front

                    # Update consolidated
                    consolidated = consolidated.union([tuple(point) for point in pareto_front.tolist()])

                    #* Note: Each iteration of this loop, returns a pareto_front

                fronts_model_level[f"{solver_name}_{combination_name}_{with_mutation}_{cross_type}_{solver_used}"] = fronts_exp_level

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
        best_front = non_dominated_sorting_vectorized(consolidated)[0]

        # Ensure nadir is not computed from a best_front that dominates every other point.
        while len(best_front) <= 2:
            for point in best_front:
                consolidated.remove(point)
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

        # Make dataframe
        dataframe = pd.DataFrame(data)
        dataframe.insert(0, "Experiment", range(1, n_experiments + 1))

        # Get columns
        columns = dataframe.columns

        # Get columns that are not generated operators
        standard_columns = [col for col in columns if col.endswith("None")]

        # Save dataframe
        for solver_name in solver_names:

            new_path = os.path.join(params["RESULTS_PATH"], solver_name, instance_name + ".csv")

            # Get the columns for that specific solver
            subset_columns = [col for col in columns if col.endswith(solver_name)]

            # Add the columns for the standard operators
            subset_columns.extend(standard_columns)
            subset_columns = ["Experiment"] + subset_columns

            subset_df = dataframe[subset_columns]
            subset_df.to_csv(new_path, index=False)

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
