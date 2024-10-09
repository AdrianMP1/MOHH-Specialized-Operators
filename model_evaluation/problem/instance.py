
import os
import numpy as np

import multiprocessing
from multiprocessing.pool import ThreadPool
from pymoo.core.problem import StarmapParallelization

from params import Params
from pymoo.core.problem import ElementwiseProblem
from pymoo.core.problem import Problem
from pymoo.core.sampling import Sampling

class Instance():

    # Shared across all instances.
    num_instances_created = 0

    def __init__(self, population_size: int, solution_type: str) -> None:
        """
        Creates an empty instance object.

        @param population_size: Number of solutions per instance.
        @param solution_type: Natural or Real.
        """
        # Instance parameters
        self.n_variables: int = None
        self.k_objectives: int = None
        self.identification: int = None
        self.kind: str = None

        self.file_name: str = None
        self.file_path: str = None
        self.instance_name: str = None

        # Naturals or Reals.
        self.solution_type: str = solution_type.lower()

        # Initial population
        self.population_size :int = population_size
        self.initial_solutions: np.ndarray = None
        self.initial_solutions_experiments: dict = {}

        # Each instance has a current non-dominated front
        self.fronts: list = []
        self.non_dominated_front: set = set()
        self.nadir_point: list = []
        self.previous_nadir_point: list = []

        # Update instance id
        Instance.num_instances_created += 1
        self.instance_id :str = f"Instance_{Instance.num_instances_created:03d}"

    def create_initial_solution(self, experiment: int) -> None:
        """
        Generates an initial solution.
        It must be executed only one time per instance.
        """

        params = Params()

        # Generate them.
        generator = MOSampling(kind=self.solution_type)
        initial_solutions = generator.generate(self.n_variables,
                                                self.population_size)
        
        # Save it to disk.
        file_path = params["FILE_PATH_INITIAL_SOLUTIONS"]

        instance_level = file_path + "/" + self.file_name
        os.makedirs(instance_level, exist_ok=True)

        with open(instance_level + "/" + f"experiment_{experiment:03d}" + ".txt", "w") as f:
            for i in range(self.population_size):
                # Extract an individual and format it to string
                sol = initial_solutions[i].tolist()
                
                if self.solution_type == "real":
                    sol = ", ".join(["{:.04f}".format(w) for w in sol])
                else:
                    sol = ", ".join(["{:03d}".format(w) for w in sol])
                    
                sol = "[" + sol + "]\n"

                # Write on file
                f.write(sol)

            # Close the file
            f.close()
        
        return initial_solutions

    def create_solutions(self, n_experiments: int) -> None:
        """
        Generates N initial solutions.
        """

        initial_solutions = {}
        
        for experiment in range(1, n_experiments+1):

            solutions = self.create_initial_solution(experiment)
            
            initial_solutions[f"Experiment_{experiment:03d}"] = solutions
        
        self.initial_solutions_experiments = initial_solutions

    def load_problem(self, problem_type: str, file_name: str, 
                     n_experiments:int) -> None:
        """
        Loads an instance file.

        @param problem_type: QAP or TSP.
        @param file_name: Instance file path.
        """

        self.file_path = file_name.replace("\\", "/")
        self.file_name = self.file_path.split("/")[-1].removesuffix(".txt")
        self.instance_name = self.file_name

        if problem_type.lower() == "qap":
            # Load a mQAP instance
            ## Extract parameters
            self._extract_qap_parameters()

            ## Create initial solutions for consistency.
            self.create_solutions(n_experiments)

            ## Create an initial nadir point
            self.previous_nadir_point = [0] * self.k_objectives

            ##* Experimental: Initialize a process pool
            #n_threads = 4
            #pool = ThreadPool(n_threads)
            #runner = StarmapParallelization(pool.starmap)

            ## Create instance problem
            self.problem = QuadraticAssignment(self.n_variables, self.k_objectives,
                                                self.file_path, self.solution_type)
            #                                    elementwise_runner=runner)

        elif problem_type.lower() == "tsp":
            # Loads a tsp instance
            pass

    def set_initial_solutions(self, experiment: int):
        """
        Set initial solutions for its respective experiment
        """

        solutions = self.initial_solutions_experiments[f"Experiment_{experiment:03d}"]
        
        self.initial_solutions = solutions

    def _extract_qap_parameters(self) -> None:
        """
        Extract parameters from file names.
        """
        # Get instance file name
        instance_name = self.file_name

        # Extract parameters from the file_name
        parameters: list = instance_name.split("-")

        # Number of variables
        self.n_variables: int = int(parameters[0][2:])

        # Number of objectives
        self.k_objectives: int = int(parameters[1][:-2])

        # Instance Id
        self.identification: int = int(parameters[2][:-2])

        # Type of distribution
        self.kind: str = parameters[2][1:]


