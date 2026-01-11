from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from pathlib import Path
from crews.mission_crew.tools.custom_tool import (
    PlannerDivideTool,
    PlannerEnrichTool,
)
ollama_llm = LLM(
    model="ollama/deepseek-r1:14b", 
    base_url="http://localhost:11434",
    temperature=0.1,
    timeout=3600
)

@CrewBase
class MissionCrew():
    """MissionCrew crew"""

    agents: List[BaseAgent]
    tasks: List[Task]
    @agent
    def planner(self) -> Agent:
        return Agent(
            config=self.agents_config['planner'],
            verbose=True,
            llm=ollama_llm,
            tools = [PlannerDivideTool()]
        )

    @agent
    def priority(self) -> Agent:
        return Agent(
            config=self.agents_config['priority'],
            verbose=True,
            llm=ollama_llm
        )

    @agent
    def hazard(self) -> Agent:
        return Agent(
            config=self.agents_config['hazard'], 
            verbose=True,
            llm=ollama_llm
        )

    @agent
    def aggregator(self) -> Agent:
        return Agent(
            config=self.agents_config['aggregator'], 
            verbose=True,
            llm=ollama_llm
        )

    @task
    def additional_information(self) -> Task:
        return Task(
            config=self.tasks_config['additional_information'],
            output_file='extract_md.json',
        )

    @task
    def reporting_priority(self) -> Task:
        return Task(
            config=self.tasks_config['reporting_priority'], 
            output_file='report_priority.json',
            context=[self.additional_information()],
            async_execution=True
        )

    @task
    def reporting_hazard(self) -> Task:
        return Task(
            config=self.tasks_config['reporting_hazard'], 
            output_file='report_hazard_constraints.json',
            context=[self.additional_information()],
            async_execution=True
        )

    @task
    def reporting_aggregation(self) -> Task:
        return Task(
            config=self.tasks_config['reporting_aggregation'],
            context=[self.reporting_priority(), self.reporting_hazard()], 
            expected_output="""
            A JSON object with the following keys:
            - rovers
            - drones
            - satellites
            Each value must be a string.
            """,
            output_file='reporting_aggregation.json'
        )
    
    @crew
    def crew(self) -> Crew:
        """Creates the MissionCrew crew"""
        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )

if __name__ == "__main__":
    crew = MissionCrew().crew()
    mission_report = Path("inputs/mission_report.md").read_text(encoding="utf-8")
    result = crew.kickoff(inputs = {"mission_report": mission_report})
