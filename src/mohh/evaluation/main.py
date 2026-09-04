
from mohh.evaluation.params import Params
from mohh.evaluation.experiment import run_experiments
from mohh.evaluation.make_plots import make_figures

def execute_experiments(experiment_path, results_paths, operators, overrides: dict = None):

    # First run the experiments and generate data
    evaluation_path = run_experiments(experiment_path, results_paths, operators, overrides)

    # Make figures in the results_path
    make_figures(evaluation_path)

    # Reset params
    params = Params()
    params.reset_instance()

