
from mohh.core.representation.population import Population as _Population
from mohh.core.representation.population import Individual

class Population(_Population):

    def get_genome_usage(self) -> list:
        """
        Returns the allels needed to map the phenotype
        from the current population.
        """
        usage = []

        for individual in self.individuals:
            usage.append(individual.used_codons)

        return usage
