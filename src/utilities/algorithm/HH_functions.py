
import numpy as np

def sin(x:np.ndarray) -> np.ndarray:
    return np.sin(x)

def cos(x:np.ndarray) -> np.ndarray:
    return np.cos(x)

def exp(x:np.ndarray) -> np.ndarray:
    return np.exp(x)

def log(x:np.ndarray) -> np.ndarray:
    return np.log(x)

def convolution(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """
    Arity: 2
    Convolve parent1 with kernel = parent2
    """
    return np.convolve(x, y, "same")

def one_point(parent1:np.ndarray, parent2:np.ndarray):
    """
    # * One Point Crossover
    @param parent1 1D numpy array
    @param parent2 1D numpy array 
    """

    crossover_point = np.random.randint(1, min(len(parent1), len(parent2)) - 1)
    child1 = np.concatenate((parent1[:crossover_point], parent2[crossover_point:]))
    child2 = np.concatenate((parent2[:crossover_point], parent1[crossover_point:]))
    return child1

def masked_cross(parent1:np.ndarray, parent2:np.ndarray):
    """
    # * Masked Crossover
    @param parent1 1D numpy array 
    @param parent2 1D numpy array 
    """
    n_var = len(parent1)

    # For each mating provided
    child1 = np.zeros_like(parent1)
    child2 = np.zeros_like(parent2)

    mask = np.random.randint(0, 2, size=n_var).astype("bool")
    child1[mask] = parent1[mask]
    child1[~mask] = parent2[~mask]

    child2[~mask] = parent1[~mask]
    child2[mask] = parent2[mask]

    return child1