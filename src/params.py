
import os
import random

from time import time
from datetime import datetime
from socket import gethostname

hostname = gethostname().split(".")
machine_name = hostname[0]

hh_params = {
    # ------------
    # EVOLUTIONARY PARAMETERS
    'POPULATION_SIZE': 50,
    'GENERATIONS': 30,
    'ELITE_SIZE': 20,

    # ------------
    # INDIVIDUALS PARAMETERS
    'MAX_TREE_DEPTH': 90,
    'MAX_INIT_TREE_DEPTH': 10,
    'MIN_INIT_TREE_DEPTH': None,

    'MAX_TREE_NODES': None,
    
    'CODON_SIZE': 1000,
    'INIT_GENOME_LENGTH': 200,
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
    'TOURNAMENT_SIZE': 2,

    # ------------
    # CROSSOVER
    # Operator
    'CROSSOVER': 'KPointCrossover',
    # Set crossover probability
    'CROSSOVER_PROBABILITY': 1.0,
    # Operator parameters
    'K_POINTS': 1,

    # ------------
    # MUTATION
    # Operator
    'MUTATION': 'BitFlipMutation',
    # Set mutation probability
    'MUTATION_PROBABILITY': 0.1,
    # Operator parameters

    # ------------
    # REPLACEMENT
    # Operator
    'REPLACEMENT': "HHReplacement"
}

mo_params = {
    # ------------
    # MOEA MODEL
    'MO_MODEL': "MOEAD",

    # ------------
    # MODEL Parameters
    'NUM_NEGIHBORS': 10,
    'PROB_NEIGHBORS': 0.9,

    # ------------
    # EVOLUTIONARY PARAMETERS
    'MO_POPULATION_SIZE': 105,
    'MO_GENERATIONS': 100,

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
    'SOLUTION_TYPE': "Real",
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
    'GRAMMAR_FILE': "original.bnf",

    # Set the number of depths permutations are calculated for
    # (starting from the minimum path of the grammar).
    # Mainly for use with the grammar analyser script.
    'PERMUTATION_RAMPS': 5,
}

misc_params = {
    # ------------
    # Set machine name
    'MACHINE': machine_name
}

params = dict(hh_params, **mo_params, **problem_params, **grammar_params, **misc_params)

