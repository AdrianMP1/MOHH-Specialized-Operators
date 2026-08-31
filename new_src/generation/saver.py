
import json
import hashlib
import logging
import numpy as np

from generation.params import Params
from os import getcwd, makedirs, path

class PopulationSaver():
    _instance = None

    # Singleton functionality
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(PopulationSaver, cls).__new__(cls)
        
        return cls._instance

    def __init__(self, experiment_path: str = None,
                current_model: str = None, file_format: str="json") -> None:
        if not hasattr(self, "initialized"):

            params = Params()
            self.base_save_dir = params[""]
            self.file_format = file_format
            self.individuals_dir = None
            self.generations_dir = None
            self.initial_solutions_dir = None
            self.existing_individuals = set()

            # Initialize folders for a new run
            self._initialize_directories(experiment_path, current_model)
            self.initialized = True

    def _initialize_directories(self, experiment_path: str, current_model: str):
        """
        Generates neccesary folders and files for saving statistics and parameters.
        """

        # Load parameters
        params = Params()

        if params['EXPERIMENT_NAME']:
            # Experiment manager is being used.
            path_1 = path.join(getcwd(), "results")

            if not path.isdir(path_1):
                # Create results folder.
                makedirs(path_1, exist_ok=True)

            # Set file path to include experiment name.
            params['FILE_PATH'] = path.join(path_1, params['EXPERIMENT_NAME'])

        else:
            # Set file path to results folder.
            #params['FILE_PATH'] = path.join(getcwd(), "results")
            params['FILE_PATH'] = path.join(getcwd(), experiment_path)

        # Generate save folders
        if not path.isdir(params['FILE_PATH']):
            makedirs(params['FILE_PATH'], exist_ok=True)

        if not path.isdir(path.join(params['FILE_PATH'],
                                    current_model + "_" + str(params['TIME_STAMP']))):
            makedirs(path.join(params['FILE_PATH'],
                               current_model + "_" + str(params['TIME_STAMP'])), exist_ok=True)

        params['FILE_PATH'] = path.join(params['FILE_PATH'],
                                        current_model + "_" + str(params['TIME_STAMP']), "generation_results")

        for name in ["individuals", "initial_solutions", "generations"]:

            # Make directory
            if not path.isdir(path.join(params["FILE_PATH"], name)):
                makedirs(path.join(params["FILE_PATH"], name), exist_ok=True)
            
            # Save in params
            params["FILE_PATH_"+name.upper()] = path.join(params["FILE_PATH"], name)

            # Set attribute.
            setattr(self, name + "_dir", params["FILE_PATH_" + name.upper()])

        self._save_params_to_file()

    def _save_params_to_file(self):
        """
        Save evolutionary parameters in a parameters.txt file.

        :return: Nothing.
        """

        # Load parameters
        params = Params()

        # Generate file path and name.
        filename = path.join(params['FILE_PATH'], "parameters.txt")
        savefile = open(filename, 'w')

        # Justify whitespaces for pretty printing/saving.
        col_width = max(len(param) for param in params.keys())

        for param in sorted(params.keys()):
            # Create whitespace buffer for pretty printing/saving.
            spaces = [" " for _ in range(col_width - len(param))]
            savefile.write(str(param) + ": " + "".join(spaces) +
                           str(params[param]) + "\n")

        savefile.close()

    def _generate_individual_id(self, individual):
        # Use a hash of the individual's genome
        unique_string = json.dumps(individual.genome)
        return hashlib.md5(unique_string.encode()).hexdigest()
    
    def save_consolidated_fronts(self, instances, generation: int):

        # Generation directory
        generation_dir = path.join(self.generations_dir, f"generation_{generation:04d}")
        makedirs(generation_dir, exist_ok=True)

        # Save consolidated fronts per instance
        for instance in instances:
            instance_name = instance.instance_name

            # List with fronts
            fronts = instance.fronts

            # Consolidated front
            consolidated = instance.non_dominated_front

            # Prepare data for json.
            data = {f"Front_{i:03d}": front for i, front in enumerate(fronts)}
            data["consolidated"] = list(consolidated)
            data["nadir_point"] = instance.nadir_point
            data["num_variables"] = instance.n_variables
            data["num_objectives"] = instance.k_objectives

            # File path
            save_path = path.join(generation_dir, f"Instance_Fronts_{instance_name}.{self.file_format}")

            with open(save_path, "w") as file:
                json.dump(data, file, indent=4)

    def save_population(self, population, generation: int):

        offspring_data = []
        population_data = []
        generation_dir = path.join(self.generations_dir, f"generation_{generation:04d}")
        makedirs(generation_dir, exist_ok=True)

        for individual in population.individuals:
            #individual_id = self._generate_individual_id(individual) 
            individual_id = individual.name
            individual_dir = path.join(self.individuals_dir, individual_id)

            if individual_id not in self.existing_individuals:
                # Make individual directory
                makedirs(individual_dir, exist_ok=True)

                # Save general info
                self._save_individual_general_info(individual, individual_dir, generation)

                # Add it to the existing set
                self.existing_individuals.add(individual_id)
            
                # Save instance-specific data for this generation
                for instance_id in individual.pareto_fronts.keys():

                    # Save fronts, sets, solutions, etc...
                    self._save_individual_instance_data(individual, instance_id, individual_dir)

            # Classify between offspring and population.
            # Add the individual's ID to the generation's list
            if individual.is_offspring:
                offspring_data.append(individual_id)
            else:
                population_data.append(individual_id)
        
        # TODO: Save hypervolume and fitness per generation?

        # If there are offsprings
        if offspring_data:
            self._save_generation_data(offspring_data, generation_dir, offspring=True)
        
        else:
            # Save the generation data (list of individual ID's)
            self._save_generation_data(population_data, generation_dir)

    def _save_individual_general_info(self, individual, individual_dir, generation):
        # Save general information of the individual
        individual_info = {
            "name":individual.name,
            "phenotype":individual.phenotype,
            "number_nodes":individual.nodes,
            "codons_usage":individual.used_codons,
            "depth":individual.depth,
            "born_in_generation": generation,
            "genome":individual.genome,
        }

        save_path = path.join(individual_dir, f"general_info.{self.file_format}")
        with open(save_path, "w") as file:
            json.dump(individual_info, file, indent=4)
    
        # TODO: Save a tree representation of the individual.
        # Create tree figure.

        # Save it as png.

    def _save_individual_instance_data(self, individual, instance_name, individual_dir):
        # Save instance-specific data for the individual

        # Extract and preprocess data
        front = individual.pareto_fronts[instance_name].copy()
        sol_set = individual.pareto_sets[instance_name].copy()

        # If real numbers, round them up to 4 decimals.
        if sol_set.dtype == float:
            sol_set = np.round(sol_set, 4)
        
        # Convert into python lists
        front_list = front.tolist()
        sol_set_list = sol_set.tolist()

        data = {
            #"fitness_value": 
            #"hypervolume":individual.hypervolumes[instance_name],
            "number_unique_solutions": individual.unique_solutions[instance_name],
            "weak_non_dominated_solutions":individual.weak_non_dominated[instance_name],
            "strong_non_dominated_solutions":individual.strong_non_dominated[instance_name],
            "front":front_list,
            "solution_set":sol_set_list,
        }

        save_path = path.join(individual_dir, f"instance_{instance_name}.{self.file_format}")
        with open(save_path, "w") as file:
            json.dump(data, file, indent=4)

    def _save_generation_data(self, generation_data, generation_dir, offspring: bool = False):

        # Define offspring or population.
        name_dir = "offspring" if offspring else "population"

        # Save the list of individuals IDs (or names) for the current generation
        population_file_path = path.join(generation_dir, f"{name_dir}.{self.file_format}")
        
        with open(population_file_path, "w") as file:
            json.dump(generation_data, file, indent=4)

    def _consolidate_instance_fronts(self, generation_data, instance_id):
        pass

    @classmethod
    def reset_instance(cls):
        cls._instance = None


