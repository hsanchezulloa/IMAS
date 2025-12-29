from crewai.tools import BaseTool
from pydantic import BaseModel, Field
import networkx as nx
from tools.mars_environment import MarsEnvironment

class RoverRouteInput(BaseModel):
    start_node: str = Field(..., description  = "Starting node ID.")
    end_node: str = Field(..., description = "Target node ID.")
    current_energy: float = Field(..., description = "Current battery level.")
    hazards: bool = Field(..., description = "Take hazards into account.")

class RoverPathfindingTool(BaseTool):
    name: str = "Rover_Route_Calculator"
    description: str = (
        "Calculates the optimal path for a rover based on real graph distances. "
        "Considers terrain penalties (icy terrain is slower). "
        "Strictly avoid 'unstable' terrain and 'high_radiation' zones. "
        "Returns the path list, total distance estimate, energy cost, remaining battery, battery status."
    )
    args_schema: type[BaseModel] = RoverRouteInput


    def _run(self, start_node: str, end_node: str, current_energy: float, hazards: bool) -> str:
        '''
        Example of output:
        (path, distance, energy, remaining_battery, batery_status) -> (['N60', 'N65', 'N66'], 9.0, 9.45, 70.55, 'BATERY OK')
        '''
        env = MarsEnvironment()
        graph = env.get_graph()

        # Ensure that the start node exists
        if start_node not in graph or end_node not in graph:
            return f"Error: Nodes {start_node} or {end_node} do not exist in the map."


        def weight_function(u, v, d):
            '''
            Weight function to find the path
            Determines the cost of moving from u to v
            - u: source node
            - v: target node
            - d: edge data (dictionary with the attributes of the edge between u and v)
            '''
            node_data = graph.nodes[v]
            
            # HAZARD CHECK: avoid dangerous nodes
            temperature = float(d.get('temperature', -50))
            if (node_data.get('unstable', False) or node_data.get('high_radiation', False)) and hazards:
                return float('inf')
            if temperature < -80:
                return float('inf')
            # TERRAIN MODIFIERS
            # Get real distance (edge length) and the terrain
            distance = float(d.get('length'))
            terrain = node_data.get('terrain').lower()
            
            # Incremented cost
            time_cost = 0
            if terrain == 'rocky':
                time_cost = distance * 1.1 # 10% increment
            elif terrain == 'sandy':
                time_cost = distance * 1.3
            elif terrain == 'crater':
                time_cost = distance * 1.4
            elif terrain == 'icy':
                time_cost = distance * 2
            
            # Rovers must enter a heat shelter during 20min if the surface temperature is below -60C
            if temperature < -60: 
                # Time increased by 20 minutes
                time_cost += 20

            return time_cost
        

        try:
            # SHORTEST PATH
            path = nx.shortest_path(graph, source = start_node, target = end_node, weight = weight_function)

            # COMPUTE TOTAL DISTANCE AND ENERGY OF THE SHORT
            total_distance = 0.0
            total_energy = 0.0
            
            # Iterate over the shortest path
            for i in range(len(path) - 1):
                u, v = path[i], path[i+1]
                
                # Distance
                edge_data = graph[u][v]
                distance = float(edge_data.get('length'))
                total_distance += distance
                
                # Energy
                terrain = graph.nodes[v].get('terrain').lower()
                if terrain == 'rocky':
                    total_energy += distance * 1.05
                elif terrain == 'sandy':
                    total_energy += distance * 1.1
                elif terrain == 'crater':
                    total_energy += distance * 1.15
                elif terrain == 'icy':
                    total_energy += distance * 1.2

            # Battery check
            if total_energy > current_energy:
                return (f'Route requires {total_energy:.2f} energy, but rover only has {current_energy}.')

            remaining_battery = current_energy - total_energy
            min_reserve = 100 * 0.30  # 30% of the total capacity
            
            warning_msg = "BATERY OK"
            if remaining_battery < min_reserve:
                # Return a string that the LLM will interpret as an alter
                warning_msg = (f"WARNING: This route leaves battery at {remaining_battery:.2f}. Plan a route to a Base Station first!")

            return path, total_distance, total_energy, remaining_battery, warning_msg

        except nx.NetworkXNoPath:
            return "No path found"
        except Exception as e:
            return f"Error calculating route: {str(e)}"