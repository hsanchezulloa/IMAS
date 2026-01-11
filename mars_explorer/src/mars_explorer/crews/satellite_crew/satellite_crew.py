from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from pydantic import BaseModel
from typing import List
from pathlib import Path
from crews.satellite_crew.tools.custom_tool import CommunicationLossTool

ollama_llm = LLM(
    model='ollama/deepseek-r1:14b',
    base_url="http://localhost:11434",
    temperature=0.1,
    timeout=3600
)

class SatelliteAssignment(BaseModel):
    id: str
    goal: str
    location: str
    communication_window: str

class PlannerOutput(BaseModel):
    assignments: List[SatelliteAssignment]

@CrewBase
class SatelliteCrew():
    """Satellites crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    @agent
    def communication_loss_extractor(self) -> Agent:
        return Agent(
            config=self.agents_config['communication_loss_extractor'],
            verbose=True,
            llm = ollama_llm,
            tools = [CommunicationLossTool()]
        )

    @agent
    def extractor(self) -> Agent:
        return Agent(
            config=self.agents_config['extractor'],
            verbose=True,
            llm = ollama_llm
        )
    
    @agent
    def planner(self) -> Agent:
        return Agent(
            config=self.agents_config['planner'],
            verbose=True,
            llm = ollama_llm
        )
    
    @agent
    def image_capture(self) -> Agent:
        return Agent(
            config=self.agents_config['image_capture'],
            verbose=True,
            llm = ollama_llm
        )

    @task
    def task_communication_loss_extractor(self) -> Task:
        return Task(
            config=self.tasks_config['task_communication_loss_extractor'], 
            async_execution=False
        )
    
    @task
    def task_extractor(self) -> Task:
        return Task(
            config=self.tasks_config['task_extractor'], 
            async_execution=False
        )
    @task
    def task_planner(self) -> Task:
        return Task(
            config=self.tasks_config['task_planner'], 
            context=[self.task_communication_loss_extractor(), self.task_extractor()],
            output_pydantic=PlannerOutput,
            output_file='routes_satellite.json',
            async_execution=False
        )
    
    @task
    def task_image_capture(self) -> Task:
        return Task(
            config=self.tasks_config['task_image_capture'], 
            output_file='image_capture_satellite.md',
            async_execution=False
        )
    
    
    
    @crew
    def crew(self) -> Crew:
        """Creates the Satellites crew"""
        return Crew(
            agents=self.agents, 
            tasks=self.tasks, 
            process=Process.sequential,
            verbose=True,
        )

if __name__ == "__main__":
    crew = SatelliteCrew().crew()
    report_priority = Path("report_priority.json").read_text(encoding="utf-8")
    report_hazard_constraints = Path("report_hazard_constraints.json").read_text(encoding="utf-8")
    satellite_json = Path("inputs/satellites.json").read_text(encoding="utf-8")
    result = crew.kickoff(inputs = {'report_priority': report_priority, 'report_hazard_constraints': report_hazard_constraints, 'satellite_json': satellite_json})

