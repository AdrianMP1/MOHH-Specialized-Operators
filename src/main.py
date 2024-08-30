
from params import Params, set_params
from algorithm.hyperheuristic import HyperHeuristic
from utilities.instance_utils import instance_paths

if __name__ == "__main__":

    # First set the parameters of the experiment
    set_params()

    # Load params
    params = Params()

    # Assemble an algorithm with its operators
    algorithm = (HyperHeuristic()
                 .load_operator("initialization", params["INITIALIZATION"])
                 .load_operator("selection", "Tournament", k=params["TOURNAMENT_SIZE"])
                 .load_operator("crossover", "KPointCrossover", n_parents=params["CROSSOVER_PARENTS"], k_points=params["CROSSOVER_K_POINTS"])
                 .load_operator("mutation", "BitFlipMutation", probability=params["MUTATION_PROBABILITY"])
                 )

    # Get instances
    instances = instance_paths()

    # Load instances to solve / train
    algorithm.load_instances(instances)

    # Execute algorithm
    algorithm.run()
