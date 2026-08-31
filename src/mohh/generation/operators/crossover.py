
import copy
import random
import numpy as np

from mohh.generation.operators.operator import GeneticOperator

class Crossover(GeneticOperator):
    """
    A general crossover operator.
    """
    def __init__(self, n_parents: int) -> None:
        super().__init__()

        # Ensure there are more than 1 parent
        if n_parents < 2:
            msg = "The number of parents \
            must be greater than 1."
            raise ValueError(msg)
        
        self.n_parents = n_parents
    
    def __call__(self, parents: list, genomes_usage: list = None) -> list:
        """
        Computes crossover from the parents list.

        @param parents: list with a group of parents.
        :return: List with offspring.
        """

        # Make a copy of the parents genomes
        parents_copy = [copy.deepcopy(parent) for parent in parents]
        
        # Create offsprings
        offspring = self.run(*parents_copy, genomes_usage)

        if offspring is None:
            # Crossover failed
            pass

        return offspring
    
    def run(self):
        """
        Execute the operator

        :return: Offspring.
        """

class KPointCrossover(Crossover):
    """
    K Point Crossover Operator.
    """
    def __init__(self, n_parents: int, k_points: int) -> None:
        super().__init__(n_parents)

        if k_points < 1:
            msg = "The number of crossover points must be at least 1."
            raise ValueError(msg)

        elif n_parents != 2:
            msg = "The number of parents must be 2."
            raise ValueError(msg)

        self.k_points = k_points

    def run(self, parent1: list, parent2: list, genome_usage: list) -> tuple:
        """
        Execute the k-point crossover

        :return: Two offspring
        """

        if len(parent1) != len(parent2):
            raise ValueError("Parents must have the same length.")
        
        # Get the upper bound of genome relevance
        max_k = max(genome_usage)
        
        # Create k random points and sort them.
        k1 = 1
        k2 = random.sample(range(2, max_k), k=1)[0]
        crossover_points: list = [k1, k2]
        #crossover_points: list = sorted(random.sample(range(1, len(parent1)), self.k_points))

        # Initialize datastructures for offsprings
        offspring1, offspring2 = parent1.copy(), parent2.copy()

        # Perform the crossover
        for i in range(self.k_points):
            if i % 2 == 0 and i+1 < self.k_points: 
                # Swap segments
                k1 = crossover_points[i]
                k2 = crossover_points[i+1]
                offspring1[k1:k2] = parent2[k1:k2]
                offspring2[k1:k2] = parent1[k1:k2]

        return offspring1, offspring2
    

class UniformCrossover(Crossover):
    """
    Uniform Crossover operator implementation
    """
    def __init__(self, n_parents: int) -> None:
        super().__init__(n_parents)
        
        if n_parents != 2:
            msg = "The number of parents must be 2."
            raise ValueError(msg)
        
    def run(self, parent1: list, parent2: list):
        """
        Execute the k-point crossover

        @return: Two offsprings
        """

        if len(parent1) != len(parent2):
            raise ValueError("Parents must have the same length.")
        
        # Convert to numpy arrays
        if (type(parent1) != np.ndarray) or (type(parent2) != np.ndarray):
            parent1 = np.array(parent1)
            parent2 = np.array(parent2)

        # Get a random mask for genes
        mask = np.random.randint(0,1+1,size=len(parent1)).astype("bool")

        # Allocate memory
        offspring1, offspring2 = np.zeros_like(parent1), np.zeros_like(parent2)

        # Crossover
        offspring1[mask] = parent1[mask]
        offspring1[~mask] = parent2[~mask]

        offspring2[mask] = parent2[mask]
        offspring2[~mask] = parent1[~mask]

        return offspring1.tolist(), offspring2.tolist()