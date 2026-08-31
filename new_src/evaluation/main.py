
from evaluation.params import Params
from evaluation.experiment import run_experiments
from evaluation.make_plots import make_figures

def execute_experiments(experiment_path, results_paths, operators):

    # First run the experiments and generate data
    evaluation_path = run_experiments(experiment_path, results_paths, operators)

    # Make figures in the results_path
    make_figures(evaluation_path)

    # Reset params
    params = Params()
    params.reset_instance()
    

if __name__ == "__main__":

    # First run the experiments and generate data
    results_path = run_experiments()

    # Make figures in the results_path
    make_figures(results_path)
    