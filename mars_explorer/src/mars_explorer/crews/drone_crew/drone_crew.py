from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from crews.rover_crew.tools.custom_tool import DroneFlightCheckTool

# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class DronesCrew():
    """DronesCrew crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    
    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools
    @agent
    def flight_planner_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['flight_planner_agent'], # type: ignore[index]
            verbose=True
        )

    @agent
    def drone_sample_collector(self) -> Agent:
        return Agent(
            config=self.agents_config['drone_sample_collector'], # type: ignore[index]
            verbose=True
        )

    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    @task
    def generating_route(self) -> Task:
        return Task(
            config=self.tasks_config['generating_route'], # type: ignore[index]
            output_file='generate_route_drone.md',
            async_execution=True
        )

    @task
    def generate_sampling(self) -> Task:
        return Task(
            config=self.tasks_config['generate_sampling'], # type: ignore[index]
            output_file='generate_sampling_drone.md',
            async_execution=True
        )

    @crew
    def crew(self) -> Crew:
        """Creates the DronesCrew crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
