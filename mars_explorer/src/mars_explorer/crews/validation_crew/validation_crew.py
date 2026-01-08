from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from pathlib import Path
# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators
ollama_llm = LLM(
    model="ollama/deepseek-r1:14b", 
    base_url="http://localhost:11434",
    temperature=0.1
)

@CrewBase
class ValidationCrew():
    """Validation Crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools
    @agent
    def validation_rover(self) -> Agent:
        return Agent(
            config=self.agents_config['validation_rover'], # type: ignore[index]
            verbose=True,
            llm=ollama_llm,
        )
    
    @agent
    def validation_drone(self) -> Agent:
        return Agent(
            config=self.agents_config['validation_drone'], # type: ignore[index]
            verbose=True,
            llm=ollama_llm,
        )
    
    @agent
    def validation_satellite(self) -> Agent:
        return Agent(
            config=self.agents_config['validation_satellite'], # type: ignore[index]
            verbose=True,
            llm=ollama_llm,
        )
    
    @agent
    def combine_validations(self) -> Agent:
        return Agent(
            config=self.agents_config['combine_validations'], # type: ignore[index]
            verbose=True,
            llm=ollama_llm,
        )


    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
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
            config=self.tasks_config['task_validation_drone'], # type: ignore[index]
            output_file='validation_drone.json',
            async_execution=True
        )
    
    @task
    def task_validation_satellite(self) -> Task:
        return Task(
            config=self.tasks_config['task_validation_satellite'], # type: ignore[index]
            output_file='validation_satellite.json',
            async_execution=True
        )
    
    @task
    def task_combine_validations(self) -> Task:
        return Task(
            config=self.tasks_config['task_combine_validations'], # type: ignore[index]
            context = [self.task_validation_rover(), self.task_validation_drone(), self.task_validation_satellite()],
            output_file='combine_validations.json',
        )

    @crew
    def crew(self) -> Crew:
        """Creates the ValidationCrew crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge
        # return Crew(
        #     agents = [self.validation_drone()],
        #     tasks = [self.task_validation_drone()],
        #     process = Process.sequential,
        #     verbose=True
        # )
    
        # return Crew(
        #     agents = [self.validation_satellite()],
        #     tasks = [self.task_validation_satellite()],
        #     process = Process.sequential,
        #     verbose=True
        # )

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )

if __name__ == "__main__":
    crew = ValidationCrew().crew()

    # reporting_aggregation = Path("reporting_aggregation.json").read_text(encoding="utf-8")
    # routes_drone = Path("routes_drone.json").read_text(encoding="utf-8")
    # result = crew.kickoff(inputs = {'routes_drone': routes_drone, 'reporting_aggregation': reporting_aggregation})

    reporting_aggregation = Path("reporting_aggregation.json").read_text(encoding="utf-8")
    routes_satellite = Path("routes_satellite.json").read_text(encoding="utf-8")
    routes_drone = Path("routes_drone.json").read_text(encoding="utf-8")
    routes_rover = Path("routes_rover.json").read_text(encoding="utf-8")
    result = crew.kickoff(inputs = {'routes_drone': routes_drone, 'routes_satellite': routes_satellite,'routes_rover': routes_rover, 'reporting_aggregation': reporting_aggregation})





