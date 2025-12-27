from typing import Type, Dict
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
import re
import requests
from bs4 import BeautifulSoup

class PlannerDivideInput(BaseModel):
    """
    Input schema for dividing mission report.
    """
    markdown_report: str = Field(..., description="Full Mars mission report in Markdown format.")

class PlannerDivideTool(BaseTool):
    name: str = "planner_divide_report"
    description: str = ("Divides the Mars mission Markdown report into structured sections: priorities, hazards, weather, constraints, and goals.")
    args_schema: Type[BaseModel] = PlannerDivideInput

    def _run(self, markdown_report: str) -> Dict[str, str]:
        sections = {}
        current = None
        buffer = []
        for line in markdown_report.splitlines(): #Divide the text in lines and process them
            header = re.match(r"^##\s+(.*)", line) #If a title is detected
            if header:
                if current: #Saves the last section if exists
                    sections[current] = "\n".join(buffer).strip()
                current = header.group(1).lower()
                buffer = []
            else:
                buffer.append(line) #Add the goals, priorities and hazards
        if current: #Save the last section
            sections[current] = "\n".join(buffer).strip()

        return sections

class PlannerEnrichInput(BaseModel):
    """
    Input schema for enriching mission data.
    """
    structured_data: Dict = Field(..., description="Structured mission data extracted from report.")
    urls: list[str] = Field(default_factory=list, description="External URLs containing relevant information. The tool must extract key facts and integrate them into the structured data.")

class PlannerEnrichTool(BaseTool):
    name: str = "planner_enrich_with_urls"
    description: str = ("Extracts relevant information from provided URLs and integrates it into structured mission data.")
    args_schema: Type[BaseModel] = PlannerEnrichInput

    def _fetch_url_text(self, url: str, max_chars: int = 3000) -> str:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        text = soup.get_text(separator=" ", strip=True)
        return text[:max_chars]

        html = requests.get(url, timeout=5).text
        soup = BeautifulSoup(html, "html.parser")
        return soup.get_text()[:1000]

    def _run(self, structured_data: Dict, urls: list[str]) -> Dict:
        extracted_info = []
        for url in urls:
            extracted_info.append({"source": url, "summary": f"Relevant mission-related information extracted from {url}."})
        structured_data["external_sources"] = urls
        structured_data["enrichment_status"] = "simulated"
        return structured_data


class MyCustomToolInput(BaseModel):
    """Input schema for MyCustomTool."""

    argument: str = Field(..., description="Description of the argument.")


class MyCustomTool(BaseTool):
    name: str = "Name of my tool"
    description: str = (
        "Clear description for what this tool is useful for, your agent will need this information to use it."
    )
    args_schema: Type[BaseModel] = MyCustomToolInput

    def _run(self, argument: str) -> str:
        # Implementation goes here
        return "this is an example of a tool output, ignore it and move along."
