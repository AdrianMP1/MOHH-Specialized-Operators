
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
    

class PMX_Cross(Crossover):

    def __init__(self, prob, **kwargs):
        super().__init__(2, 2, prob, **kwargs)

    def is_permutation(self, arr):

        n = len(arr)

        arr_set = set(arr)

        return len(arr_set) == n and min(arr) == 0 and max(arr) == n-1

    def _do(self, problem, X, **kwargs):

        # Input shape (n_parents, n_matings, n_var)
        _, n_matings, n_var = X.shape

        # Initialize offspring array
        offspring = np.full((2, n_matings, n_var), -1)

        for i in range(n_matings):

            # Get parents
            parent1, parent2 = X[0, i], X[1, i]

            # Choose two crossover points
            cx_point1, cx_point2 = sorted(np.random.choice(n_var, 2, replace=False))

            # Create offspring for current mating by copying crossover segments
            offspring[0, i, cx_point1:cx_point2] = parent1[cx_point1:cx_point2]
            offspring[1, i, cx_point1:cx_point2] = parent2[cx_point1:cx_point2]

            # Mapping function
            def map_genes(o, p, cx1, cx2):
                for j in range(n_var):
                    if j < cx1 or j >= cx2:
                        gene = p[j]
                        while gene in o[cx1:cx2]:
                            gene = p[np.where(o==gene)[0][0]]
                        o[j] = gene

            # Map genes
            map_genes(offspring[0, i], parent2, cx_point1, cx_point2)
            map_genes(offspring[1, i], parent1, cx_point1, cx_point2)

            # Verify they are permutation
            if self.is_permutation(offspring[0, i]) and self.is_permutation(offspring[1, i]):
                continue

            else:
                raise(ValueError)

            # Replace -1 values with genes from the other parent
            #offspring[0, i] = np.where(offspring[0, i] == -1, parent2, offspring[0,i])
            #offspring[1, i] = np.where(offspring[1, i] == -1, parent1, offspring[1,i])

        return offspring
