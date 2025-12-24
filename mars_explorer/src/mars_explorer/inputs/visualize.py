import networkx as nx
import matplotlib.pyplot as plt

# 1. Load the graph data
G = nx.read_graphml("inputs/graph_v1.graphml")

# 2. Define a color map for the different terrains
terrain_colors = {
    'rocky': '#8B4513',   # Brown
    'crater': '#DC143C',  # Red
    'sandy': '#DAA520',   # Gold/Yellow
    'plain': '#90EE90',   # Light Green
    'icy': '#ADD8E6'      # Light Blue
}

# 3. Generate a layout (positioning) for the nodes
# 'seed' ensures the layout is reproducible
pos = nx.spring_layout(G, seed=24)

plt.figure(figsize=(12, 10))

# 4. Draw the edges first (background)
nx.draw_networkx_edges(G, pos, alpha=0.3, edge_color='gray')

# 5. Draw nodes for each terrain type separately
for terrain, color in terrain_colors.items():
    # Find all nodes that belong to this terrain
    nodelist = [n for n, d in G.nodes(data=True) if d.get('terrain') == terrain]
    
    # Draw these nodes
    nx.draw_networkx_nodes(
        G, pos,
        nodelist=nodelist,
        node_color=color,
        node_size=300,
        label=terrain,  # Label for the legend
        alpha=0.9
    )

# 6. Add title and legend
plt.title("Mars Terrain Graph Visualization")
plt.legend(title="Terrain Type", scatterpoints=1)
plt.axis('off')

# Save and show
plt.savefig("mars_terrain_visualization.png")
plt.show()