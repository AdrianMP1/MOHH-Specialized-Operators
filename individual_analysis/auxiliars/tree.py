
import copy
import numpy as np

from auxiliars.test_functions import *

terminals = ["x", "y"]
arithmetics = ["+", "-"]

class Node:
    def __init__(self, value):
        self.value = value
        self.children = []
        #self.terminals = ["x","y"]
        #self.arithmetics = ["+", "-"]

    def __repr__(self):
        return f"{self.value}({', '.join(map(str, self.children))})"
    
    def phenotype(self):

        if self.value in terminals:
            return str(self.value)
        
        elif self.value in arithmetics:
            return f"({self.children[0].phenotype()} {self.value} {self.children[1].phenotype()})"

        else:
            return f"{self.value}({', '.join([child.phenotype() for child in self.children])})"
    
    def evaluate(self, inputs: list[list[float]]):
        x, y = inputs
        x = np.array(x)
        y = np.array(y)
        return eval(self.phenotype())
    
    def copy(self):

        # Deep copy of the tree node
        node_copy = Node(self.value)
        node_copy.children = [copy.deepcopy(child) for child in self.children]
        
        return node_copy
    
    def remove_subtree(self, index):
        
        # Removes a subtree at the given index.
        if index < len(self.children):
            return self.children.pop(index)