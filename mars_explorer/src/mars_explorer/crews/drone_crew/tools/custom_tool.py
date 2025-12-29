from crewai.tools import BaseTool
from pydantic import BaseModel, Field
import networkx as nx
from tools.mars_environment import MarsEnvironment

class DroneFlightInput(BaseModel):
    start_node: str = Field(..., description="Takeoff node ID (Base Station).")
    target_nodes: list[str] = Field(..., description="List of node IDs to visit.")

class DroneFlightCheckTool(BaseTool):
    name: str = "Drone_Flight_Feasibility"
    description: str = (
        "Considers that the trip must be less than 25 minutes."
        "Disable the flight if there are dust storms active or wind exceeds 40 km/h. "
        "Energy consumption increases by 15 percent if wind exceeds 30 km/h. "
        "Returns valid route, total time, and energy cost.")
    args_schema: type[BaseModel] = DroneFlightInput 


    def _run(self, start_node: str, current_energy: float, target_nodes: list[str], hazards: bool) -> str:
        '''
        Example of output:
        (path, total_distance, total_energy, remaining_battery, energy_msg) -> (['N60', 'N62', 'N63', 'N60'], 9.0, 0.225, 99.775, 'BATERY OK')
        '''

        env = MarsEnvironment()
        graph = env.get_graph()

        # PATH: Base -> Targets -> Base (Round Trip)
        full_stops = [start_node] + target_nodes + [start_node]
        
        total_distance = 0.0
        max_wind = 0.0
        
        # Assumption
        DRONE_SPEED = 40

        path = []
        for i in range(len(full_stops) - 1):
            u, v = full_stops[i], full_stops[i+1]
            
            if u not in graph or v not in graph:
                return f"Error: Nodes {u} or {v} do not exist in the map."

            try:
                # SHORTEST PATH (according to the shortest length)
                segment_path = nx.shortest_path(graph, source=u, target=v, weight='length')
                
                # HAZARDS
                for node in segment_path:
                    node_data = graph.nodes[node]
                    
                    # Storm
                    if node_data.get('dust_storms', False) and hazards:
                        return f"ABORT: Active dust storm detected at {node}."
                    
                    # Wind
                    wind = float(node_data.get('wind', 0.0))
                    if wind > max_wind:
                        max_wind = wind
        
                    if wind > 40.0:
                        return f"ABORT: High wind ({wind} km/h) at {node} exceeds limit (40 km/h)."
                
                # Calculate distance of the segment
                for k in range(len(segment_path)-1):
                    p1, p2 = segment_path[k], segment_path[k+1]
                    total_distance += float(graph[p1][p2].get('length'))
                
                if i == 0:
                    path.extend(segment_path)
                else:
                    path.extend(segment_path[1:])

            except nx.NetworkXNoPath:
                return "No path found"

        # Time calculation
        total_time = total_distance / DRONE_SPEED
        
        # Energy Consumption 
        total_energy = total_time # (1 unit per minute assumed)
        remaining_battery = current_energy - total_energy
        energy_msg = "BATERY OK"

        if total_energy > current_energy:
            return (f'Route requires {total_energy:.2f} energy, but rover only has {current_energy}.')
        
        if remaining_battery < 30:
            energy_msg = (f"WARNING: This route leaves battery at {remaining_battery:.2f}. Plan a shorter route!")
        
        # Increase energy consumption by 15% if wind is higher than 30 km/h
        if max_wind > 30.0:
            total_energy = total_time * 1.15
            energy_msg = f"Increased (+15% due to wind {max_wind}km/h)"

        # Return to base after 25 minutes of flight."
        if total_time > 25.0:
            return (f"INFEASIBLE: Total flight time {total_time:.2f} min exceeds 25 min limit. ")
    
        return path, total_distance, total_energy, remaining_battery, energy_msg
