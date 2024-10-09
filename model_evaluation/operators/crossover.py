
import numpy as np

from pymoo.core.individual import Individual
from pymoo.core.crossover import Crossover
from pymoo.operators.crossover.sbx import SBX


class SBX_Cross(Crossover):

    def __init__(self, prob, **kwargs):
        self.crossover = SBX(prob)
        super().__init__(2, 2, prob, **kwargs)

    def _do(self, problem, X, **kwargs):
    
        # Input shape (n_parents, n_matings, n_var)
        _, n_matings, n_var = X.shape

        problem.xu = np.array([1.0 for _ in range(problem.n_var)])
        problem.xl = np.array([0.0 for _ in range(problem.n_var)])

        parents = [[Individual(X=X[0,i]), Individual(X=X[1,i])] for i in range(X.shape[1])]

        off = self.crossover.do(problem, parents)
        Xp = off.get("X")
        Xp = Xp.reshape(2, n_matings, n_var)

        # Return a numpy array with shape (n_parents, n_matings, n_var)
        return Xp
    


