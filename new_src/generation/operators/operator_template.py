
import numpy as np

from pymoo.core.mutation import Mutation
from pymoo.core.crossover import Crossover
from generation.utilities.algorithm.HH_functions import *

class HH_Operator(Crossover):
    def __init__(self, operator: str, solution_type: str, n_parents: int=2,
                n_offsprings: int=2, prob: float=1.0, **kwargs):
        """
        @param operator: Phenotype operator.
        @param solution_type: Natural or Real.
        """
        super().__init__(n_parents, n_offsprings, prob, **kwargs)

        # Load phenotype expression
        self.expression = operator

        # Work with natural or real numbers
        self.solution_type = solution_type.lower()
    
    def _do(self, problem, X, **kwargs):
        """
        Apply the operator following Pymoo documentation.
        """
        # X has shape (n_parents, n_matings, n_var)
        _, n_matings, n_var = X.shape

        # Output with shape (n_offsprings, n_matings, n_var)
        Y = np.full_like(X, None, dtype=object)

        for k in range(n_matings):
            # x and y are 1D arrays, required to evaluate
            x, y = X[0, k], X[1, k]

            # Evaluate with operator
            child = eval(self.expression)

            if self.solution_type == "real":
                Y[0, k], Y[1, k] = child, 1 - child
            
            else:
                Y[0, k], Y[1, k] = child, child[::-1]
        return Y
    

class NullMutation(Mutation):

    def __init__(self, prob=0, prob_var=None, **kwargs) -> None:
        super().__init__(prob, prob_var, **kwargs)

    def _do(self, problem, X, **kwargs):
        """
        Do nothing.
        """
        # Return individuals.
        return X