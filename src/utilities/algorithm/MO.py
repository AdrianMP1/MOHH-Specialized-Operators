
import numpy as np

from params import Params
from pymoo.indicators.hv import HV

params = Params()

sign = 1
if not(params["OPTIMIZATION_KIND"]):
    sign = -1

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
    
    return fronts


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