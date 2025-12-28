
from typing import Type, Dict, Any
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
import re
import requests
from bs4 import BeautifulSoup

# def parse_priorities(text: str) -> dict:
#     priorities = {"high": [],"medium": [],"low": []}
#     current = None
#     for line in text.splitlines():
#         line = line.strip()
#         # Detect priority headers
#         if re.match(r"\d+\.\s*\*\*High Priority\*\*", line):
#             current = "high"
#             continue
#         if re.match(r"\d+\.\s*\*\*Medium Priority\*\*", line):
#             current = "medium"
#             continue
#         if re.match(r"\d+\.\s*\*\*Low Priority\*\*", line):
#             current = "low"
#             continue
#         # Capture bullet points
#         if current and line.startswith("-"):
#             priorities[current].append(line.lstrip("- ").strip())

#     return priorities

# def parse_list_section(text: str) -> list[str]:
#     items = []
#     for line in text.splitlines():
#         line = line.strip()
#         # Ignore separators and empty lines
#         if not line or line == "---":
#             continue
#         # Remove bullet if present
#         if line.startswith("-"):
#             line = line.lstrip("- ").strip()
#         items.append(line)
#     return items


# def run(markdown_report: str):
#         sections = {}
#         current = None
#         buffer = []
#         for line in markdown_report.splitlines(): #Divide the text in lines and process them
#             header = re.match(r"^##\s+(.*)", line) #If a title is detected
#             if header:
#                 if current: #Saves the last section if exists
#                     content = "\n".join(buffer).strip()
#                     if current == "mission priorities":
#                         sections[current] = parse_priorities(content)
#                     else:
#                         sections[current] = parse_list_section(content)
#                 current = header.group(1).lower()
#                 buffer = []
#             else:
#                 buffer.append(line) #Add the goals, priorities and hazards
#         if current: #Save the last section
#             content = "\n".join(buffer).strip()
#             if current == "mission priorities":
#                 sections[current] = parse_priorities(content)
#             else:
#                 sections[current] = parse_list_section(content)

#         return sections
# def read_markdown(path: str) -> str:
#     with open(path, "r", encoding="utf-8") as f:
#         return f.read()

# print(run(read_markdown("inputs\mission_report.md")))


# urls = ["https://science.nasa.gov/planetary-science/programs/mars-exploration/", "https://ai.jpl.nasa.gov/public/documents/presentations/CADRE-AAMAS-Slides.pdf"]
urls = ["https://science.nasa.gov/mars/facts/"]

def fetch_url_text(url: str, max_chars: int=30000) -> str:
    # headers = {"User-Agent": "Mozilla/5.0 (compatible; MarsPlannerBot/1.0)"}
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    text = soup.get_text(separator=" ", strip=True)
    return text[:max_chars]

def run(structured_data: Dict, urls: list[str]) -> Dict:
    extracted_info = []
    for url in urls:
        text = fetch_url_text(url)
        extracted_info.append(text)
    structured_data["external_sources"] = extracted_info
    return structured_data
dict_prova = {'hola': 'adios'}
print(run(dict_prova, urls))