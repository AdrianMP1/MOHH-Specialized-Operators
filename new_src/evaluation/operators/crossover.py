
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


class CX_Cross(Crossover):

    def __init__(self, prob, **kwargs):
        super().__init__(2, 2, prob, **kwargs)

    def is_permutation(self, arr):
        n = len(arr)
        arr_set = set(arr)
        return len(arr_set) == n and min(arr) == 0 and max(arr) == n - 1
    
    def _do(self, problem, X, **kwargs):
        # Input shape (n_parents, n_matings, n_var)
        _, n_matings, n_var = X.shape

        # Initialize offspring array
        offspring = np.full((2, n_matings, n_var), -1)

        for i in range(n_matings):
            # Get parents
            parent1, parent2 = X[0, i], X[1, i]

            size = len(parent1)

            # Select a starting index
            indx = np.random.randint(size)
            start_indx = indx

            while True:
                # Copy the element of indx to child
                offspring[0, i, indx] = parent1[indx]
                offspring[1, i, indx] = parent2[indx]

                # Find the element from the other parent to the selected element
                val = parent2[indx]
                ## update indx
                indx = np.where(parent1 == val)[0][0]

                # Break the cycle when starting index is reached
                if indx == start_indx:
                    break
            
            # Copy the remaining elements from the other parent
            for j in range(size):
                if offspring[0, i, j] == -1:
                    offspring[0, i, j] = parent2[j]
                if offspring[1, i, j] == -1:
                    offspring[1, i, j] = parent1[j]

        # Verify permutations
        if not (self.is_permutation(offspring[0, i]) and self.is_permutation(offspring[1, i])):
            raise ValueError("Offspring are not valid permutations!")
        
        return offspring
"""

    def _do(self, problem, X, **kwargs):
        # Input shape (n_parents, n_matings, n_var)
        _, n_matings, n_var = X.shape

        # Initialize offspring array
        offspring = np.full((2, n_matings, n_var), -1)

        for i in range(n_matings):
            # Get parents
            parent1, parent2 = X[0, i], X[1, i]

            n = len(parent1)
            visited = [False] * n

            for start in range(n):
                if not visited[start]:
                    # Start a new cycle
                    indices = []
                    current = start
                    while not visited[current]:
                        indices.append(current)
                        visited[current] = True
                        # Find the corresponding index in parent 2
                        current = np.where(parent1 == parent2[current])[0][0]
                    
                    # Assign cycle values to offspring
                    for idx in indices:
                        offspring[0, i, idx] = parent1[idx]
                        offspring[1, i, idx] = parent2[idx]

            # Fill the remaining positions with elements from the other parent
            for j in range(n):
                if offspring[0, i, j] == -1:
                    offspring[0, i, j] = parent2[j]
                if offspring[1, i, j] == -1:
                    offspring[1, i, j] = parent1[j]

        # Verify permutations
        if not (self.is_permutation(offspring[0, i]) and self.is_permutation(offspring[1, i])):
            raise ValueError("Offspring are not valid permutations!")

        return offspring
"""
"""
    def find_cycle(self, parent1, parent2):
        n = len(parent1)
        visited = [False] * n
        cycles = []

        for start in range(n):
            if not visited[start]:
                cycle = []
                idx = start
                while not visited[idx]:
                    cycle.append(idx)
                    visited[idx] = True
                    idx = np.where(parent2 == parent1[idx])[0][0]
                cycles.append(cycle)

        return cycles
    
    def _do(self, problem, X, **kwargs):
        # Input shape (n_parents, n_matings, n_var)
        _, n_matings, n_var = X.shape

        # Initialize offspring array
        offspring = np.full((2, n_matings, n_var), -1)

        for i in range(n_matings):
            # Get parents
            parent1, parent2 = X[0, i], X[1, i]

            # Find cycles
            cycles = self.find_cycle(parent1, parent2)

            # Alternate cycles between offspring
            for c_idx, cycle in enumerate(cycles):
                if c_idx % 2 == 0:
                    # Copy cycle from parent1 to offspring[0] and parent2 to offspring[1]
                    offspring[0, i, cycle] = parent1[cycle]
                    offspring[1, i, cycle] = parent2[cycle]
                else:
                    # Copy cycle from parent2 to offspring[0] and parent1 to offspring[1]
                    offspring[0, i, cycle] = parent2[cycle]
                    offspring[1, i, cycle] = parent1[cycle]

            # Fill in the remaining values from the other parent
            offspring[0, i] = np.where(offspring[0, i] == -1, parent2, offspring[0, i])
            offspring[1, i] = np.where(offspring[1, i] == -1, parent1, offspring[1, i])

            # Verify permutations
            if not (self.is_permutation(offspring[0, i]) and self.is_permutation(offspring[1, i])):
                raise ValueError("Offspring are not valid permutations!")

        return offspring
"""