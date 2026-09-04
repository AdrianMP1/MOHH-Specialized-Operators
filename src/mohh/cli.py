
import argparse

from mohh.main import make_experiment_path, run_generation
from mohh.run_evaluation import discover_models, extract_operators
from mohh.evaluation.main import execute_experiments
from mohh.evaluation.params import params_dict as evaluation_params_dict

def _generation_overrides(args) -> dict:

    overrides = {}

    if args.population_size is not None:
        overrides["POPULATION_SIZE"] = args.population_size
    if args.generations is not None:
        overrides["GENERATIONS"] = args.generations
    if args.elite_size is not None:
        overrides["ELITE_SIZE"] = args.elite_size
    if args.mo_population_size is not None:
        overrides["MO_POPULATION_SIZE"] = args.mo_population_size
    if args.mo_generations is not None:
        overrides["MO_GENERATIONS"] = args.mo_generations

    return overrides

def _parse_eval_budgets(value: str) -> dict:

    budgets = {}

    for pair in value.split(","):
        label, budget = pair.split(":")
        budgets[label] = int(budget)

    return budgets

def _evaluation_overrides(args, solvers: list, models: list) -> dict:

    overrides = {"SOLVERS": solvers, "MODELS": models}

    if args.mo_population_size is not None:
        overrides["MO_POPULATION_SIZE"] = args.mo_population_size
    if args.mo_generations is not None:
        overrides["MO_GENERATIONS"] = args.mo_generations
    if args.n_experiments is not None:
        overrides["N_EXPERIMENTS"] = args.n_experiments
    if args.eval_budgets is not None:
        overrides["EVAL_BUDGETS"] = _parse_eval_budgets(args.eval_budgets)

    return overrides

def _add_mo_args(parser: argparse.ArgumentParser):

    parser.add_argument("--mo-population-size", type=int, default=None)
    parser.add_argument("--mo-generations", type=int, default=None)

def _add_eval_budgets_arg(parser: argparse.ArgumentParser):

    parser.add_argument("--eval-budgets", default=None,
                        help="Comma-separated label:evaluations pairs, e.g. 10k:10500,30k:31500,50k:52500.")

def _add_solvers_arg(parser: argparse.ArgumentParser):

    parser.add_argument("--solvers", default=None,
                        help="Comma-separated MOEAs to benchmark with (default: from params).")

def generate():

    parser = argparse.ArgumentParser(description="Run the GE hyper-heuristic to generate variation operators.")
    parser.add_argument("--models", default="MOEAD", help="Comma-separated MOEA models to try (default: MOEAD).")
    parser.add_argument("--population-size", type=int, default=None)
    parser.add_argument("--generations", type=int, default=None)
    parser.add_argument("--elite-size", type=int, default=None)
    _add_mo_args(parser)
    args = parser.parse_args()

    models = args.models.split(",")
    overrides = _generation_overrides(args)

    experiment_path = make_experiment_path()
    run_generation(experiment_path, models, overrides)

    print(f"\nGeneration complete: {experiment_path}")

def evaluate():

    parser = argparse.ArgumentParser(description="Benchmark discovered operators against unseen instances.")
    parser.add_argument("experiment_path", help="Path to an experiment folder produced by mohh-generate.")
    parser.add_argument("--models", default=None,
                        help="Comma-separated generation models to pull operators from (default: auto-detect from experiment_path).")
    _add_solvers_arg(parser)
    parser.add_argument("--n-experiments", type=int, default=None)
    _add_mo_args(parser)
    _add_eval_budgets_arg(parser)
    args = parser.parse_args()

    models = args.models.split(",") if args.models else discover_models(args.experiment_path)
    solvers = args.solvers.split(",") if args.solvers else evaluation_params_dict["SOLVERS"]
    overrides = _evaluation_overrides(args, solvers, models)

    operators = extract_operators(args.experiment_path, models)
    execute_experiments(args.experiment_path, "", operators, overrides)

def run_full():

    parser = argparse.ArgumentParser(description="Run generation followed by evaluation end-to-end.")
    parser.add_argument("--full", action="store_true",
                        help="Confirm you want to run both stages (evaluation is expensive).")
    parser.add_argument("--models", default="MOEAD", help="Comma-separated MOEA models to try (default: MOEAD).")
    parser.add_argument("--population-size", type=int, default=None)
    parser.add_argument("--generations", type=int, default=None)
    parser.add_argument("--elite-size", type=int, default=None)
    parser.add_argument("--n-experiments", type=int, default=None)
    _add_mo_args(parser)
    _add_eval_budgets_arg(parser)
    _add_solvers_arg(parser)
    args = parser.parse_args()

    if not args.full:
        parser.error("Pass --full to confirm you want to run generation followed by evaluation end-to-end (evaluation is expensive).")

    models = args.models.split(",")
    gen_overrides = _generation_overrides(args)
    solvers = args.solvers.split(",") if args.solvers else evaluation_params_dict["SOLVERS"]
    eval_overrides = _evaluation_overrides(args, solvers, models)

    experiment_path = make_experiment_path()
    phenotypes = run_generation(experiment_path, models, gen_overrides)

    execute_experiments(experiment_path, "", phenotypes, eval_overrides)
