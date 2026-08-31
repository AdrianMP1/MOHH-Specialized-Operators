
from mohh.generation.params import Params, set_params
from mohh.generation.algorithm.hyperheuristic import HyperHeuristic
from mohh.core.utilities.instance_utils import instance_paths

def execute_generation(mo_model: str, experiment_path: str) -> str:

    # First set the parameters of the experiment
    set_params(experiment_path, mo_model)

    # Load params
    params = Params()

    # Assemble an algorithm with its operators
    algorithm = (HyperHeuristic()
                 .load_operator("initialization", params["INITIALIZATION"])
                 .load_operator("selection", "Tournament", k=params["TOURNAMENT_SIZE"])
                 .load_operator("crossover", "KPointCrossover", n_parents=params["CROSSOVER_PARENTS"], k_points=params["CROSSOVER_K_POINTS"])
                 .load_operator("mutation", "BitFlipMutation", probability=params["MUTATION_PROBABILITY"])
                 )
    
    algorithm.mo_model_name = mo_model

    # Get instances
    instances = instance_paths(train=True)

    # Load instances to solve / train
    algorithm.load_instances(instances)

    # Execute algorithm
    algorithm.run()

    # Reset params singleton
    params_dict = params.get_params()
    params.reset_instance()

    # Return the path with the last generation operators
    return params_dict["FILE_PATH"], params_dict["FILE_PATH_GENERATIONS"], params_dict["FILE_PATH_INDIVIDUALS"], params_dict["ELITE_SIZE"]

if __name__ == "__main__":

    execute_generation()
