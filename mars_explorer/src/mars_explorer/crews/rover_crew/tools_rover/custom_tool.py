import json
import random
import networkx as nx
from typing import List, Dict, Any
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from tools.mars_environment import MarsEnvironment 

class BatchRouteInput(BaseModel):
    targets_list: str = Field(..., description="JSON string list of target nodes (e.g. \"['N70', 'N102']\")")
    rovers_data: str = Field(..., description="JSON string of rovers list (e.g. \"[{'id':'rover_0', 'location':'N30', 'energy': 100}]\")")

class BatchRoverRouteTool(BaseTool):
    name: str = "Batch_Route_Calculator"
    description: str = (
        "Calculates FULL routes for multiple targets in one go. "
        "Input: targets list and rovers list. "
        "Logic: Assigns the closest rover by Node ID number. If tie, selects random. "
        "Output: Final JSON string with assigned routes."
    )
    args_schema: type[BaseModel] = BatchRouteInput

    def _run(self, targets_list: str, rovers_data: str) -> str:
        # 1. PARSE INPUTS
        try:
            # Fix common LLM quote issues
            targets = json.loads(targets_list.replace("'", '"'))
            rovers = json.loads(rovers_data.replace("'", '"'))
            
            # Ensure rovers is a list of dicts
            if isinstance(rovers, dict):
                rovers = [{"id": k, **v} for k, v in rovers.items()]
                
        except Exception as e:
            return f"Error parsing JSON inputs: {str(e)}"

        env = MarsEnvironment()
        graph = env.get_graph()
        
        final_output = {}
        
        # Helper: Extract number from "N30" -> 30
        def get_node_number(node_str):
            try:
                return int(str(node_str).upper().replace("N", ""))
            except:
                return 99999

        # 2. ITERATE OVER TARGETS
        for target_node in targets:
            target_num = get_node_number(target_node)
            rover_candidates = []
            
            # Calculate distance for all valid rovers
            for rover in rovers:
                rover_loc = rover.get('location', 'N0')
                # Safety check: does rover have enough energy
                if float(rover.get('energy', 0)) < 30.0:
                    continue
                    
                rover_num = get_node_number(rover_loc)
                diff = abs(target_num - rover_num)
                rover_candidates.append({'rover': rover, 'diff': diff})
            
            # Fallback if all rovers are dead
            if not rover_candidates:
                # Use the first one even if low battery, just to produce a path
                best_rover = rovers[0]
            else:
                # Sort by difference (closest first)
                rover_candidates.sort(key=lambda x: x['diff'])
                # Find minimum difference
                min_diff = rover_candidates[0]['diff']
                # Filter all rovers that share the minimum difference (Ties)
                best_ties = [item['rover'] for item in rover_candidates if item['diff'] == min_diff]
                # Random selection among ties
                best_rover = random.choice(best_ties)

            rover_id = best_rover['id']
            start_node = best_rover['location']
            current_energy = float(best_rover.get('energy', 100.0))

            if start_node not in graph or target_node not in graph:
                # Log error in output but continue
                if rover_id not in final_output: final_output[rover_id] = []
                final_output[rover_id].append([f"ERROR: Node {target_node} not in graph"])
                continue

            # Hazards determination (50% chance)
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

            # CALCULATE PATH
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

                # ENERGY CHECK
                if total_energy > current_energy:
                    print(f"SKIPPING TARGET {target_node} for {rover_id}: Needs {total_energy:.2f} energy, has {current_energy:.2f}.")
                    continue
                
                remaining_battery = current_energy - total_energy
                min_reserve = 100 * 0.30  # 30% of the total capacity
                
                warning_msg = "BATERY OK"
                if remaining_battery < min_reserve:
                    # Return a string that the LLM will interpret as an alter
                    warning_msg = (f"WARNING: This route leaves battery at {remaining_battery:.2f}. Consider using another rover!")
                print(warning_msg)

                # SAVE RESULT
                if rover_id not in final_output:
                    final_output[rover_id] = []
                
                final_output[rover_id].append(path)

            except nx.NetworkXNoPath:
                if rover_id not in final_output: final_output[rover_id] = []
                final_output[rover_id].append(["NO_PATH_FOUND"])
            except Exception as e:
                if rover_id not in final_output: final_output[rover_id] = []
                final_output[rover_id].append([f"ERROR: {str(e)}"])
    
        # 3. RETURN FINAL JSON
        return json.dumps(final_output)