
from handle_params import Params, set_params

from graphviz_creator import map_individuals_to_trees

from individual_operations import load_generation
from individual_operations import get_num_generations
from individual_operations import compute_hypervolumes
from individual_operations import phenotypes_to_trees
from individual_operations import compute_metrics

def main():

    # Select experiment
    experiment_name: str = "DESKTOP-E3F66CS_2024_8_26_2217_148643"

    # Set parameters
    set_params(experiment_name)
    
    # Create individuals tree representation
    map_individuals_to_trees()

    num_generations: int = get_num_generations()

    for gen in range(num_generations):

        # Get current generation phenotypes.
        pop_phenotypes, off_phenotypes = load_generation(gen)

        # TODO: This is computing fine. Maybe the graphs/figures of HVs & Fronts
        # TODO: Should be inside compute_hypervolumes since the functions access
        # TODO: the fronts inside its loops.
        # Compute HVs and fitness
        rankings, hypervolumes = compute_hypervolumes(pop_phenotypes, gen)

        # Map phenotypes into trees
        pop_trees = phenotypes_to_trees(pop_phenotypes)
        off_trees = phenotypes_to_trees(off_phenotypes)

        # TODO: Start making graphs!!!
        compute_metrics(pop_trees, rankings, hypervolumes)
        

if __name__ == "__main__":
    main()