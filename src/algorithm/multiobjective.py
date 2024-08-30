
import numpy as np

from params import Params

from pymoo.algorithms.moo.moead import MOEAD
from pymoo.core.evaluator import Evaluator
from pymoo.core.population import Population
from pymoo.util.ref_dirs import get_reference_directions

class MOSolver():
    
    def __init__(self, seed) -> None:
        """
        """

        # Load parameters
        params = Params()

        # Multiobjective parameters
        self.generations = params["MO_GENERATIONS"]
        self.seed = seed

        # Multiobjective operators
        self.crossover = None
        self.mutation = None
        self.with_mutation = params["MO_MUTATION_BOOL"]

        self.pop = None
        self.problem = None

    def __call__(self):
        pass

    def load_operator(self):
        pass

    def load_instance(self):
        pass

    def start_model(self):
        pass

    def solve_instance(self):
        pass