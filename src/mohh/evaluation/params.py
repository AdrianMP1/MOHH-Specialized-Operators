
import os
import random

from time import time
from datetime import datetime
from socket import gethostname

hostname = gethostname().split(".")
machine_name = hostname[0]

mo_params = {


    # Evolutionary parameters
    'MO_POPULATION_SIZE': 105,
    'MO_GENERATIONS': 500,


    # ----------------
    # MOEAD Parameters
    'NUM_NEGIHBORS': 10,
    'PROB_NEIGHBORS': 0.9,

    # Crossover
    'MOEAD_CROSSOVER': None, # SBX
    'MOEAD_CROSSOVER_PROBABILITY': 1.0,

    # Mutation
    'MOEAD_MUTATION': "PM_Mutation", # PM
    'MOEAD_MUTATION_PROBABILITY': 0.05,
    'MOEAD_MUTATION_BOOL': False,


    # ----------------
    # NSGAII Parameters
    
    # Crossover
    'NSGA_CROSSOVER': None, # SBX
    'NSGA_CROSSOVER_PROBABILITY': 1.0,

    # Mutation
    'NSGA_MUTATION': "PM_Mutation", # PM
    'NSGA_MUTATION_PROBABILITY': 0.05,
    'NSGA_MUTATION_BOOL': False,

    # ----------------
    # SMS-EMOA Parameters

    # Crossover
    'SMS_CROSSOVER': None,
    'SMS_CROSSOVER_PROBABILITY': 1.0,

    # Mutation
    'SMS_MUTATION': "PM_Mutation",
    'SMS_MUTATION_PROBABILITY': 0.05,
    'SMS_MUTATION_BOOL': False

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
    'DATASET_TRAIN': None,
    'DATASET_TEST': "test",
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

params_dict = dict(mo_params, **problem_params, **grammar_params, **misc_params)

class Params:
    _instance = None # Store singleton instance
    _params = {}     # Store the parameters

    def __new__(cls):
        # Check if an instance already exists
        if not cls._instance:
            # Create a new instance
            cls._instance = super(Params, cls).__new__(cls)
        
        # Return singleton instance
        return cls._instance

    # Overload operators to make the class
    # similar to a python dictionary
    
    # Get attributes
    def __getitem__(self, key):
        return self._params.get(key)
    
    # Set attributes
    def __setitem__(self, key, value):
        self._params[key] = value

    # Access params
    def get_params(self):
        return self._params
    
    # Update the whole params dictionary
    def update_params(self, new_params):
        self._params.update(new_params)

    # Get keys
    def keys(self):
        return self._params.keys()
    
    # Get values
    def values(self):
        return self._params.values()
    
    # Get items
    def items(self):
        return self._params.items()
    
    # Reset singleton
    @classmethod
    def reset_instance(cls):
        cls._instance = None
    

def load_params():
    pass


def set_params():

    # Initialize singleton object with params
    params = Params()
    params.update_params(params_dict)

    # Load Grammar & Saver
    from mohh.evaluation.representation import grammar
    #from saver import PopulationSaver, MyLogger

    # Get actual time
    start = datetime.now()

    # Set random seed
    if params["RANDOM_SEED"] is None:
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
    #if params["SAVE"]:
        #save = PopulationSaver()
        #logger = MyLogger().get_logger()
        #logger.info(f"Start")

    # Set Genome operations
    params["GENOME_OPERATIONS"] = True
    
    # Parse grammar file and set grammar class
    params["BNF_GRAMMAR"] = grammar.Grammar(
        os.path.join("grammars", params["GRAMMAR_FILE"])
    )
