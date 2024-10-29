from experiment import run_experiments
from make_plots import make_figures

if __name__ == "__main__":

    # First run the experiments and generate data
    results_path = run_experiments()

    # Make figures in the results_path
    make_figures(results_path)
    