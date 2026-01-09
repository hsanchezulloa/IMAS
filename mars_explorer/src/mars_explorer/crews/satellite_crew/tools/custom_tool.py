from typing import Any, Dict, List, Type
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
import xml.etree.ElementTree as ET
import networkx as nx



        
class GraphInput(BaseModel):
    """Input schema for CommunicationLossTool."""
    file_path: str = Field(..., description="Path to the .graphml file to be analyzed.")

class CommunicationLossTool(BaseTool):
    name: str = "Communication_Loss_Detector"
    description: str = "Parses a GraphML file and returns a list of Node IDs where communication loss is active."
    args_schema: Type[BaseModel] = GraphInput

    def _run(self, file_path: str) -> str:
        try:
            # Load the graph
            G = nx.read_graphml(file_path)
            
            # Filter nodes where communication_loss is True
            # In GraphML, boolean data is often stored as strings 'true'/'false'
            lost_comm_nodes = [
                node_id for node_id, data in G.nodes(data=True) 
                if str(data.get('communication_loss')).lower() == 'true'
            ]
            
            if not lost_comm_nodes:
                return "Analysis complete: No nodes with communication loss detected."
            print('LOST COMM NODES', lost_comm_nodes)
            return f"Nodes with Communication Loss: {', '.join(lost_comm_nodes)}"
        
        except Exception as e:
            return f"Error parsing GraphML: {str(e)}"
