
import numpy as np

from params import Params
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
        self.initial_solutions: np.ndarray = []

        # Each instance has a current non-dominated front
        self.fronts: list = []
        self.non_dominated_front: set = set()
        self.nadir_point: list = []
        self.previous_nadir_point: list = []

        # Update instance id
        Instance.num_instances_created += 1
        self.instance_id :str = f"Instance_{Instance.num_instances_created:03d}"

    def create_initial_solution(self) -> None:
        """
        Generates an initial solution.
        It must be executed only one time per instance.
        """

        params = Params()

        # Generate them.
        generator = MOSampling(kind=self.solution_type)
        self.initial_solutions = generator.generate(self.n_variables,
                                                self.population_size)
        
        # Save it to disk.
        file_path = params["FILE_PATH_INITIAL_SOLUTIONS"]

        with open(file_path + "/" + self.file_name + ".txt", "w") as f:
            for i in range(self.population_size):
                # Extract an individual and format it to string
                sol = self.initial_solutions[i].tolist()
                
                if self.solution_type == "real":
                    sol = ", ".join(["{:.04f}".format(w) for w in sol])
                else:
                    sol = ", ".join(["{:03d}".format(w) for w in sol])
                    
                sol = "[" + sol + "]\n"

                # Write on file
                f.write(sol)

            # Close the file
            f.close()

    def load_problem(self, problem_type: str, file_name: str) -> None:
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
            self.create_initial_solution()

            ## Create an initial nadir point
            self.previous_nadir_point = [0] * self.k_objectives

            ## Create instance problem
            self.problem = QuadraticAssignment(self.n_variables, self.k_objectives,
                                                self.file_path, self.solution_type)

        elif problem_type.lower() == "tsp":
            # Loads a tsp instance
            pass

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

class QuadraticAssignment(Problem):
    pass

class MOSampling(Sampling):
    pass

