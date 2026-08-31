
import copy
import numpy as np

from mohh.generation.params import Params

from mohh.generation.problem.instance import Instance
from mohh.generation.utilities.load_modules import find_module
from mohh.generation.operators.operator_template import NullMutation

from pymoo.algorithms.moo.moead import MOEAD
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.algorithms.moo.sms import SMSEMOA

from pymoo.core.evaluator import Evaluator
from pymoo.core.population import Population
from pymoo.util.ref_dirs import get_reference_directions

class MOSolver():
    
    def __init__(self, seed) -> None:
        """
        Initialize solver for an individual.
        """

        # Load parameters
        params = Params()

        # Multiobjective parameters
        self.generations = params["MO_GENERATIONS"]
        self.seed = seed

        # Multiobjective operators
        self.crossover = None
        self.mutation = None
        self.with_mutation = params["MO_MUTATION_BOOL"]

        self.pop = None
        self.problem = None

    def load_operator(self, operator_type: str, operator_name: str, **kwargs: dict):
        """
        Loads a genetic operator to the algorithm.
        Choose between: crossover and mutation

        @param operator_type: Choose between: crossover and mutation.
        @param operator_name: Name of the operator.
        """

        # Handle algorithms with no mutation
        if not(self.with_mutation) and operator_type == "mutation":
            self.mutation = NullMutation()

        else:
            # Load operator
            module_name = f"mohh.generation.operators.{operator_type}"
            operator = find_module(module_name, operator_name, **kwargs)

            # Dynamically set the attribute based on operator_type
            setattr(self, "crossover", operator)
        
        return self

    def load_instance(self, instance: Instance):
        """
        Load an instance object and copy its initial solution.
        
        @param instance: Instance object.
        """
        
        # Load problem
        self.problem = copy.deepcopy(instance.problem)

        # Start with initial population
        self.pop = Population.new("X", instance.initial_solutions.copy())

        # Extract information from the instance
        self.pop_size = instance.population_size
        self.k_objectives = instance.k_objectives

        # Evaluate the initial solutions
        Evaluator().eval(self.problem, self.pop)

    def start_model(self, model_name: str):
        """
        Load the MOEA.
        
        @param model_name: MOEA solver name.
        """

        params = Params()

        # Initialize algorithm
        if model_name == "MOEAD":

            # Create reference directions
            ref_dirs = get_reference_directions("uniform", self.k_objectives, n_points=self.pop_size)

            # Build algorithm
            self.algorithm = MOEAD(
                ref_dirs=ref_dirs,
                n_neighbors=params["NUM_NEGIHBORS"],
                prob_neighbor_mating=params["PROB_NEIGHBORS"],
                sampling=self.pop,
                crossover=self.crossover,
                mutation=self.mutation
            )

            #self.algorithm.setup(self.problem, termination=("n_gen", self.generations),
            #                     verbose=False, seed=self.seed)
        
        elif model_name == "NSGAII":

            # Build algorithm
            self.algorithm = NSGA2(
                pop_size=self.pop_size,
                sampling=self.pop,
                crossover=self.crossover,
                mutation=self.mutation
            )

        elif model_name == "SMSEMOA":

            # Build algorithm
            self.algorithm = SMSEMOA(
                pop_size=self.pop_size,
                sampling=self.pop,
                crossover=self.crossover,
                mutation=self.mutation
            )
        
        else:
            raise(ValueError)
        
        self.algorithm.setup(self.problem, termination=("n_gen", self.generations),
                             verbose=False, seed=self.seed)
        

    def solve_instance(self):
        """
        MOEA process. 
        """

        while self.algorithm.has_next():

            # Ask the algorithm for the next population
            pop = self.algorithm.ask()

            try:
                # Evaluate population
                self.algorithm.evaluator.eval(self.problem, pop)

            except TypeError as e:
                
                if "NoneType" in str(e):
                    # Handle the specific problem of SMS-EMOA
                    #print("None Population")
                    break

                else:
                    # Handle other TypeErrors
                    print(e)
                    raise

            except Exception as e:
                print(e)
                raise

            # Return the evaluated individuals
            self.algorithm.tell(infills=pop)

        # Extract results
        results = self.algorithm.result()
        pareto_set = results.X
        pareto_front = results.F

        # Get the number of individuals weakly non-dominated
        number_weak_non_dominated = len(pareto_set)

        # Get the number of truly unique individuals
        number_unique_results = len(np.unique(pareto_set, axis=0))

        # Filter by unique elements in the pareto front
        pareto_front, mask = np.unique(pareto_front, return_index=True, axis=0)
        pareto_set = pareto_set[mask]

        # Get the number of unique individuals from pareto front
        number_unique_pareto_front = len(pareto_front)

        return (pareto_set, pareto_front, number_weak_non_dominated,
            number_unique_results, number_unique_pareto_front)