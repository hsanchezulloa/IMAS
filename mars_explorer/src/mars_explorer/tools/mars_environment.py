import networkx as nx
import os

# Load the input graph describing the Mars Environment
class MarsEnvironment:
    _instance = None
    _graph = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MarsEnvironment, cls).__new__(cls)
            cls._load_graph()
        return cls._instance

    @classmethod
    def _load_graph(cls):
        try:
            base_dir = os.path.dirname(__file__)
            graph_path = os.path.join(base_dir, "..", "inputs", "mars_terrain_graph.graphml")
            graph_path = os.path.abspath(graph_path)
            cls._graph = nx.read_graphml(graph_path)
        except Exception as e:
            raise ValueError(f'Graph could not be loaded: {e}')
    
    def get_graph(self):
        return self._graph

    def get_node_data(self, node_id):
        if node_id in self._graph.nodes:
            return self._graph.nodes[node_id]
        return {}
