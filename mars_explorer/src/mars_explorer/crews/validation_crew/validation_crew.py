from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from pathlib import Path

ollama_llm = LLM(
    model="ollama/deepseek-r1:14b", 
    base_url="http://localhost:11434",
    temperature=0.1,
    timeout=3600
)

@CrewBase
class ValidationCrew():
    """Validation Crew"""

    agents: List[BaseAgent]
    tasks: List[Task]
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def validation_rover(self) -> Agent:
        return Agent(
            config=self.agents_config['validation_rover'],
            verbose=True,
            llm=ollama_llm,
        )
    
    @agent
    def validation_drone(self) -> Agent:
        return Agent(
            config=self.agents_config['validation_drone'],
            verbose=True,
            llm=ollama_llm,
        )
    
    @agent
    def validation_satellite(self) -> Agent:
        return Agent(
            config=self.agents_config['validation_satellite'],
            verbose=True,
            llm=ollama_llm,
        )
    
    @agent
    def combine_validations(self) -> Agent:
        return Agent(
            config=self.agents_config['combine_validations'],
            verbose=True,
            llm=ollama_llm,
        )


    @task
    def task_validation_rover(self) -> Task:
        return Task(
            config=self.tasks_config['task_validation_rover'],
            output_file='validation_rover.json',
            async_execution=True
        )
    
    @task
    def task_validation_drone(self) -> Task:
        return Task(
            config=self.tasks_config['task_validation_drone'],
            output_file='validation_drone.json',
            async_execution=True
        )
    
    @task
    def task_validation_satellite(self) -> Task:
        return Task(
            config=self.tasks_config['task_validation_satellite'],
            output_file='validation_satellite.json',
            async_execution=True
        )
    
    @task
    def task_combine_validations(self) -> Task:
        return Task(
            config=self.tasks_config['task_combine_validations'],
            context = [self.task_validation_rover(), self.task_validation_drone(), self.task_validation_satellite()],
            output_file='combine_validations.json',
        )

    @crew
    def crew(self) -> Crew:
        """Creates the ValidationCrew crew"""
        
        return Crew(
            agents=self.agents, 
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )

if __name__ == "__main__":
    crew = ValidationCrew().crew()
    reporting_aggregation = Path("reporting_aggregation.json").read_text(encoding="utf-8")
    routes_satellite = Path("routes_satellite.json").read_text(encoding="utf-8")
    routes_drone = Path("routes_drone.json").read_text(encoding="utf-8")
    routes_rover = Path("routes_rover.json").read_text(encoding="utf-8")
    result = crew.kickoff(inputs = {'routes_drone': routes_drone, 'routes_satellite': routes_satellite,'routes_rover': routes_rover, 'reporting_aggregation': reporting_aggregation})