class MyLogger():

    # Variable to hold singleton
    _instance = None

    def __new__(cls):

        # Verify if there is already an instance
        if cls._instance is None:
            # Create a new instance
            cls._instance = super(MyLogger, cls).__new__(cls)
        
        return cls._instance
    
    def __init__(self):

        # Check if logger has already been initialized
        if hasattr(self, "logger"):
            return
        
        # Load parameters for paths.
        params = Params()
        experiment_path = params["FILE_PATH"]
        log_path = path.join(experiment_path, "CLI_output.log")

        # Configure the logger
        self.logger = logging.getLogger("MyLogger")
        self.logger.setLevel(logging.INFO)

        # Create a file handler to save logs
        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(logging.INFO)

        # Create a console handler to print to the console
        #console_handler = logging.StreamHandler()
        #console_handler.setLevel(logging.INFO)

        # Define the format
        formatter = logging.Formatter("%(asctime)s :: %(message)s")
        file_handler.setFormatter(formatter)
        #console_handler.setFormatter(formatter)

        # Add handlers
        self.logger.addHandler(file_handler)
        #self.logger.addHandler(console_handler)
    
    def get_logger(self) -> logging.Logger:
        # Access the logger instance
        return self.logger
    
    def close_logger(self) -> None:
        # Close file
        handlers = self.logger.handlers[:]
        for handler in handlers:
            handler.close()
            self.logger.removeHandler(handler)

    @classmethod
    def reset_instance(cls):
        
        if cls._instance is not None:
            # Close handler
            cls._instance.close_logger()
            cls._instance = None
            