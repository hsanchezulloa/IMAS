from typing import List
from crewai.tools import BaseTool
from pydantic import BaseModel, Field, PrivateAttr
import networkx as nx
from tools.mars_environment import MarsEnvironment
import random

class RoverRouteInput(BaseModel):
    start_node: str = Field("Base", description="Starting Base Station.")
    start_node: str = Field(..., description  = "Starting node ID.")
    target_node: str = Field(..., description = "Target node ID (e.g., 'N70').")
    current_energy: float = Field(..., description = "Current battery level.")

class RoverPathfindingTool(BaseTool):
    name: str = "Rover_Route_Calculator"
    description: str = (
        "Calculates the optimal round path for a rover based on real graph distances. "
        "Considers terrain penalties (icy terrain is slower). "
        "Strictly avoid 'unstable' terrain and 'high_radiation' zones. "
        "Saves the path list, total distance estimate, energy cost, remaining battery, battery status."
    )
    args_schema: type[BaseModel] = RoverRouteInput

    def _run(self, start_node: str, target_node: str, current_energy: float) -> str:
        '''
        Example of output:
        (path, distance, energy, batery_status) -> (['N60', 'N65', 'N66'], 9.0, 9.45, 'BATERY OK')
        '''
        env = MarsEnvironment()
        graph = env.get_graph()

        print(f"route_planner (inside RoverPathfindingTool): target_node = {target_node}")

        # Ensure that the start node exists
        if start_node not in graph or target_node not in graph:
            return f"Error: Nodes {start_node} or {target_node} do not exist in the map."

        # Determine if hazards are considered or not (50% probability each)
        hazards = random.random() >= 0.5

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
            # from base to target node
            path_go = nx.shortest_path(graph, source = start_node, target = target_node, weight = weight_function)
            # from target node to base
            path_back = nx.shortest_path(graph, source = target_node, target = start_node, weight = weight_function)  
            # full path
            path = path_go + path_back[1:]

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
                warning_msg = (f"WARNING: This route leaves battery at {remaining_battery:.2f}. Consider using another rover!")

            return path, total_distance, total_energy, warning_msg

        except nx.NetworkXNoPath:
            return "No path found"
        except Exception as e:
            return f"Error calculating route: {str(e)}"