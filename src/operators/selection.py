
import random

from params import Params
from operators.operator import GeneticOperator


class Selection(GeneticOperator):
    """
    Selection Operator.
    """
    def __init__(self, num_parents: int) -> None:
        super().__init__()
        self.num_parents = num_parents

    def __call__(self, population: list, scores: list) -> list:
        """
        Selects parents from population.

        @param population: list with genomes from the current population.
        @param scores: list with score values for each individual.

        :return: A pair of parents.
        """

        # Initialize an empty variable for selected individuals
        parents = []

        for _ in range(self.num_parents):
            # Select individual and add it to the parent list
            parents.append(self.run(population, scores))
        
        return parents
    
    def run(self):
        """
        Execute the operator

        :return: Mutated Individual
        """


class Tournament(Selection):
    
    def __init__(self, k: int, num_parents: int=2) -> None:
        """
        Tournament Selection
        @param k: Sample size.
        """
        super().__init__(num_parents=num_parents)
        self.sample_size = k
    
    def run(self, population: list, scores: list):
        """
        @param population: list with individuals.
        @param scores: list with fitness values.
        
        :return: parent
        """

        # Choose a subset k randomly
        selected_candidates = random.sample(list(enumerate(population)), self.sample_size)

        # Separete indices from individuals
        indices, candidates = list(zip(*selected_candidates))

        # Extract the scores for the selected candidates
        candidates_scores = [scores[i] for i in indices]

        # Get the index of the min score
        winner_index = candidates_scores.index(min(candidates_scores))

        # Return the winner candidate
        return candidates[winner_index]