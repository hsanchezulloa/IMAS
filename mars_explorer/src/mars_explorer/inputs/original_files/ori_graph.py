import networkx as nx
import matplotlib.pyplot as plt

# Load the GraphML file
G = nx.read_graphml("inputs/ori_mars_terrain.graphml")

# Draw the graph
plt.figure(figsize=(10, 8))
pos = nx.spring_layout(G)
nx.draw(G, pos, with_labels=True, node_size=50, font_size=8)
plt.title("Mars Terrain Graph")
plt.show()

def compute_shortest_distance(graph, source, target, weight='length'):
    distance = nx.dijkstra_path_length(graph, source, target, weight=weight)
    path = nx.dijkstra_path(graph, source, target, weight=weight)
    
    return distance, path

terrain_multipliers = {
    "plain": 1.0,
    "rocky": 1.3,
    "sandy": 1.6,
    "icy": 2.0,
    "crater": 2.5
}

def terrain_weight(s, t, data):
    terrain_s = G.nodes[s].get("terrain", "plain")
    terrain_t = G.nodes[t].get("terrain", "plain")
    base_weight = 10
    multiplier = (terrain_multipliers.get(terrain_s, 1.0) + terrain_multipliers.get(terrain_t, 1.0)) / 2

    return base_weight * multiplier

source_node = 'N1'
target_node = 'N90'
distance, path = compute_shortest_distance(G, source_node, target_node, terrain_weight)

print(f'Distance {source_node} -> {target_node}: {distance}')
print(f'Path {source_node} -> {target_node}: {path}')