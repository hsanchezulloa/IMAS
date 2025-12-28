from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

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
            config=self.agents_config['planner'], # type: ignore[index]
            verbose=True
        )

    @agent
    def priority(self) -> Agent:
        return Agent(
            config=self.agents_config['priority'], # type: ignore[index]
            verbose=True
        )

    @agent
    def hazard(self) -> Agent:
        return Agent(
            config=self.agents_config['hazard'], # type: ignore[index]
            verbose=True
        )

    @agent
    def weather(self) -> Agent:
        return Agent(
            config=self.agents_config['weather'], # type: ignore[index]
            verbose=True
        )

    @agent
    def aggregator(self) -> Agent:
        return Agent(
            config=self.agents_config['aggregator'], # type: ignore[index]
            verbose=True
        )
    
    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    @task
    def additional_information(self) -> Task:
        return Task(
            config=self.tasks_config['additional_information'], # type: ignore[index]
        )

    @task
    def reporting_priority(self) -> Task:
        return Task(
            config=self.tasks_config['reporting_priority'], # type: ignore[index]
            output_file='report_priority.md',
            async_execution=True
        )

    @task
    def reporting_hazard(self) -> Task:
        return Task(
            config=self.tasks_config['reporting_hazard'], # type: ignore[index]
            output_file='report_hazard.md',
            async_execution=True
        )

    @task
    def reporting_weather(self) -> Task:
        return Task(
            config=self.tasks_config['reporting_weather'], # type: ignore[index]
            output_file='report_weather.md',
            async_execution=True
        )

    @task
    def reporting_aggregation(self) -> Task:
        return Task(
            config=self.tasks_config['reporting_aggregation'], # type: ignore[index]
            output_file='reporting_aggregation.md'
        )
    @task
    def extract_terrain(self) -> Task:
        return Task(
            config=self.tasks_config['extract_terrain'], # type: ignore[index]
            output_file='terrain.md'
        )
    
    @task
    def extract_edges(self) -> Task:
        return Task(
            config=self.tasks_config['extract_terrain'], # type: ignore[index]
            output_file='terrain.md'
        )


    @crew
    def crew(self) -> Crew:
        """Creates the MissionCrew crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
