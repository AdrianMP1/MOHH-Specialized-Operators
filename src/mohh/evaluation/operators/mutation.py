
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
    

class Swap_Mutation(Mutation):

    def __init__(self, prob, **kwargs) -> None:
        super().__init__(prob, **kwargs)

        self.probability = prob

    def _do(self, problem, X, **kwargs):
        
        # X -> Input shape (n_individuals, n_var)
        n_individuals, n_var = X.shape

        # Create a copy of X to mutate individuals
        mutated_X = np.copy(X)

        if self.probability > 0:

            # For each individual
            for i in range(n_individuals):

                # Apply mutation based on the mutation rate
                if np.random.rand() < self.probability:

                    # Select two positions to swap
                    pos1, pos2 = np.random.choice(n_var, 2, replace=False)

                    # Swap
                    mutated_X[i, pos1], mutated_X[i, pos2] = mutated_X[i, pos2], mutated_X[i, pos1]

        return mutated_X