class QuadraticAssignment(ElementwiseProblem):
    
    def __init__(self, n_var: int, k_obj: int, file_name: str,
                 kind_solutions: str, **kwargs):
        super().__init__(n_var=n_var, n_obj=k_obj, **kwargs)
        """
        QAP instance class for Pymoo.

        @param n_var: Number of variables.
        @param k_obj: Number of objective matrices.
        @param file_name: Instance file path.
        @param kind_solutions: Natural or Real.

        :return: QAP Instance.
        """

        self.k_obj = k_obj
        self.n_var = n_var

        self.weights = None
        self.positions = None

        # Permutations or Real values.
        self.kind_solutions = kind_solutions

        self.init_with_instance_file(file_name)

    def init_with_instance_file(self, instance_file: str) -> None:
        """
        Loads the positions of the factories and their weights in numpy arrays.
        
        @param instance_file: Instance path to load.
        """
        if isinstance(instance_file, str):
            self.instance_file = instance_file
        else:
            raise TypeError("Instance_file must be a string")

        # Open and read instance file
        file = open(self.instance_file, 'r')
        file_content = list(map(str.strip, file.readlines()))
        file.close()
        
        # Extract parameters
        parameters = file_content[0].split(" ")

        n_variables = int(parameters[1])
        k_objectives = int(parameters[3])

        # Clean data
        file_content = list(map(lambda x: " ".join(x.split()) , file_content[1:]))

        # Extract position matrix
        positions = np.array( [list(map(int, line.split(" "))) for line in file_content[:n_variables]] )

        # Create the array for the flux between variables
        flux = np.zeros((k_objectives, n_variables, n_variables))

        for i in range(k_objectives):
            start = (i+1)*n_variables + 1 + i
            end = (i+2)*n_variables + 1 + i

            # Fill the 3-Matrix
            flux[i] = np.array( [list(map(int, line.split(" "))) for line in file_content[start:end]] )

        # Save positions and weights into self.weights and self.positions
        self.weights = flux
        self.positions = positions

    def decode_random_keys(self, solution:np.ndarray) -> list:
        """
        Auxiliar function to decode random_keys into natural numbers.

        @param solution: Numpy array with float numbers.

        :return: List with int numbers.
        """
        # Add index labels
        augmented_keys = list(zip([i for i in range(len(solution))], solution))

        # Sort the keys by the random numbers
        augmented_keys.sort(key = lambda x: x[1])

        # Unzip it and extract the decoded solution
        return list(zip(*augmented_keys))[0]


    def _evaluate(self, x:np.ndarray, out:dict, *args, **kwargs):
        """
        Receives the population form the algorithm and evaluates each individual.
        It end updating the F key of the variable out.
        Current complexity: O(p x k x n^2) where p is population size.

        @param x: Population.
        @param out: Dictionary to update.
        """
        x = x.reshape(1, -1)

        # Get population size
        population_size = x.shape[0]

        # Allocate memory for fitness values.
        values = np.zeros((population_size, self.k_obj))

        # Verify if solutions are ints or floats.
        if self.kind_solutions.lower() == "real":
            # Convert random-keys into int values
            solutions = np.array([self.decode_random_keys(x[i,:].copy()) for i in range(population_size)])
        else:
            # 
            solutions = x
        
        for i in range(population_size):
            for current_objective in range(self.k_obj):
                values[i, current_objective] = self.cost_of_solution(current_objective, solutions[i,:])

        #for i in range(population):
        #    for current_objective in range(self.k_obj):

        #        values[i,current_objective] = self.cost_of_solution(current_objective, self.decode_random_keys(x[i,:]))

        out["F"] = values.squeeze()
    
    def cost_of_solution(self, function_indx:int, solution:np.ndarray):
        """
        Return the cost of a solution in its respective function
        Vectorized implementation. Current complexity: O(n^2)
        """
        # Rearrange self.positions based on the solution
        permuted_positions = self.positions[np.ix_(solution, solution)]

        # Perform element-wise multiplication with the corresponding weights
        total_cost = np.sum(self.weights[function_indx] * permuted_positions)

        return total_cost // 2


