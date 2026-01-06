import networkx as nx
import matplotlib.pyplot as plt

G = nx.read_graphml("inputs/graph_v1.graphml")

terrain_colors = {
    'rocky': '#8B4513', 
    'crater': '#DC143C',
    'sandy': '#DAA520', 
    'plain': '#90EE90', 
    'icy': '#ADD8E6'    
}

pos = nx.spring_layout(G, seed=24)
plt.figure(figsize=(12, 10))
nx.draw_networkx_edges(G, pos, alpha=0.3, edge_color='gray')

for terrain, color in terrain_colors.items():
    nodelist = [n for n, d in G.nodes(data=True) if d.get('terrain') == terrain]
    nx.draw_networkx_nodes(G, pos, nodelist=nodelist, node_color=color, node_size=300, label=terrain, alpha=0.9)

plt.title("Mars Terrain Graph Visualization")
plt.legend(title="Terrain Type", scatterpoints=1)
plt.axis('off')
plt.savefig("mars_terrain_visualization.png")
plt.show()