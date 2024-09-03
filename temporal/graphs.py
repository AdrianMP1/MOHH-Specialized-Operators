import networkx as nx
import matplotlib.pyplot as plt


from graphviz import Digraph


if __name__ == "__main__":

    dot = [Digraph()]

    dot[0].attr(kw="graph", label="Test")
    count = [0]
    dot[0].node('1', "Sin")

    dot[0].node('3', 'Sin')
    dot[0].edge('1', '3')

    dot[0].node('5', 'y')
    dot[0].edge('3', '5')

    dot[0].view()
    dot[0].render("Test.gv", format="png", )

    """

    G = nx.Graph()

    G.add_node("Sin")
    G.add_node("(")
    G.add_node("y")
    G.add_node(")")

    G.add_edge("Sin", "(")
    G.add_edge("Sin", "y")
    G.add_edge("Sin", ")")

    nx.draw(G, with_labels=True, font_weight='bold')
    plt.show()
    
    """