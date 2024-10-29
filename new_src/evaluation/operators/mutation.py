
import random
import numpy as np

from pymoo.core.mutation import Mutation
from pymoo.core.population import Population
from pymoo.operators.mutation.pm import PolynomialMutation

class PM_Mutation(Mutation):

    def __init__(self, prob, **kwargs) -> None:
        
        self.mutation = PolynomialMutation(prob)

        super().__init__(prob, **kwargs)


    def _do(self, problem, X, **kwargs):

        # Input shape (n_individuals, n_var)

        pop = Population.new(X=X)

        problem.xu = np.array([1.0 for _ in range(problem.n_var)])
        problem.xl = np.array([0.0 for _ in range(problem.n_var)])

        off = self.mutation(problem, pop)
        Xp = off.get("X")

        return Xp
    