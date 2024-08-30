
import numpy as np

from params import Params
from representation.mapper import mapper

class Population():

    def __init__(self, operator) -> None:
        
        # Store individuals
        self.individuals = []

        # Initialization method
        self.initialize_operator = operator

        # Keep record of the number of individuals
        self.num_individuals_created = 0

    def initialize_population(self, population_size: int):
        """
        Initialize the first generation for the GE.
        
        @param population_size: Number of individuals to create.
        """

        # Store data
        self.population_size = population_size

        # Make use of the operator to start a population
        self.individuals = self.initialize_operator.run(self.population_size)

        # Add a name to each individual
        for i in range(self.population_size):
            self.individuals[i].name = f"Individual_{self.num_individuals_created+1:06d}"
            self.num_individuals_created += 1

    def get_population(self) -> list:
        """
        Returns the individuals who are not offspring.
        """
        pop = []

        for individual in self.individuals:
            if not(individual.is_offspring):
                pop.append(individual)
            
        return pop
    
    def get_offspring(self) -> list:
        """
        Returns the individuals who are currently
        offspring.
        """
        offspring = []

        for individual in self.individuals:
            if individual.is_offspring:
                offspring.append(individual)

        return offspring
    
    def non_evaluated(self) -> list:
        """
        Returns the not evaluated individuals.
        """
        non_evaluated = []

        for individual in self.individuals:
            if not(individual.evaluated):
                non_evaluated.append(individual)
        
        return non_evaluated
    
    def evaluated(self) -> list:
        """
        Returns the individuals already evaluated.
        """
        evaluated = []

        for individual in self.individuals:
            if individual.evaluated:
                evaluated.append(individual)

        return evaluated
    
    def get_hypervolumes(self, instance_name: str) -> list:
        """
        Returns the hypervolumes of all individuals
        in a given instance.
        """
        hypervolumes = []

        for individual in self.individuals:
            hypervolumes.append(individual.hypervolumes[instance_name])

        return hypervolumes
    
    def get_genomes(self) -> list:
        """
        Get the genomes of all individuals.
        """
        genomes = []

        for individual in self.individuals:
            genomes.append(individual.genome)
        
        return genomes
    
    def get_phenotypes(self) -> list:
        """
        Returns the individual's phenotypes
        from the current population
        """
        phenotypes = []

        for individual in self.individuals:
            phenotypes.append(individual.phenotype)
        
        return phenotypes
    
