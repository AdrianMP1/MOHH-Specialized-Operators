
import numpy as np

# * REAL OPERATORS
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

# * PERMUTATION OPERATORS

# Unary functions

def swap(x):
    """
    Swap two variables from a solution
    """

    # Make sure x is one list
    x = verify_inputs(x)

    n_var = len(x)

    # Two random numbers without replacement
    i, j = np.random.choice(n_var, size=2, replace=False)
    
    # Swap elements at the chosen indices
    x[i], x[j] = x[j], x[i]
    
    return x

def move_right(x):
    """
    Move all elements to the right.
    """
    # Make sure x is one list
    x = verify_inputs(x)

    # Rotate the array
    return np.concatenate(([x[-1]], x[:-1]))

def reverse(x):
    """
    Reverse the elements.
    """
    # Make sure x is one list
    x = verify_inputs(x)

    return x[::-1]

# Binary functions

def map_list(x, y):

    # Make sure x is one list
    x = verify_inputs(x)
    
    # Make sure y is one list
    y = verify_inputs(y)

     # Ensure y contains valid indices
    if not np.all((y >= 0) & (y < len(x))):
        raise ValueError("All elements of y must be valid indices for x and y.")

    if not np.all((x >= 0) & (x < len(y))):
        raise ValueError("All elements of x must be valid indices for x and y.")
    
    new_x = x[y]
    new_y = y[x]

    return new_x, new_y

def alternate_elements(x, y):
    """
    Alternate each element of both parents
    """
    # Make sure x is one list
    x = verify_inputs(x)
    
    # Make sure y is one list
    y = verify_inputs(y)

    new_x = []
    new_y = []

    for i in range(len(x)):

        if np.random.rand() < 0.5:
            new_x.extend([x[i], y[i]])
            new_y.extend([y[i], x[i]])
        
        else:
            new_x.extend([y[i], x[i]])
            new_y.extend([x[i], y[i]])

    # Traverse each new list and remove duplicates
    new_x, new_y = np.array(new_x), np.array(new_y)

    _, indx = np.unique(new_x, return_index=True)
    new_x = new_x[np.sort(indx)]

    _, indx = np.unique(new_y, return_index=True)
    new_y = new_y[np.sort(indx)]

    return new_x, new_y

def alternate_segments(x, y):
    """
    Alternate list segments.

    x and y are list of lists.
    The number of sublists must match
    """

    if len(x) != len(y):
        print("Alternate segments: No of Sublists doesn't match.")
        raise(ValueError)

    new_x = []
    new_y = []


    for i in range(len(x)):

        if np.random.rand() < 0.5:
            new_x.extend(x[i])
            new_x.extend(y[i])

            new_y.extend(y[i])
            new_y.extend(x[i])

        else:
            new_x.extend(y[i])
            new_x.extend(x[i])

            new_y.extend(x[i])
            new_y.extend(y[i])
    
    # Traverse each new list and remove duplicates
    new_x, new_y = np.array(new_x), np.array(new_y)

    _, indx = np.unique(new_x, return_index=True)
    new_x = new_x[np.sort(new_x)]

    _, indx = np.unique(new_y, return_index=True)
    new_y = new_y[np.sort(indx)]

    return new_x, new_y

def preserve_elements(x):
    """
    Select some elements.
    """

    # Make sure x is one list
    x = verify_inputs(x)

    # Select k elements
    k = np.random.randint(1, len(x))

    # Convert to numpy if not already
    x = np.array(x)

    # Select k indices without replacements
    selected = np.random.choice(len(x), size=k, replace=False)

    # Create result list
    #result = [[] for _ in range(len(x))]
    #for indx in selected:
    #    result[indx] = [x[indx]]

    result = -np.ones_like(x)
    result[selected] = x[selected]
    
    return result

def preserve_segments(x):
    """
    Select segments
    """

    # Make sure x is one list
    x = verify_inputs(x)

    # Select two random indices
    i = 0
    j = len(x) - 1
    while (i == 0 and j == len(x) - 1) or (i == j):
        selected = np.sort(np.random.choice(len(x), size=2, replace=False))
        i, j = selected
        j -= 1

    # The segments are 0 -> i, i+1 -> j, j+1 -> N
    # Preserve the one at the middle.
    
    # Result array
    #result = [[] for _ in range(3)]
#
    #if i == 0:
    #    result[0] = x[i:j]
#
    #elif j == len(x) - 1:
    #    result[2] = x[i:j]
#
    #else:
    #    # Preserve the middle segment (i+1 -> j)
    #    result[1] = x[i:j]

    result = -np.ones_like(x)
    result[i:j] = x[i:j]

    return result


def fill_first_occurring(preserved, filler):
    """
    Fill preserved with filler
    """

    # Make sure x is one list
    preserved = verify_inputs(preserved)
    
    # Make sure y is one list
    filler = verify_inputs(filler)

    # Find the elements of preserved
    existing_values = set(preserved[preserved != -1])

    j = 0
    for i in range(len(preserved)):
        
        while preserved[i] == -1:
            
            if filler[j] not in existing_values:
                preserved[i] = filler[j]
            
            j += 1

    #for i, element in enumerate(filler):
    #    if (element not in existing_values) and preserved[i] == -1:
    #        preserved[i] = element
    
    return preserved

def order_based(fill_method, preserve_method, x, y):
    """
    fill_method is how to rebuild (chosed by the grammar)
    preserve_method selects segments or elements (chosed by the grammar)
    x is a terminal
    y is a terminal
    """

    # Make sure x is one list
    x = verify_inputs(x)
    
    # Make sure y is one list
    y = verify_inputs(y)

    # First, select the elements to preserve
    preserved_data_x = preserve_method(x)
    preserved_data_y = preserve_method(y) 

    # Fill the empty slots with the second parent
    new_x: np.ndarray = fill_method(preserved_data_x, y)
    new_y: np.ndarray = fill_method(preserved_data_y, x)

    return new_x, new_y

def collapse(x, y=None):

    return x

def verify_inputs(x):
    
    # Make sure x is one list
    if isinstance(x, tuple):
        x = collapse(x[0], x[1])
    
    return x