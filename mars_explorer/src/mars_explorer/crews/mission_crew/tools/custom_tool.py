from typing import Any, Dict, List, Type
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
import re
import requests
from bs4 import BeautifulSoup
import re


class PlannerDivideInput(BaseModel):
    """
    Input schema for dividing mission report.
    """
    markdown_report: str = Field(..., description="The RAW markdown text. MUST contain the 'Scientific Goals', 'Operational Constraints', 'Mission Priorities' and 'Known Hazards' sections. DO NOT SPLIT INTO KEYS.")

class PlannerDivideTool(BaseTool):
    name: str = "planner_divide_report"
    description: str = ("Divides the Mars mission Markdown report into structured sections: 'Scientific Goals', 'Operational Constraints', 'Mission Priorities' and 'Known Hazards'.")
    args_schema: Type[BaseModel] = PlannerDivideInput

    def _parse_priorities(self, text: str) -> dict:
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
    
    def _parse_list_section(self, text: str) -> list[str]:
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

    def _run(self, markdown_report: str) -> Dict[str, Any]:
        sections = {}
        current = None
        buffer = []
        for line in markdown_report.splitlines(): #Divide the text in lines and process them
            header = re.match(r"^##\s+(.*)", line) #If a title is detected
            if header:
                if current: #Saves the last section if exists
                    content = "\n".join(buffer).strip()
                    if current == "mission priorities":
                        sections[current] = self._parse_priorities(content)
                    else:
                        sections[current] = self._parse_list_section(content)
                current = header.group(1).lower()
                buffer = []
            else:
                buffer.append(line) #Add the goals, priorities and hazards
        if current: #Save the last section
            content = "\n".join(buffer).strip()
            if current == "mission priorities":
                sections[current] = self._parse_priorities(content)
            else:
                sections[current] = self._parse_list_section(content)

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

    def _fetch_url_text(self, url: str, max_chars: int=30000) -> str:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        text = soup.get_text(separator=" ", strip=True)
        return text[:max_chars]

    def _run(self, structured_data: Dict, urls: list[str]) -> Dict:
        extracted_info = []
        for url in urls:
            text = self._fetch_url_text(url)
            extracted_info.append(text)
        structured_data["external_sources"] = extracted_info
        return structured_data



# class MyCustomToolInput(BaseModel):
#     """Input schema for MyCustomTool."""

#     argument: str = Field(..., description="Description of the argument.")


# class MyCustomTool(BaseTool):
#     name: str = "Name of my tool"
#     description: str = (
#         "Clear description for what this tool is useful for, your agent will need this information to use it."
#     )
#     args_schema: Type[BaseModel] = MyCustomToolInput

#     def _run(self, argument: str) -> str:
#         # Implementation goes here
#         return "this is an example of a tool output, ignore it and move along."
