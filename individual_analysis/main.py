
from handle_params import Params, set_params

from graphviz_creator import map_individuals_to_trees

from individual_operations import generational_metrics
from individual_operations import individual_metrics_json
from individual_operations import individual_metrics_dataframe

def main():

    # Select experiment
    experiment_name: str = "DESKTOP-E3F66CS_2024_8_26_2217_148643"

    # Set parameters
    set_params(experiment_name)
    
    # Create individuals tree representation
    map_individuals_to_trees()

    # Compute generation independent metrics
    ## Balance, Skewness, Depth, Size, Entropy, Path Length Variance
    ## HVs per instance with nadir point from the last generation.
    metrics_df = individual_metrics_dataframe()
    
    # Compute generation independent & non-dataframe metrics
    ## Subtree frequency, Subtree depths, Non-Terminals Rate
    individual_metrics_json()

    # Compute generation dependent metrics
    pop_df, off_df = generational_metrics(metrics_df)

    # TODO: Now, we have the data structured, we can start making the plots.
    
    # TODO: The only thing yet to do is, where the fronts should be plotted?

if __name__ == "__main__":
    main()