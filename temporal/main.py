
import json
import networkx as nx
from graphviz import Digraph
import matplotlib.pyplot as plt

from params import Params, set_params
from tree import Tree

GRAMMAR = {
    '<exp>': ['(<exp> <op> <exp>)', '<binary_func>(<expr>,<expr>)', '<unary_func>(<expr>)', '<var>'],
    '<op>': ['+', '-'],
    '<binary_func>': ['convolution', 'one_point', 'masked_cross'],
    '<unary_func>': ['sin', 'cos'],
    '<var>': ['x', 'y']
}

class Node:
    def __init__(self, value):
        self.value = value
        self.children = []

    def __repr__(self):
        return f"{self.value}({', '.join(map(str, self.children))})"

def search_operators(expression, grammar):
    level = 1
    indices = []
    for i, char in enumerate(expression):
        if char == "(":
            level += 1
        elif char == ")":
            level -= 1
        
        elif level == 1 and char in grammar["<op>"]:
            indices.append(i)
    
    return indices

def search_closure(expression):
    level = 1
    for i, char in enumerate(expression):
        if char == "(":
            level += 1
        
        elif char == ")":
            level -= 1

        elif level == 0:
            # We have reached the closure
            return i

def parse_expression(expression, grammar=GRAMMAR):
    expression = expression.replace(' ', '')

    if expression in grammar['<var>']:
        return Node(expression)
    
    # Search operators that are outside parenthesis
    indices = search_operators(expression, grammar)

    if indices:
        element = indices[0]
        node = Node(expression[element])

        # Split expression in left and right
        left = expression[:element]
        right = expression[element+1:]
        left_child = parse_expression(left, grammar)
        right_child = parse_expression(right, grammar)

        node.children.extend([left_child, right_child])
        return node
    
    for func in grammar['<binary_func>']:
        if expression.startswith(func + '(') and expression.endswith(')'):
            node = Node(func)
            inner_expr = expression[len(func) + 1:-1]
            
            inner_exprs = split_args(inner_expr)
            for expr in inner_exprs:
                child = parse_expression(expr, grammar)
                node.children.append(child)
            
            return node

    for func in grammar['<unary_func>']:
        if expression.startswith(func + '(') and expression.endswith(')'):
            node = Node(func)
            inner_expr = expression[len(func) + 1:-1]
            child = parse_expression(inner_expr, grammar)
            node.children.append(child)
            return node

    if expression.startswith('(') and expression.endswith(')'):
        expression = expression[1:-1]
        return parse_expression(expression)

    raise ValueError(f"Invalid expression: {expression}")

def split_args(expression):
    level = 0
    args = []
    start = 0
    for i, char in enumerate(expression):
        if char == '(':
            level += 1
        elif char == ')':
            level -= 1
        elif char == ',' and level == 0:
            args.append(expression[start:i])
            start = i + 1
    args.append(expression[start:])
    return args

def add_nodes_edges(graph, node, parent=None):
    graph.add_node(id(node), label=node.value)
    if parent:
        graph.add_edge(id(parent), id(node))
    for child in node.children:
        add_nodes_edges(graph, child, node)


def visualize_tree(syntax_tree, expression, gen, indx):
    def add_nodes_edges(graph, node, parent=None):
        graph.node(str(id(node)), label=node.value)
        if parent:
            graph.edge(str(id(parent)), str(id(node)))
        for child in node.children:
            add_nodes_edges(graph, child, node)
    
    graph = Digraph()
    add_nodes_edges(graph, syntax_tree)

    graph.render(f"Tree_{indx}.gv", format="png")


def visualize_syntax_tree(syntax_tree, expression, gen):
    def add_nodes_edges(graph, node, parent=None):
        graph.add_node(id(node), label=node.value)
        if parent:
            graph.add_edge(id(parent), id(node))
        for child in node.children:
            add_nodes_edges(graph, child, node)

    graph = nx.DiGraph()
    add_nodes_edges(graph, syntax_tree)

    # Set positions for tree nodes
    pos = nx.nx_agraph.graphviz_layout(graph, prog='dot')

    # Draw the tree
    dpi = 400
    #plt.subplots(1,1,figsize=(500/dpi, 700/dpi), dpi=dpi)
    fig = plt.figure(figsize=(5, 7), dpi=dpi)
    nx.draw(graph, pos, labels=nx.get_node_attributes(graph, 'label'),
            with_labels=True, node_size=1000, node_color='skyblue',
            font_size=10, font_color='black', font_weight='bold',
            edge_color='gray', arrows=True, arrowsize=20)
    ax = plt.gca()
    plt.text(0.01,0.99,expression, ha='left', va='top',fontdict={"fontsize":8, "weight":'bold'}, transform=ax.transAxes)
    plt.text(0.01,0.95,f"Generation {gen}", ha='left', va='top',fontdict={"fontsize":8, "weight":'bold'}, transform=ax.transAxes)
    #fig.savefig("Test.jpg")
    
    return fig

def extract_expression(file:str, directory:str):
    file_path = directory + "/" + file

    with open(file_path, "r") as f:
        data = f.read()
        f.close()

    expression = data.splitlines()[0].strip()

    return expression




if __name__ == "__main__":

    set_params()

    params = Params()

    from create_tree_figures import genome_to_tree_map

    start_expr = str(params["BNF_GRAMMAR"].start_rule["symbol"])
    non_terminals = params["BNF_GRAMMAR"].non_terminals

    # Load a certain generation
    generation = 0
    generation_path = "results/DESKTOP-E3F66CS_2024_8_26_2217_148643/generations/"
    population_path = generation_path + f"generation_{generation:04d}/population.json"
    with open(population_path, "r") as f:
        data = json.load(f)
        f.close()
    
    # Load genomes
    genomes = []
    phenotypes_to_verify = []

    individuals_path = "results/DESKTOP-E3F66CS_2024_8_26_2217_148643/individuals/"
    for individual in data:
        ind_path = individuals_path + str(individual)
        general_info_path = ind_path + "/" + "general_info.json"

        with open(general_info_path, "r") as f:
            ind_data = json.load(f)
            f.close()
        
        genomes.append(ind_data["genome"])
        phenotypes_to_verify.append(ind_data["phenotype"])
        
    # Map genomes to trees.
    for i, genome in enumerate(genomes):
        
        # Instantiate a tree
        tree = Tree(start_expr, None)

        # Build Tree
        output, used_codons, nodes, depth, max_depth, invalid = \
            genome_to_tree_map(tree, genome, [], 0, 0, 0, 0)
        
        # Get information
        effective_genome, output, _, tree_depth, num_nodes = tree.get_tree_info(non_terminals, [], [])

        phenotype = "".join(output)

        individual_tree = parse_expression(phenotype)

        visualize_tree(individual_tree, phenotype, 0, i)

        #visualize_syntax_tree(individual_tree, phenotype, 0)
        
        print(phenotype, " || ", phenotypes_to_verify[i])
