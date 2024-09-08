
import os
from tqdm import tqdm

from graphviz import Digraph
from handle_params import Params

from auxiliars.tree import Node
from auxiliars.read_files import read_json
from auxiliars.tree_parser import parse_expression


def add_nodes_edges(graph: Digraph, node: Node, parent: Node=None) -> Digraph:

    # Add node
    graph.node(str(id(node)), label=node.value)

    # Add edge if current node has a parent
    if parent:
        graph.edge(str(id(parent)), str(id(node)))
    
    # Recursively apply the function to the children
    for child in node.children:
        graph = add_nodes_edges(graph, child, node)
    
    return graph


def make_graphviz_tree(syntax_tree: Node) -> Digraph:

    # Make graph
    graph = Digraph()

    graph = add_nodes_edges(graph, syntax_tree)

    return graph


def render_tree(graph: Digraph, file_path: str, name: str, expr: str) -> None:

    # Get save path
    save_path = os.path.join(file_path, f"Tree_{name}.gv")

    # Add footer
    graph.attr(kw="graph", label=f"\n{name}\n{expr}")

    # Render it
    graph.render(save_path, format="png")


def map_individuals_to_trees() -> None:

    params = Params()

    individuals_path = params["INDIVIDUALS_PATH"]

    # Verify if the individuals have already been mapped into trees.
    if os.path.exists(os.path.join(individuals_path, "all_read_trees.json")):
        return
    
    # If not, loop over every individual
    for individual in tqdm(os.listdir(individuals_path)):

        current_path = os.path.join(individuals_path, individual)

        # Load individual information
        data = read_json(os.path.join(current_path, "general_info.json"))
        #with open(os.path.join(current_path, "general_info.json"), "r") as f:
        #    data = json.load(f)
        #    f.close()
        
        phenotype = data["phenotype"]

        syntax_tree = parse_expression(phenotype)

        graph = make_graphviz_tree(syntax_tree)

        render_tree(graph, current_path, individual, expr=phenotype)
    
    # Make a file to avoid re-runs
    with open(os.path.join(individuals_path, "all_ready_trees.json"), "w") as f:
        f.close()
        