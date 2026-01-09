import json
import random
import networkx as nx
from typing import List, Dict, Any
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from tools.mars_environment import MarsEnvironment 

class BatchDroneInput(BaseModel):
    targets_list: str = Field(..., description="JSON string list of target nodes (e.g. \"['N33', 'N59']\")")
    drones_data: str = Field(..., description="JSON string of drones list (e.g. \"[{'id':'drone_0', 'location':'N30', 'energy': 100}]\")")
    hazards: bool = Field(..., description="Indicates whether hazardous zones must be avoided")

class BatchDroneFlightTool(BaseTool):
    name: str = "Batch_Flight_Calculator"
    description: str = (
        "Calculates ROUND TRIP flights for multiple targets in one go. "
        "Logic: Assigns closest drone. Checks constraints (Time < 25min, Wind < 40km/h, No Storms). "
        "Updates battery dynamically. "
        "Output: Final JSON string with valid flights."
    )
    args_schema: type[BaseModel] = BatchDroneInput

    def _run(self, targets_list: list, drones_data: str, hazards) -> str:
        # PARSE INPUTS
        try:
            targets = json.loads(targets_list.replace("'", '"'))
            drones = json.loads(drones_data.replace("'", '"'))
            
            targets = list(dict.fromkeys(targets))
            if isinstance(drones, dict):
                drones = [{"id": k, **v} for k, v in drones.items()]
                
        except Exception as e:
            return f"Error parsing JSON inputs: {str(e)}"

        env = MarsEnvironment()
        graph = env.get_graph()
        
        final_output = {}
        DRONE_SPEED = 40.0 # Assumed speed unit
        
        # Helper: Extract number from "N30" -> 30
        def get_node_number(node_str):
            try:
                return int(str(node_str).upper().replace("N", ""))
            except:
                return 99999

        # ITERATE OVER TARGETS
        for target_node in targets:
            target_num = get_node_number(target_node)
            drone_candidates = []
            
            # Calculate distance for all valid drones
            for drone in drones:
                drone_loc = drone.get('location', 'N0')
                if float(drone.get('battery', 0)) < 30.0:
                    continue
                
                drone_num = get_node_number(drone_loc)
                diff = abs(target_num - drone_num)
                drone_candidates.append({'drone': drone, 'diff': diff})
            
            # Fallback if all drones are dead
            if not drone_candidates:
                best_drone = drones[0]
            else:
                # Sort closest + Random tie-break
                drone_candidates.sort(key=lambda x: x['diff'])
                min_diff = drone_candidates[0]['diff']
                best_ties = [item['drone'] for item in drone_candidates if item['diff'] == min_diff]
                best_drone = random.choice(best_ties)

            drone_id = best_drone['id']
            start_node = best_drone['location']
            current_energy = float(best_drone.get('energy', 100.0))

            if start_node not in graph or target_node not in graph:
                print(f"SKIPPING {target_node}: Node not in graph.")
                continue

            # HAZARD (50% Chance)
            # hazards = random.random() >= 0.5

            # FLIGHT CALCULATION
            # Trip: Start -> Target -> Start
            full_stops = [start_node, target_node, start_node]
            
            path = []
            total_distance = 0.0
            max_wind = 0.0
            abort_flight = False
            abort_reason = ""

            try:
                for i in range(len(full_stops) - 1):
                    u, v = full_stops[i], full_stops[i+1]
                    
                    # Shortest path segment
                    segment_path = nx.shortest_path(graph, source=u, target=v, weight='length')
                    
                    # Check Hazards on segment
                    for node in segment_path:
                        node_data = graph.nodes[node]
                        
                        # Storm Check
                        if node_data.get('dust_storms', False) and hazards:
                            abort_reason = f"Storm at {node}"
                            continue
                        
                        # Wind Check
                        wind = float(node_data.get('wind', 0.0))
                        if wind > max_wind: 
                            max_wind = wind
                        
                        if wind > 40.0:
                            abort_reason = f"Wind {wind}km/h at {node}"
                            continue
                    
                    # Distance Calculation
                    for k in range(len(segment_path)-1):
                        p1, p2 = segment_path[k], segment_path[k+1]
                        total_distance += float(graph[p1][p2].get('length', 1.0))

                    # Construct Path list
                    if i == 0:
                        path.extend(segment_path)
                    else:
                        path.extend(segment_path[1:]) # Avoid duplicating middle node

            except nx.NetworkXNoPath:
                print(f"SKIPPING {target_node}: No path found.")
                continue
            
            if abort_flight:
                print(f"SKIPPING {target_node} ({drone_id}): {abort_reason}")
                continue

            # ENERGY
            total_time = total_distance / DRONE_SPEED
            total_energy = total_time # Base cost

            # Constraint: wind > 30 adds 15% cost
            if max_wind > 30.0:
                total_energy = total_time * 1.15
            
            # Constraint: time Limit
            if total_time > 25.0:
                print(f"SKIPPING {target_node}: Time {total_time:.2f} > 25 min limit.")
                continue

            # Constraint: battery Check
            if total_energy > current_energy:
                print(f"SKIPPING {target_node}: Need {total_energy:.2f} energy, has {current_energy:.2f}.")
                continue

            # Update
            best_drone['energy'] = current_energy - total_energy
            
            if drone_id not in final_output:
                final_output[drone_id] = []
            
            # final_output[drone_id].append(path)
            final_output[drone_id].append(path)

        return json.dumps(final_output)