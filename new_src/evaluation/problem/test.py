import numpy as np

class MultiObjectiveQAP:
    def __init__(self, weights, positions):
        self.weights = weights
        self.positions = positions

    def cost_of_solution(self, function_indx: int, solution: np.ndarray):
        # Rearrange self.positions based on the solution
        permuted_positions = self.positions[np.ix_(solution, solution)]

        # Perform element-wise multiplication with the corresponding weights
        total_cost = np.sum(self.weights[function_indx] * permuted_positions)

        return total_cost // 2
    
    def non_vectorized(self, function_indx: int, solution: np.ndarray):

        total_cost = 0
        for i in range(len(solution)):
            for j in range(len(solution)):
                total_cost += self.weights[function_indx, i, j] * self.positions[solution[i], solution[j]]

        return total_cost//2

# Test data
M = 2  # Number of objectives
N = 3  # Number of variables

# Example weight matrices for each objective (M, N, N)
weights = np.array([
    [[1, 2, 3, 4],   # Objective 1 weight matrix
     [2, 1, 4, 5],
     [3, 4, 1, 6],
     [4, 5, 6, 1]],
    
    [[3, 2, 1, 2],   # Objective 2 weight matrix
     [2, 3, 4, 3],
     [1, 4, 3, 1],
     [2, 3, 1, 3]]
])

# Example position matrix (N, N)
positions = np.array([
    [0, 5, 2, 4],
    [5, 0, 3, 1],
    [2, 3, 0, 5],
    [4, 1, 5, 0]
])

# Sample solution (permutation of indices)
solution = np.array([2, 0, 1, 3])  # This permutes the positions matrix

# Create an instance of the problem
qap = MultiObjectiveQAP(weights, positions)

# Test the cost calculation for both objectives
for function_index in range(M):
    cost = qap.cost_of_solution(function_index, solution)
    old_cost = qap.non_vectorized(function_index, solution)
    print(f"Cost for objective {function_index + 1}: {cost}")
    print(f"Old cost {function_index+1}: {old_cost}")


