
import numpy as np

from mohh.core.params import Params
from pymoo.indicators.hv import HV

params = Params()

sign = 1
if not(params["OPTIMIZATION_KIND"]):
    sign = -1


def dominates_vectorized(p, q):
    # Verify if p dominates q
    return np.all(p >= q) and np.any(p > q)

def non_dominated_sorting_vectorized(population: set):

    # Convert set to numpy array
    population = np.array(list(population))

    # Adjust population values (1 for maximization, -1 for minimization)
    adjusted_population = population * sign

    N = adjusted_population.shape[0]
    is_dominated = np.zeros(N, dtype=bool)

    for i in range(N):
        if is_dominated[i]:
            # Skip if dominated
            continue
            
        for j in range(N):
            if dominates_vectorized(adjusted_population[i], adjusted_population[j]):
                is_dominated[j] = True
            elif dominates_vectorized(adjusted_population[j], adjusted_population[i]):
                is_dominated[i] = True
                break

    front = population[~is_dominated]
    front_set = [tuple(p) for p in front]

    return [front_set]


def compute_nadir_point(front: set):

    if params["OPTIMIZATION_KIND"]:
        # Maximize problem
        nadir_point = list(map(min, zip(*front)))
    else:
        # Minimize problem
        nadir_point = list(map(max, zip(*front)))
    return nadir_point


def compute_hypervolume(ref_point: np.ndarray, front: np.ndarray) -> float:

    # Load the indicator
    indicator = HV(ref_point = ref_point)

    # Compute the metric
    hv = indicator(front)

    return hv

