import networkx as nx
import matplotlib.pyplot as plt

if __name__ == "__main__":

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
    
