
import copy
import numpy as np

from mohh.evaluation.params import Params

from abc import ABC, abstractmethod

from mohh.evaluation.problem.instance import Instance
from mohh.core.utilities.load_modules import find_module
from mohh.evaluation.operators.operator_template import NullMutation

from pymoo.core.evaluator import Evaluator
from pymoo.core.population import Population
from pymoo.util.ref_dirs import get_reference_directions

from pymoo.algorithms.moo.moead import MOEAD
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.algorithms.moo.sms import SMSEMOA

from pymoo.core.callback import Callback

class MyCallback(Callback):

    def __init__(self):
        super().__init__()
        self.populations = {}

    def notify(self, algorithm):
        
        if algorithm.n_gen in [100, 300, 500]:
            results = algorithm.result()
            pareto_set = results.X
            pareto_front = results.F

            pareto_front, mask = np.unique(pareto_front, return_index=True, axis=0)

            if algorithm.n_gen == 100:
                self.populations["10k"] = pareto_front
            elif algorithm.n_gen == 300:
                self.populations["30k"] = pareto_front
            elif algorithm.n_gen == 500:
                self.populations["50k"] = pareto_front


class MOSolver(ABC):

    def __init__(self) -> None:
        """
        Initialize solver for an operator
        """

        # Load parameters
        params = Params()

        # Multiobjective parameters
        self.generations = params["MO_GENERATIONS"]

        # Multiobjective operators
        self.crossover = None
        self.mutation = None
        #self.with_mutation = params["MO_MUTATION_BOOL"]

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
        if operator_type == "mutation" and operator_name == "NullMutation":
            self.mutation = NullMutation()

        else:
            # Load operator
            module_name = f"mohh.evaluation.operators.{operator_type}"
            operator = find_module(module_name, operator_name, **kwargs)

            # Dynamically set the attribute based on operator_type
            operator_type = "crossover" if operator_type == "operator_template" else operator_type
            setattr(self, operator_type, operator)
        
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

    @abstractmethod
    def start_model(self):
        """
        Start the MOEA.
        """
        return
    
    @abstractmethod
    def solve_instance(self):
        """
        Execute MOEA
        """
        return


class MOEA_Decomposition(MOSolver):

    def __init__(self) -> None:
        super().__init__()
    
    def start_model(self, seed):
        """
        Start the MOEA.
        """

        # Load parameters
        params = Params()

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

        self.algorithm.setup(self.problem, termination=("n_gen", self.generations),
                             verbose=False, seed=seed, callback=MyCallback())
    
    def solve_instance(self):
        """
        MOEA execution
        """

        while self.algorithm.has_next():

            # Ask the algorithm for the next population
            pop = self.algorithm.ask()

            # Evaluate population
            self.algorithm.evaluator.eval(self.problem, pop)

            # Return the evaluated individuals
            self.algorithm.tell(infills=pop)

        # Extract callback data
        snapshots_data = self.algorithm.callback.populations
        
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

        return snapshots_data


class NSGAII(MOSolver):
    def __init__(self) -> None:
        super().__init__()
    
    def start_model(self, seed):
        """
        Start the MOEA.
        
        @param model_name: MOEA solver name.
        """

        # Build algorithm
        self.algorithm = NSGA2(
            pop_size=self.pop_size,
            sampling=self.pop,
            crossover=self.crossover,
            mutation=self.mutation
        )
        # Implicit operators
        # Tournament selection
        # Survival RankandCrowding

        self.algorithm.setup(self.problem, termination=("n_gen", self.generations),
                             verbose=False, seed=seed)
    
    def solve_instance(self):
        """
        MOEA execution
        """

        while self.algorithm.has_next():

            # Ask the algorithm for the next population
            pop = self.algorithm.ask()

            # Evaluate population
            self.algorithm.evaluator.eval(self.problem, pop)

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


class SMS_MOEA(MOSolver):
    def __init__(self) -> None:
        super().__init__()
    
    def start_model(self, seed):
        """
        Start the MOEA.
        
        @param model_name: MOEA solver name.
        """

        # Build algorithm
        self.algorithm = SMSEMOA(
            pop_size=self.pop_size,
            sampling=self.pop,
            crossover=self.crossover,
            mutation=self.mutation
        )
        # Implicit operators
        # Tournament selection
        # Survival LeastHypervolumeContributionSurvival

        self.algorithm.setup(self.problem, termination=("n_gen", self.generations),
                             verbose=False, seed=seed)
    
    def solve_instance(self):
        """
        MOEA execution
        """

        while self.algorithm.has_next():

            # Ask the algorithm for the next population
            pop = self.algorithm.ask()

            # Evaluate population
            self.algorithm.evaluator.eval(self.problem, pop)

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

class IBEA():
    pass
