
import numpy as np

from generation.params import Params
from generation.operators.operator import GeneticOperator


class Mutation(GeneticOperator):
    """
    Mutation operators.

    Require at least 1 solution.
    """
    def __init__(self, probability) -> None:
        super().__init__()
        self.probability = probability

    def __call__(self, population: list) -> list:
        """
        Computes mutation for all the individuals.

        @param individuals: list of individuals genomes to be mutated.

        :return: Mutated genomes.
        """

        # Initialise empty population
        new_pop = []

        # Iterate over the current population
        for ind in population:

            # Perform mutation
            new_genome = self.run(ind)

            # Append the mutated individual
            new_pop.append(new_genome)
        
        return new_pop
    
    def run(self):
        """
        Execute the operator

        :return: Mutated Individual
        """


class BitFlipMutation(Mutation):
    """
    Bit Flip Mutation Operator
    """
    def __init__(self, probability) -> None:
        super().__init__(probability)

        params = Params()
        self.upper_limit = params["CODON_SIZE"]

    def run(self, genome: list) -> list:
        """
        Mutates an individual genome.

        @param individual: Genome of the individual.

        :return: New genome
        """

        if (type(genome) != list) and (type(genome) != np.ndarray):
            msg = "genomes must be lists of integers or numpy arrays."
            raise ValueError(msg)
        
        if type(genome) == list:
            genome = np.array(genome)
        
        mutation_mask = np.random.rand(len(genome)) < self.probability
        mutations = np.random.randint(-10,10, size=len(genome))

        mutated_genome = genome + mutation_mask * mutations
        mutated_genome = np.clip(mutated_genome, 0, self.upper_limit)

        return mutated_genome.tolist()