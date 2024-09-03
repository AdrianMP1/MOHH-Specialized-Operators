
from graphviz import Digraph
from individuals_tree.parser import Node

def add_nodes_edges(graph: Digraph, node: Node, parent=None):
    
    # Add node
    graph.node(str(id(node)), label=node.value)

    # Add edge if current node has a parent
    if parent:
        graph.edge(str(id(parent)), str(id(node)))
    
    # Recursively, apply the function to the children
    for child in node.children:
        add_nodes_edges(graph, child, node)
    



def make_visual_tree(syntax_tree):

    # Make graph
    graph = Digraph()
    
    # Add nodes and edges
    # TODO: We have a problem, it doesn't update graph due to global local functions.
    add_nodes_edges(graph, syntax_tree)

    return graph
