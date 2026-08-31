
import os
import random

from time import time
from datetime import datetime
from socket import gethostname

from mohh.core.params import Params

hostname = gethostname().split(".")
machine_name = hostname[0]

hh_params = {
    # ------------
    # EVOLUTIONARY PARAMETERS
    'POPULATION_SIZE': 50,
    'GENERATIONS': 30,
    'ELITE_SIZE': 15,

    # ------------
    # INDIVIDUALS PARAMETERS
    'MAX_TREE_DEPTH': 90,
    'MAX_INIT_TREE_DEPTH': 10,
    'MIN_INIT_TREE_DEPTH': None,

    'MAX_TREE_NODES': None,
    
    'CODON_SIZE': 255,
    'INIT_GENOME_LENGTH': 100,
    'MAX_GENOME_LENGTH': None,
    'MAX_WRAPS': 0,

    # ------------
    # INITIALIZATION
    # Operator
    'INITIALIZATION': "Rvd",
    
    # ------------
    # SELECTION
    # Operator
    'SELECTION': "Tournament",
    # Operator parameters
    'TOURNAMENT_SIZE': 3,

    # ------------
    # CROSSOVER
    # Operator
    'CROSSOVER': 'KPointCrossover',
    # Set crossover probability
    'CROSSOVER_PROBABILITY': 1.0,
    # Operator parameters
    'CROSSOVER_K_POINTS': 2,
    'CROSSOVER_PARENTS': 2,

    # ------------
    # MUTATION
    # Operator
    'MUTATION': 'BitFlipMutation',
    # Set mutation probability
    'MUTATION_PROBABILITY': 0.01,
    # Operator parameters

    # ------------
    # REPLACEMENT
    # Operator
    'REPLACEMENT': "HHReplacement"
}

mo_params = {
    # ------------
    # MOEA MODEL
    #'MO_MODEL': "MOEAD",
    #'MO_MODEL': "NSGAII",
    'MO_MODEL': "SMSEMOA",

    # ------------
    # MODEL Parameters
    'NUM_NEGIHBORS': 10,
    'PROB_NEIGHBORS': 0.9,

    # ------------
    # EVOLUTIONARY PARAMETERS
    'MO_POPULATION_SIZE': 105,
    'MO_GENERATIONS': 300,

    # ------------
    # CROSSOVER
    # Operator
    'MO_CROSSOVER': None,
    # Set crossover probability
    'MO_CROSSOVER_PROBABILITY': 1.0,

    # ------------
    # MUTATION
    # Operator
    'MO_MUTATION': "SwapMutation",
    # Set mutation probability
    'MO_MUTATION_PROBABILITY': 0.01,
    # Define if mutation will be active
    'MO_MUTATION_BOOL': False,
}

problem_params = {
    # ------------
    # Problem class
    'PROBLEM_NAME': "QAP",
    'SOLUTION_TYPE': "Natural",
    # Define if maximize or minimize.
    # True for maximize, False for minimize
    'OPTIMIZATION_KIND': False,

    # ------------
    # Select problem dataset
    'DATASET': "mqap",
    'DATASET_TRAIN': "train",
    'DATASET_TEST': None,
}

grammar_params = {
    # ------------
    # GRAMMAR
    'GRAMMAR_FILE': "naturals.bnf",

    # Set the number of depths permutations are calculated for
    # (starting from the minimum path of the grammar).
    # Mainly for use with the grammar analyser script.
    'PERMUTATION_RAMPS': 5,
}

misc_params = {
    # ------------
    # Set machine name
    'MACHINE': machine_name,

    "SAVE": True
}

params_dict = dict(hh_params, **mo_params, **problem_params, **grammar_params, **misc_params)

def load_params():
    pass


def set_params(experiment_path: str, current_model: str):

    # Initialize singleton object with params
    params = Params()
    params.update_params(params_dict)

    # Load Grammar & Saver
    from mohh.core.representation import grammar
    from mohh.generation.saver import PopulationSaver, MyLogger

    # Get actual time
    start = datetime.now()

    # Set random seed
    #if params["RANDOM_SEED"] is None:
    params["RANDOM_SEED"] = int(start.microsecond)

    random.seed(params["RANDOM_SEED"])

    # Generate a timestamp to name folder
    hm = "%02d%02d" % (start.hour, start.minute)
    params["TIME_STAMP"] = "_".join([gethostname(),
                                     str(start.year),
                                     str(start.month),
                                     str(start.day), hm,
                                     str(params["RANDOM_SEED"])])
    
    print("\nStart:\t", start, "\n")

    # Generate save folders
    if params["SAVE"]:
        save = PopulationSaver(experiment_path, current_model)
        logger = MyLogger().get_logger()
        logger.info(f"Start")

    # Set Genome operations
    params["GENOME_OPERATIONS"] = True

    # Set the generation size (Elitism)
    params["GENERATION_SIZE"] = params["POPULATION_SIZE"] - \
                                params["ELITE_SIZE"]
    
    # Parse grammar file and set grammar class
    params["BNF_GRAMMAR"] = grammar.Grammar(
        os.path.join("grammars", params["GRAMMAR_FILE"])
    )
