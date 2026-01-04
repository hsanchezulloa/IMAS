from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators
ollama_llm = LLM(
    model='ollama/deepseek-r1:14b',
    base_url="http://localhost:11434",
    temperature=0.1
)

@CrewBase
class SatelliteCrew():
    """Satellites crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    
    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools
    @agent
    def communication_loss_extractor(self) -> Agent:
        return Agent(
            config=self.agents_config['communication_loss_extractor'],
            verbose=True,
            llm = ollama_llm
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
    
    @agent
    def thermal_scan(self) -> Agent:
        return Agent(
            config=self.agents_config['thermal_scan'],
            verbose=True,
            llm = ollama_llm
        )

    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    @task
    def task_communication_loss_extractor(self) -> Task:
        return Task(
            config=self.tasks_config['task_communication_loss_extractor'], 
            async_execution=True
        )
    
    @task
    def task_extractor(self) -> Task:
        return Task(
            config=self.tasks_config['task_extractor'], 
            async_execution=True
        )
    
    @task
    def task_image_capture(self) -> Task:
        return Task(
            config=self.tasks_config['task_image_capture'], 
            output_file='image_capture_satellite.md',
            async_execution=True
        )
    
    @task
    def task_thermal_scan(self) -> Task:
        return Task(
            config=self.tasks_config['task_thermal_scan'], 
            output_file='thermal_scan_satellite.md',
            async_execution=True
        )
    
    @task
    def task_planner(self) -> Task:
        return Task(
            config=self.tasks_config['task_planner'], 
            # context = [],
            output_file='satellite_route.json'
        )
    
    
    
    @crew
    def crew(self) -> Crew:
        """Creates the Satellites crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge
        # return Crew(agents=[self.aggregator()], tasks = [self.reporting_aggregation()], process = Process.sequential, verbose=True)
        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
