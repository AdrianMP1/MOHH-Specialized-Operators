
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


def non_dominated_sorting(solutions):
    """
    Compute the non dominated sorting.
    """

    fronts = [[]]
    rank = dict()

    domination_count = dict()
    dominated_solutions = dict()
    
    for p in solutions:
        
        dominated_solutions[p] = []
        domination_count[p] = 0

        # Compute the domination counter of p
        for q in solutions:

            if dominates(p, q):
                # Add q to the set of solutions dominated by p
                dominated_solutions[p].append(q)
            elif dominates(q, p):
                domination_count[p] += 1
        
        # If p belongs to the first front
        if domination_count[p] == 0:
            fronts[0].append(p)
            rank[p] = 0
        
    i = 0

    while len(fronts[i]) > 0:

        big_q = []

        for p in fronts[i]:

            for q in dominated_solutions[p]:
                domination_count[q] -= 1

                # If counter reaches 0, the solution is added to the next front
                if domination_count[q] == 0:
                    rank[q] = i + 1
                    big_q.append(q)
        
        i += 1

        fronts.append(big_q)
    
    # TODO: Hard-coded temporarily.
    return fronts[:3]


def dominates(individual1, individual2):
    """
    Return True if individual 1 dominates individual 2, else False.
    """

    better_in_at_least_one = False

    # Check if A is strictly better than B in at least one objective
    for a, b in zip(individual1, individual2):
        if sign * a < sign * b:
            # If A is worse in any objective, it doesn't dominates B
            return False
        if sign * a > sign * b:
            # If A is better in any objective, mark this condition
            better_in_at_least_one = True
    
    # A dominates B if A is better in at least one objective and
    # equal in the others.

    return better_in_at_least_one


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


import matplotlib.pyplot as plt
if __name__ == "__main__":

    points = np.random.rand(50,2)

    points_set = set([tuple(p) for p in points])

    front = non_dominated_sorting_vectorized(points_set)

    front = np.array(front[0])

    plt.scatter(points[:,0], points[:,1])
    plt.scatter(front[:,0], front[:,1], c="r")

    plt.show()
