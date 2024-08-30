
import copy
import time
from tqdm import tqdm

from params import Params

from algorithm.load_modules import find_module
from algorithm.multiobjective import MOSolver

from problem.instance import Instance
from representation.population import Population

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
        
        # Evaluate individuals
        for individual in tqdm(self.population.non_evaluated()):

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
        Compute indicators
        """
        pass

    def evolutionary_step(self):
        """
        Compute an evolutionary step.
        Selection, Crossover, Mutation.
        """
        pass

    def replace_step(self):
        """
        """
        pass

    def run(self):
        """
        Execute the generation hyperheuristic.
        """
        
        # Load population saver

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
        

        for gen in range(1, self.num_generations + 1):

            print(f"\nGeneration {gen}/{self.num_generations}")

            # Generate offsprings
            self.evaluation_step(scores)

            # Note: Evolutionary step has increased the size from N to N + n.
            # Evaluation will skip the already evaluated N individuals,
            # and just evaluate the rest n.
            # If a nadir point is modified, compute metrics will recompute HVs
            # for all the individuals (N+n), else just n new individuals.

            # Evaluate offsprings
            self.evaluation_step()
            scores = self.compute_metrics()

            # Save offspring in disk

            # Replace current population with offsprings.
            self.replace_step()

            # Note: Replace deletes the worst n individuals in the population,
            # therefore, population has now a size of N.

            # Save current population in disk
            
            print(f"Best Individual: {self.population.individuals[0].phenotype}")

        # Print total time
        end = time.time()
        seconds = round(end - start_time, 2)
        minutes = round(seconds / 60, 2)
        hours = round(minutes / 60, 2)
        print(f"\n\n Total time: {seconds} seconds.")
        print(f"Minutes: {minutes}")
        print(f"Hours: {hours}")