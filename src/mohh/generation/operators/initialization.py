
import random

from mohh.core.representation.tree import Tree
from mohh.generation.representation.population import Individual

from mohh.generation.params import Params
from mohh.generation.operators.operator import GeneticOperator

params = Params()

class Initialization(GeneticOperator):
    """
    Initialization operator
    """
    def __init__(self) -> None:
        super().__init__()

    def __call__(self, population_size: int) -> list:
        """
        Initialise a population.

        @param: population_size: Number of individuals to generate.

        :return: A full population generated using the specified
        initialization technique
        """
        individuals = self.run(population_size)
        return individuals


    def run(self):
        return super().run()
    
class Rvd(Initialization):
    """
    RVD Initialisation method.
    """
    def __init__(self):
        super().__init__()


    def run(self, size: int) -> list:
        """
        Create a random population discarding invalids and duplicates.

        @param size: The population size.
    
        @return: A full population of individuals.
        """
        tries = 0
        max_tries = size * 30

        population = []
        phenotypes = set()

        while len(population) < size:
            ind = Individual(sample_genome(), None)
            if ind.invalid or ind.phenotype in phenotypes:
                tries += 1
                if tries > max_tries:
                    s = f"""max tries {max_tries} exceeded during rvd initialisation."""
                    raise RuntimeError(s)

            else:
                phenotypes.add(ind.phenotype)
                population.append(ind)

        return population
    
def sample_genome() -> list:
    """
    Generate a random genome, uniformly.

    @return: A randomly generate genome.
    """

    genome = [random.randint(0, params["CODON_SIZE"]) for _ in
              range(params["INIT_GENOME_LENGTH"])]
    
    return genome