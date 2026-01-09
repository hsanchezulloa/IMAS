from typing import List, Dict, Any, Optional, Set
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
import networkx as nx
from tools.mars_environment import MarsEnvironment
import random
import itertools
import json

class MultiRoverRouteInput(BaseModel):
    rovers: List[Dict[str, Any]] = Field(description="List of rovers with keys: id, location, energy")
    target_nodes: List[str] = Field(description="List of target node IDs")
    hazards: bool = Field(..., description="Indicates whether hazardous zones must be avoided")

class RoverPathfindingTool(BaseTool):
    name: str = "Multi_Rover_Route_Calculator"
    description: str = (
        "Deterministic rover planner. "
        "Computes feasible routes, assigns target nodes, "
        "and returns final round-trip paths. "
        "Returns ONLY a JSON dictionary."
    )
    args_schema: type[BaseModel] = MultiRoverRouteInput

    def _run(self, rovers: List[Dict], target_nodes: List[str], hazards) -> Dict[str, Any]:
        env = MarsEnvironment()
        graph = env.get_graph()
        results = {}

        # hazards = random.random() >= 0.5
        MAX_CANDIDATE_PATHS = 10


        # Weight function (time-based)
        def weight_function(u, v, d):
            node_data = graph.nodes[v]
            temperature = float(d.get("temperature", -50))

            if (node_data.get("unstable", False) or node_data.get("high_radiation", False)) and hazards:
                return float("inf")
            if temperature < -80:
                return float("inf")

            distance = float(d.get("length"))
            terrain = node_data.get("terrain", "").lower()

            multiplier = {"rocky": 1.1,"sandy": 1.3,"crater": 1.4,"icy": 2.0}.get(terrain, 1.0)

            cost = distance * multiplier
            if temperature < -60:
                cost += 20

            return cost


        # Energy + distance computation
        def compute_energy_and_distance(path):
            total_distance = 0.0
            total_energy = 0.0

            for i in range(len(path) - 1):
                u, v = path[i], path[i + 1]
                edge_data = graph[u][v]
                distance = float(edge_data.get("length", 0))
                total_distance += distance

                terrain = graph.nodes[v].get("terrain", "").lower()
                energy_factor = {"rocky": 1.05,"sandy": 1.10,"crater": 1.15,"icy": 1.20}.get(terrain, 1.0)

                total_energy += distance * energy_factor

            return total_distance, total_energy

        # Main loop
        for rover in rovers:
            rover_id = rover.get("id")
            start_node = rover.get("location")
            current_energy = rover.get("energy")

            rover_result = {
                "location": start_node,
                "energy": current_energy,
                "output_nodes": {}
            }

            if start_node not in graph:
                results[rover_id] = rover_result
                continue

            for target in target_nodes:
                node_result = {
                    "distance": None,
                    "energy": None,
                    "feasible": False,
                    "warning": "NO PATH",
                }

                if target not in graph:
                    rover_result["output_nodes"][target] = node_result
                    continue

                try:
                    go_paths = itertools.islice(nx.shortest_simple_paths(graph, start_node, target, weight=weight_function),MAX_CANDIDATE_PATHS)
                    feasible_found = False
                    for path_go in go_paths:
                        try:
                            path_back = nx.shortest_path(graph, target, start_node, weight=weight_function)
                        except nx.NetworkXNoPath:
                            continue

                        full_path = path_go + path_back[1:]
                        total_distance, total_energy = compute_energy_and_distance(full_path)

                        if total_energy <= current_energy:
                            remaining = current_energy - total_energy
                            min_reserve = 100 * 0.30

                            warning = "BATTERY OK"
                            if remaining < min_reserve:
                                warning = f"WARNING: Low battery remaining ({remaining:.2f})"
                            node_result = {
                                "distance": round(total_distance, 2),
                                "energy": round(remaining, 2),
                                "feasible": True,
                                "warning": warning,
                            }
                            feasible_found = True
                            break

                    if not feasible_found:
                        node_result["warning"] = "NO FEASIBLE PATH (BATTERY)"

                except nx.NetworkXNoPath:
                    node_result["warning"] = "NO PATH"
                except Exception as e:
                    node_result["warning"] = f"ERROR: {str(e)}"

                rover_result["output_nodes"][target] = node_result

            results[rover_id] = rover_result
        
        
        with open(f"possible_paths_rovers.json", "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)

        # NODE ASSIGNMENT
        enforce_min_one_per_rover=True
        # List of rover IDs
        rovers_id = list(results.keys())

        # Store only feasible paths
        feasible = {}
        all_nodes = set()

        for rover, data in results.items():
            for node, info in data.get("output_nodes", {}).items():
                if info.get("feasible"):
                    feasible.setdefault(rover, {})[node] = info
                    all_nodes.add(node)

        assignments = {rover: [] for rover in rovers_id}
        used_nodes = set()

        def weight_function(u, v, d):
            node_data = graph.nodes[v]
            distance = float(d.get("length", 0))
            terrain = node_data.get("terrain", "").lower()
            multiplier = {
                "rocky": 1.1,
                "sandy": 1.3,
                "crater": 1.4,
                "icy": 2.0,
            }.get(terrain, 1.0)

            return distance * multiplier

        # choose best rover for node
        def best_rover_for_node(node):
            candidates = []
            for rover, nodes in feasible.items():
                if node in nodes:
                    info = nodes[node]
                    candidates.append((rover, info["distance"], info["energy"]))
            if not candidates:
                return None
            # shortest distance, then highest energy
            return min(candidates, key=lambda x: (x[1], -x[2]))[0]


        # ensure each rover gets ≥1 node
        if enforce_min_one_per_rover:
            for rover in rovers_id:
                if rover not in feasible:
                    continue
                candidates = [(node,float(info["distance"]),float(info["energy"])) for node, info in feasible[rover].items() if node not in used_nodes]
                if not candidates:
                    continue
                best_node = min(candidates, key=lambda x: (x[1], -x[2]))[0]
                assignments[rover].append(best_node)
                used_nodes.add(best_node)


        # assign remaining nodes
        for node in sorted(all_nodes):
            if node in used_nodes:
                continue
            rover = best_rover_for_node(node)
            if rover:
                # assignments[rover].append(node)
                assignments[rover].append(node)
                used_nodes.add(node)
                
        final_paths = {}

        for rover, nodes in assignments.items():
            start = results[rover]["location"]
            final_paths[rover] = []

            for target in nodes:
                try:
                    path_go = nx.shortest_path(graph, start, target, weight=weight_function)
                    path_back = nx.shortest_path(graph, target, start, weight=weight_function)
                    full_path = path_go + path_back[1:]
                    final_paths[rover].append(full_path)
                except nx.NetworkXNoPath:
                    continue

        return final_paths



    




