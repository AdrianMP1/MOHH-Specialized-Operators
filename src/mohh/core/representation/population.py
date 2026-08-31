
import numpy as np

from mohh.core.params import Params
from mohh.core.representation.mapper import mapper

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


class Individual():

    def __init__(self, genome: list, tree: object, map_required: bool=True) -> None:
        """
        Create a new individual.

        @param genome: Individual's genome.
        @param tree: Derivation tree.
        @param map_required: Bool to indicate if it needs to be mapped first.
        """

        # Load params
        params = Params()

        if map_required:
            # Map the individual
            self.phenotype, self.genome, self.tree, self.nodes, self.invalid, \
            self.depth, self.used_codons = mapper(genome, tree)

        else:
            self.genome, self.tree = genome, tree
        
        # Add individual information
        self.name = None
        self.evaluated = False
        self.is_offspring = False
        self.runtime_error = None

        # Optimization information
        self.maximize = params["OPTIMIZATION_KIND"]

        # Determine sign for domination comparison
        self.sign = 1
        if not(self.maximize):
            self.sign = -1
        
        # Variables to store results
        self.hypervolumes = dict()
        self.fitness_values = dict()

        self.pareto_sets = dict()
        self.pareto_fronts = dict()

        self.unique_solutions = dict()
        self.weak_non_dominated = dict()
        self.strong_non_dominated = dict()
    
    def __len__(self):
        """
        Returns the genome length of the individual.
        """
        return len(self.genome)
    
    def __str__(self):
        """
        Returns individuals phenotype
        """
        return self.phenotype
    
    def __repr__(self) -> str:
        """
        Shows individuals phenotype
        """
        return f"Individual({self.phenotype})"
