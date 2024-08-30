
import copy
import time
from tqdm import tqdm

from params import Params

class HyperHeuristic():

    def __init__(self) -> None:
        
        # Load General Parameters
        params = Params()

        # Parameters
        self.seed = params["RANDOM_SEED"]
        self.population_size = params["POPULATION_SIZE"]
        self.num_generations = params["GENERATIONS"]

        self.mo_model_name = params["MO_MODEL"]
        self.mo_cross_prob = params["MO_CROSSOVER_PROBABILITY"]
        self.mo_population_size = params["MO_POPULATION_SIZE"]

        # Genetic Operators
        self.selection = None
        self.crossover = None
        self.mutation = None
        self.replacement = None

        # Population
        self.population = None
        self.already_seen = set()
        self.num_offsprings = params["GENERATION_SIZE"]

        # Instances parameters
        self.problem_name = params["PROBLEM_NAME"]
        self.solution_type = params["SOLUTION_TYPE"]

    def load_operator(self):
        pass

    def load_instances(self):
        pass

    def evaluation_step(self):
        pass

    def compute_metrics(self):
        pass

    def evolutionary_step(self):
        pass

    def run(self):
        pass