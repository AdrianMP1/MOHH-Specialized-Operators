
from handle_params import Params, set_params

from graphviz_creator import map_individuals_to_trees

from plots import make_plots
from individual_operations import generational_metrics
from individual_operations import individual_metrics_json
from individual_operations import individual_metrics_dataframe

def main():

    # Select experiment
    experiment_name: str = ""

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
    full_pop_dfs, full_off_dfs = generational_metrics(metrics_df)

    del metrics_df
    
    # Make plots
    make_plots(full_pop_dfs)
    #make_plots(full_off_dfs, offspring=True)

if __name__ == "__main__":
    main()