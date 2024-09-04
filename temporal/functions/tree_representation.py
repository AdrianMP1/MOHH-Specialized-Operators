import copy

class Node:
    def __init__(self, value):
        self.value = value
        self.children = []

    def __repr__(self):
        return f"{self.value}({', '.join(map(str, self.children))})"
    
    def evaluate(self, inputs):
        pass

    def copy(self):

        # Deep copy of the tree node
        node_copy = Node(self.value)
        node_copy.children = [copy.deepcopy(child) for child in self.children]
        
        return node_copy
    
    def remove_subtree(self, index):
        
        # Removes a subtree at the given index.
        if index < len(self.children):
            return self.children.pop(index)
        
