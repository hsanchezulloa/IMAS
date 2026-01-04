from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from pathlib import Path
from crews.mission_crew.tools.custom_tool import (
    PlannerDivideTool,
    PlannerEnrichTool,
)
# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators
ollama_llm = LLM(
    model="ollama/deepseek-r1:14b", 
    base_url="http://localhost:11434",
    temperature=0.1
)

@CrewBase
class MissionCrew():
    """MissionCrew crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    
    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools
    
        
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
    def weather(self) -> Agent:
        return Agent(
            config=self.agents_config['weather'], 
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
    
    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
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
            output_file='report_priority.md',
            async_execution=True
        )

    @task
    def reporting_hazard(self) -> Task:
        return Task(
            config=self.tasks_config['reporting_hazard'], 
            output_file='report_hazard.md',
            async_execution=True
        )

    @task
    def reporting_weather(self) -> Task:
        return Task(
            config=self.tasks_config['reporting_weather'], 
            output_file='report_weather.md',
            async_execution=True
        )

    @task
    def reporting_aggregation(self) -> Task:
        return Task(
            config=self.tasks_config['reporting_aggregation'], 
            expected_output="""
            A JSON object with the following keys:
            - rovers
            - drones
            - satellites
            Each value must be a string.
            """,
            output_file='reporting_aggregation.md'
        )
    
    @crew
    def crew(self) -> Crew:
        """Creates the MissionCrew crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge
        return Crew(agents=[self.planner()], tasks = [self.additional_information()], process = Process.sequential, verbose=True)
        # return Crew(
        #     agents=self.agents, # Automatically created by the @agent decorator
        #     tasks=self.tasks, # Automatically created by the @task decorator
        #     process=Process.sequential,
        #     verbose=True,
        #     # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        # )

if __name__ == "__main__":
    crew = MissionCrew().crew()
    mission_report = Path("inputs/mission_report.md").read_text(encoding="utf-8")
    print(mission_report)
    result = crew.kickoff(inputs = {"mission_report": mission_report})
    print(result)
