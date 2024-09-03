
import os
from graphviz import Digraph
from parser import Node

def add_nodes_edges(graph: Digraph, node: Node, parent=None):
    
    # Add node
    graph.node(str(id(node)), label=node.value)

    # Add edge if current node has a parent
    if parent:
        graph.edge(str(id(parent)), str(id(node)))
    
    # Recursively, apply the function to the children
    for child in node.children:
        graph = add_nodes_edges(graph, child, node)
    
    return graph


def make_visual_tree(syntax_tree):

    # Make graph
    graph = Digraph()
    
    # Add nodes and edges
    # TODO: We have a problem, it doesn't update graph due to global local functions.
    graph = add_nodes_edges(graph, syntax_tree)

    return graph


def render_tree(graph: Digraph, file_path: str, name: str, expr: str) -> None:

    # Make save_path
    save_path = os.path.join(file_path, f"Tree_{name}.gv")

    # Add footer
    graph.attr(kw='graph', label = f"\n{name}\n{expr}")

    # Render it
    graph.render(save_path, format="png")

