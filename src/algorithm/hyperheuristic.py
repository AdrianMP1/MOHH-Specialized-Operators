
import sys
import copy
import time
from tqdm import tqdm

# Classes
from params import Params
from saver import PopulationSaver

from problem.instance import Instance
from algorithm.multiobjective import MOSolver
from representation.population import Population
from representation.population import Individual

# Auxiliar functions
from utilities.print_utils import update_lines
from utilities.print_utils import clear_above_lines
from utilities.load_modules import find_module
from utilities.algorithm.MO import compute_nadir_point
from utilities.algorithm.MO import compute_hypervolume
from utilities.algorithm.MO import non_dominated_sorting
from utilities.algorithm.HH_auxiliars import compute_rank
from utilities.algorithm.HH_auxiliars import test_individual

class HyperHeuristic():

    def __init__(self) -> None:
        
        # Load General Parameters
        params = Params()

        # Parameters
        self.seed = params["RANDOM_SEED"]
        self.population_size = params["POPULATION_SIZE"]
        self.num_generations = params["GENERATIONS"]

        self.mo_model_name = params["MO_MODEL"]
        self.mo_cross_prob = params["MO_CROSSOVER_PROBABILITY"]
        self.mo_population_size = params["MO_POPULATION_SIZE"]

        # Genetic Operators
        self.selection = None
        self.crossover = None
        self.mutation = None
        self.replacement = None

        # Population
        self.population = None
        self.already_seen = set()
        self.num_offsprings = params["GENERATION_SIZE"]

        # Instances parameters
        self.problem_name = params["PROBLEM_NAME"]
        self.solution_type = params["SOLUTION_TYPE"]

    def load_operator(self, operator_type: str, operator_name: str, **kwargs: dict):
        """
        Load a genetic operator to the algorithm.
        Choose between: selection, crossover, mutation,
        replacement and initialization.

        @param operator_type: Choose between selection, crossover,
        mutation, replacement and initialization
        @param operator_name: Operator name.
        """

        operator_type = operator_type.lower()

        module_name = f"operators.{operator_type}"
        operator = find_module(module_name, operator_name, **kwargs)

        # Handle initialization
        if operator_type == "initialization" or operator_type == "initialization":
            self.population = Population(operator)
            return self

        # Dynamically set the attribute based on operator_type
        setattr(self, operator_type, operator)

        return self

    def load_instances(self, instance_paths: list) -> None:
        """
        Load instance paths, and create instance objects.

        @param instance_paths: List with instances file paths.
        """
        # Create an instance object per file.
        self.instances = []

        # Verify if MO population size is a list or integer
        if type(self.mo_population_size) == int:
            # Transform it into a list with repeated values
            self.mo_population_size = [self.mo_population_size]*len(instance_paths)
        
        for indx, instance_path in enumerate(instance_paths):
            # Initiate instance object
            instance = Instance(self.mo_population_size[indx], self.solution_type)

            # Load problem
            instance.load_problem(self.problem_name, instance_path)

            # Store it
            self.instances.append(instance)

    def evaluation_step(self):
        """
        Evaluates the individuals by solving the instances.
        """

        # Make a progress bar
        pbar = tqdm(self.population.non_evaluated(), desc="Evaluating...",
                    bar_format="{l_bar}{bar:20}{r_bar}", leave=True)
        
        # Evaluate individuals
        for individual in pbar:

            # Create a MOSolver for the individual
            solver = MOSolver(seed=self.seed)
            solver.load_operator("operator_template", "HH_Operator",
                                 operator=individual.phenotype,
                                 solution_type=self.solution_type,
                                 prob=self.mo_cross_prob)
            solver.load_operator("mutation", "NullMutation")

            for instance in self.instances:
                
                # Send the instance to the MO solver
                solver.load_instance(instance)

                # Start the model
                solver.start_model(model_name=self.mo_model_name)

                # Solve the instance
                results = solver.solve_instance()

                # Extract results
                pareto_set, pareto_front = results[:2]
                weak_non_dominated, unique_solutions, strong_non_dominated = results[2:]

                # Store results in the individual object
                instance_name = instance.instance_name
                individual.pareto_sets[instance_name] = pareto_set
                individual.pareto_fronts[instance_name] = pareto_front
                individual.unique_solutions[instance_name] = unique_solutions
                individual.weak_non_dominated[instance_name] = weak_non_dominated
                individual.strong_non_dominated[instance_name] = strong_non_dominated

                # Add front to the consolidated
                instance.non_dominated_front = \
                    instance.non_dominated_front.union([tuple(element) for element in pareto_front.tolist()])
    
    def compute_metrics(self):
        """
        Compute an indicator metric and rank the individuals.
        """

        # Now that every individual has solved the instances.
        fitness_values = [[0]*len(self.instances) for _ in range(len(self.population.individuals))]

        # Make memory for instance times
        instance_sorting_time = [0.0]*len(self.instances)
        instance_hv_time = [0.0]*len(self.instances)

        # Display times
        sorting_text = ", ".join([f"{i:05.1f} min" for i in instance_sorting_time])
        hv_text = ", ".join([f"{i:05.1f} min" for i in instance_hv_time])
        print(f"\nSorting: ", sorting_text)
        print(f"Hypervolumes: ", hv_text)

        # Make a progress bar
        pbar = tqdm(self.instances, desc="Computing metrics...",
                     bar_format="{l_bar}{bar:20}{r_bar}", leave=True)

        # For each individual...
        for i, instance in enumerate(pbar):
                
            # Instance name
            instance_name = instance.instance_name

            # Measure non dominated sorting time
            sorting_time_init = time.time()

            # If instance already has fronts...
            if instance.fronts:
                
                # Merge all fronts with non-dominated front
                for front in instance.fronts:
                    instance.non_dominated_front = instance.non_dominated_front.union(front)

            # Compute non-dominated-sorting on each instance non-dominated-front.    
            instance.fronts = non_dominated_sorting(instance.non_dominated_front)

            # Measure non dominated sorting end time [min]
            sorting_time = (time.time() - sorting_time_init) / 60

            # Set non-dominated front as the first front.
            instance.non_dominated_front = set(instance.fronts[0])

            # Compute Nadir Points
            instance.nadir_point = compute_nadir_point(instance.non_dominated_front)

            # Verify that new Nadir Point is indeed worst # TODO: IMPROVE IT (location maybe?, the way consolidated is updated influences.)
            # For now it will work with a new nadir every time.
            #instance.nadir_point = list(map(max, zip(*[instance.nadir_point, instance.previous_nadir_point])))

            # Measure Hypervolume computation time.
            hv_time_init = time.time()

            # If nadir point changed...
            if instance.previous_nadir_point != instance.nadir_point:

                # Re-compute the hypervolume of the actual population
                for individual in self.population.evaluated():
                    individual.hypervolumes[instance_name] = compute_hypervolume(instance.nadir_point,
                                                                individual.pareto_fronts[instance_name])

            # Compute the hypervolume to all the new individuals
            for individual in self.population.non_evaluated():

                # Compute hypervolume to the new individual.
                individual.hypervolumes[instance_name] = compute_hypervolume(instance.nadir_point,
                                                            individual.pareto_fronts[instance_name])
            
            # Get total time Hypervolume took [min]
            hv_time = (time.time() - hv_time_init) / 60

            # Save the nadir_points to verify changes.
            instance.previous_nadir_point = instance.nadir_point

            # Assign a rank for each individual based on their hypervolumes.
            ranks = compute_rank(self.population.get_hypervolumes(instance_name))

            # Store the rank to the individuals
            for j, individual in enumerate(self.population.individuals):
                individual.fitness_values[instance_name] = ranks[j]
                fitness_values[j][i] = ranks[j]

            # Store computation times
            instance_sorting_time[i] = sorting_time
            instance_hv_time[i] = hv_time

            # Make new time strings
            sorting_text = ", ".join([f"{i:05.1f} min" for i in instance_sorting_time])
            hv_text = ", ".join([f"{i:05.1f} min" for i in instance_hv_time])

            # Update CLI prints
            update_lines(["Sorting: " + sorting_text,
                        "Hypervolumes: " + hv_text])

        # Once an individual computed its hypervolumes across all instances,
        # mark it as evaluated.
        for individual in self.population.non_evaluated():
            # Mark the individual as evaluated.
            individual.evaluated = True

        # Average the fitness values across all instances.
        scores = [sum(fitness_values[i]) / len(self.instances) for i in range(len(self.population.individuals))]

        return scores

    def evolutionary_step(self, scores: list):
        """
        Compute an evolutionary step.
        Selection, Crossover, Mutation.
        """
        
        # Extract current genomes from population
        genomes = copy.deepcopy(self.population.get_genomes())

        # Extract current phenotypes from population
        phenotypes = copy.deepcopy(self.population.get_phenotypes())

        # Create variable for new individuals
        offspring = []

        # Apply Genetic Operators
        while len(offspring) < self.num_offsprings:

            # Work with genomes only
            parents = self.selection(genomes, scores)
            children = self.crossover(parents)
            children = self.mutation(children)
            
            for child in children:
                # Create new individual.
                ind = Individual(child, None)
                
                # Verify if individual is invalid or repeated
                if ind.invalid or ind.phenotype in phenotypes:
                    continue
                
                # Verify if it outputs valid values.
                elif test_individual(ind.phenotype, self.solution_type) == False:
                    continue

                # Verify individual hasn't already be created
                elif ind.phenotype in self.already_seen:
                    continue
                
                # Offspring is valid and outputs admisible results.
                offspring.append(ind)

                # Add it to already seen
                self.already_seen.add(ind.phenotype)

                # Hard constraint, don't exceed num_offsprings.
                if len(offspring) == self.num_offsprings:
                    break

        # Name individuals.
        for child in offspring:

            # Set child as offspring.
            child.is_offspring = True

            # Set individual name.
            child.name = f"Individual_{self.population.num_individuals_created+1:06d}"
            
            # Increase counter.
            self.population.num_individuals_created += 1
        
        # Append the new generation to the current one.
        self.population.individuals.extend(offspring)

    def replace_step(self, scores: list) -> list:
        """
        Apply replacement with elitism.
        """
        # Get the individuals list
        #individuals = self.population.individuals
        
        # Get the current population
        population = self.population.get_population()

        # Get the current offspring
        offspring = self.population.get_offspring()

        # Elitism size
        elitism_size = len(population) - len(offspring)

        # Assuming the order is conserved...
        paired_population = list(zip(population, scores[:len(population)]))

        paired_offspring = list(zip(offspring, scores[len(population):]))

        # Sort population
        sorted_population = sorted(paired_population, key=lambda x: x[1])

        # Remove the last n individuals with worse score
        preserved_population = sorted_population[:elitism_size]

        # Merge preserved population with offsprings
        preserved_population.extend(paired_offspring)

        # Sort final population
        final_pairs = sorted(preserved_population, key=lambda x: x[1])

        # Extract population and scores
        new_population = [ind for ind, _ in final_pairs] 

        scores = [score for _, score in final_pairs]

        # Update population
        self.population.individuals = new_population

        # Set individuals as not offsprings
        for individual in self.population.individuals:
            individual.is_offspring = False

        return scores

    def run(self):
        """
        Execute the generation hyperheuristic.
        """
        
        # Load population saver
        population_saver = PopulationSaver()

        # Start timer
        start_time = time.time()

        print("Generation 0.")
        print("Start initial population.")

        # Create initial population.
        self.population.initialize_population(self.population_size)
        
        # Store phenotypes in memory.
        self.already_seen = self.already_seen.union(self.population.get_phenotypes())

        print("Evaluating initial population...")
        
        # Evaluate the initial population and compute metrics.
        self.evaluation_step()
        scores = self.compute_metrics()

        # Save population and instance data
        population_saver.save_population(self.population, generation=0)
        population_saver.save_consolidated_fronts(self.instances, generation=0)

        for gen in range(1, self.num_generations + 1):

            print(f"\nGeneration {gen}/{self.num_generations}")

            # Generate offsprings
            self.evolutionary_step(scores)

            # Note: Evolutionary step has increased the size from N to N + n.
            # Evaluation will skip the already evaluated N individuals,
            # and just evaluate the rest n.
            # If a nadir point is modified, compute metrics will recompute HVs
            # for all the individuals (N+n), else just n new individuals.

            # Evaluate offsprings
            self.evaluation_step()
            scores = self.compute_metrics()

            # Save offspring in disk
            population_saver.save_population(self.population, generation=gen-1)

            # Replace current population with offsprings.
            scores = self.replace_step(scores)

            # Note: Replace deletes the worst n individuals in the population,
            # therefore, population has now a size of N.

            # Save current population in disk
            population_saver.save_population(self.population, generation=gen)
            population_saver.save_consolidated_fronts(self.instances, generation=gen)
            
            print(f"\nBest Individual: {self.population.individuals[0].phenotype}")

        # Print total time
        end = time.time()
        seconds = round(end - start_time, 2)
        minutes = round(seconds / 60, 2)
        hours = round(minutes / 60, 2)
        print(f"\n\n Total time: {seconds} seconds.")
        print(f"Minutes: {minutes}")
        print(f"Hours: {hours}")