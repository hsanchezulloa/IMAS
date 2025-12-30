
from typing import Type, Dict, Any
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
import re
import requests
from bs4 import BeautifulSoup
from pathlib import Path

def parse_priorities(text: str) -> dict:
    priorities = {"high": [],"medium": [],"low": []}
    current = None
    for line in text.splitlines():
        line = line.strip()
        # Detect priority headers
        if re.match(r"\d+\.\s*\*\*High Priority\*\*", line):
            current = "high"
            continue
        if re.match(r"\d+\.\s*\*\*Medium Priority\*\*", line):
            current = "medium"
            continue
        if re.match(r"\d+\.\s*\*\*Low Priority\*\*", line):
            current = "low"
            continue
        # Capture bullet points
        if current and line.startswith("-"):
            priorities[current].append(line.lstrip("- ").strip())

    return priorities

def parse_list_section(text: str) -> list[str]:
    items = []
    for line in text.splitlines():
        line = line.strip()
        # Ignore separators and empty lines
        if not line or line == "---":
            continue
        # Remove bullet if present
        if line.startswith("-"):
            line = line.lstrip("- ").strip()
        items.append(line)
    return items


def run(markdown_report: str):
        sections = {}
        current = None
        buffer = []
        for line in markdown_report.splitlines(): #Divide the text in lines and process them
            header = re.match(r"^##\s+(.*)", line) #If a title is detected
            if header:
                if current: #Saves the last section if exists
                    content = "\n".join(buffer).strip()
                    if current == "mission priorities":
                        sections[current] = parse_priorities(content)
                    else:
                        sections[current] = parse_list_section(content)
                current = header.group(1).lower()
                buffer = []
            else:
                buffer.append(line) #Add the goals, priorities and hazards
        if current: #Save the last section
            content = "\n".join(buffer).strip()
            if current == "mission priorities":
                sections[current] = parse_priorities(content)
            else:
                sections[current] = parse_list_section(content)

        return sections
def read_markdown(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

print(run(Path("inputs/mission_report.md").read_text(encoding="utf-8")))


# urls = ["https://science.nasa.gov/planetary-science/programs/mars-exploration/", "https://ai.jpl.nasa.gov/public/documents/presentations/CADRE-AAMAS-Slides.pdf"]
# urls = ["https://science.nasa.gov/mars/facts/"]

# def fetch_url_text(url: str, max_chars: int=30000) -> str:
#     # headers = {"User-Agent": "Mozilla/5.0 (compatible; MarsPlannerBot/1.0)"}
#     response = requests.get(url, timeout=10)
#     response.raise_for_status()
#     soup = BeautifulSoup(response.text, "html.parser")
#     for tag in soup(["script", "style", "noscript"]):
#         tag.decompose()
#     text = soup.get_text(separator=" ", strip=True)
#     return text[:max_chars]

# def run(structured_data: Dict, urls: list[str]) -> Dict:
#     extracted_info = []
#     for url in urls:
#         text = fetch_url_text(url)
#         extracted_info.append(text)
#     structured_data["external_sources"] = extracted_info
#     return structured_data
# dict_prova = {'hola': 'adios'}
# print(run(dict_prova, urls))




'''
from tools.mars_environment import *

## ENVIRONMENT
env1 = MarsEnvironment()
env2 = MarsEnvironment()

G = env1.get_graph()
node_id = list(G.nodes)[0]
print("Node ID:", node_id)
print("Node data:", env1.get_node_data(node_id))

print(env1 is env2) 
print(type(env1.get_graph()))'''


'''
## ROVERS
from crews.rover_crew.rover_tools import RoverPathfindingTool

# Instantiate the tool
tool = RoverPathfindingTool()

# Dummy input values (ajusta los nodos a los que existan en tu grafo)
start_node = "N60"
end_node = "N66"
rover_max_energy = 100.0
current_energy = 80.0

# Run the tool
result = tool._run(
    start_node=start_node,
    end_node=end_node,
    current_energy=current_energy
)

print("RESULT:")
print(result)
'''

'''
## DRONE
from crews.drone_crew.drone_tools import DroneFlightCheckTool
# Instantiate the tool
tool = DroneFlightCheckTool()

# Dummy input (ajusta els nodes als que realment existeixen al teu grafo)
start_node = "N60"
target_nodes = ["N62", "N63"]  # nodes que vols visitar

# Run the tool
result = tool._run(
    start_node=start_node,
    current_energy=100,
    target_nodes=target_nodes
)

print("RESULT:")
print(result)
'''

'''
# prova_satellite.py
from tools.mars_environment import MarsEnvironment
from crews.satellite_crew.satellite_tools import SatelliteTool

# Instantiate the satellite tool
sat_tool = SatelliteTool()

# Get the graph from your existing MarsEnvironment
env = MarsEnvironment()
graph = env.get_graph()

# -------------------------------
# Define some test scenarios
# -------------------------------
# Format: (target_node, mission_time, action)
tests = [
    ("N30", 2.0, "communicate_base"),  # Test comms with base station
    ("N84", 6.0, "communicate_base"),  # Test comms outside window
    ("N75", 1.0, "imaging"),           # Test visual imaging (maybe dust storm)
    ("IcyNode", 5.5, "thermal_scan"),  # Test thermal scan (ice or anomaly)
    ("UnknownNode", 1.0, "thermal_scan"),  # Invalid node test
]

# -------------------------------
# Run the tests
# -------------------------------
for node, time, action in tests:
    # Call the satellite tool's _run method
    result = sat_tool._run(node, time, action)
    
    # Print the scenario and its result
    print(f"Scenario: node={node}, time={time}, action={action}")
    print("Result:")
    print(result)
    print("-" * 60)
'''