class QuadraticAssignment_nonParallel(Problem):

    def __init__(self, n_var: int, k_obj: int, file_name: str,
                kind_solutions: str, **kwargs):
        """
        QAP instance class for Pymoo.

        @param n_var: Number of variables.
        @param k_obj: Number of objective matrices.
        @param file_name: Instance file path.
        @param kind_solutions: Natural or Real.

        :return: QAP Instance.
        """
        super().__init__(n_var=n_var, n_obj=k_obj, **kwargs)

        self.k_obj = k_obj
        self.n_var = n_var

        self.weights = None
        self.positions = None

        # Permutations or Real values.
        self.kind_solutions = kind_solutions

        self.init_with_instance_file(file_name)

    def init_with_instance_file(self, instance_file: str) -> None:
        """
        Loads the positions of the factories and their weights in numpy arrays.
        
        @param instance_file: Instance path to load.
        """
        if isinstance(instance_file, str):
            self.instance_file = instance_file
        else:
            raise TypeError("Instance_file must be a string")

        # Open and read instance file
        file = open(self.instance_file, 'r')
        file_content = list(map(str.strip, file.readlines()))
        file.close()
        
        # Extract parameters
        parameters = file_content[0].split(" ")

        n_variables = int(parameters[1])
        k_objectives = int(parameters[3])

        # Clean data
        file_content = list(map(lambda x: " ".join(x.split()) , file_content[1:]))

        # Extract position matrix
        positions = np.array( [list(map(int, line.split(" "))) for line in file_content[:n_variables]] )

        # Create the array for the flux between variables
        flux = np.zeros((k_objectives, n_variables, n_variables))

        for i in range(k_objectives):
            start = (i+1)*n_variables + 1 + i
            end = (i+2)*n_variables + 1 + i

            # Fill the 3-Matrix
            flux[i] = np.array( [list(map(int, line.split(" "))) for line in file_content[start:end]] )

        # Save positions and weights into self.weights and self.positions
        self.weights = flux
        self.positions = positions

    
    def decode_random_keys(self, solution:np.ndarray) -> list:
        """
        Auxiliar function to decode random_keys into natural numbers.

        @param solution: Numpy array with float numbers.

        :return: List with int numbers.
        """
        # Add index labels
        augmented_keys = list(zip([i for i in range(len(solution))], solution))

        # Sort the keys by the random numbers
        augmented_keys.sort(key = lambda x: x[1])

        # Unzip it and extract the decoded solution
        return list(zip(*augmented_keys))[0]


    def _evaluate(self, x:np.ndarray, out:dict, *args, **kwargs):
        """
        Receives the population form the algorithm and evaluates each individual.
        It end updating the F key of the variable out.
        Current complexity: O(p x k x n^2) where p is population size.

        @param x: Population.
        @param out: Dictionary to update.
        """
        # Get population size
        population_size = len(x[:,0])

        # Allocate memory for fitness values.
        values = np.zeros((population_size, self.k_obj))

        # Verify if solutions are ints or floats.
        if self.kind_solutions.lower() == "real":
            # Convert random-keys into int values
            solutions = np.array([self.decode_random_keys(x[i,:].copy()) for i in range(population_size)])
        else:
            # 
            solutions = x
        
        for i in range(population_size):
            for current_objective in range(self.k_obj):
                values[i, current_objective] = self.cost_of_solution(current_objective, solutions[i,:])

        #for i in range(population):
        #    for current_objective in range(self.k_obj):

        #        values[i,current_objective] = self.cost_of_solution(current_objective, self.decode_random_keys(x[i,:]))

        out["F"] = values

    
    def cost_of_solution(self, function_indx:int, solution:np.ndarray):
        """
        Return the cost of a solution in its respective function
        Current complexity: O(n^2)
        """
        total_cost = 0
        for i in range(len(solution)):
            for j in range(len(solution)):
                total_cost += self.weights[function_indx, i, j] * self.positions[solution[i], solution[j]]

        return total_cost//2

class MOSampling(Sampling):

    def __init__(self, kind: str="real") -> None:
        """
        @param kind: natural or real
        """
        super().__init__()

        self.kind = kind.lower()

    def generate(self, n_var: int, n_samples: int) -> np.ndarray:
        """
        Generate initial solutions.
        
        @param n_var: Number of variables.
        @param n_samples: Number of solutions.

        :return: Initial solutions in a numpy array.
        """
        if self.kind == "real":
            X = np.random.random((n_samples, n_var))
        
        else:
            X = np.zeros((n_samples, n_var), dtype=int)
            for i in range(n_samples):
                X[i] = np.random.permutation(n_var)
        
        return X
    
    def _do(self, problem: Problem, n_samples: int, **kwargs) -> np.ndarray:
        """
        Function for pymoo functionality.
        """

        n_variables = problem.n_var

        X = self.generate(n_variables, n_samples)

        return X
    