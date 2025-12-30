from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from crews.mission_crew.tools.custom_tool import (
    PlannerDivideTool,
    PlannerEnrichTool,
)
# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators
ollama_llm = LLM(
    model="ollama/phi4", 
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
    def extractor_graph(self) -> Agent:
        return Agent(
            config=self.agents_config['extractor_graph'],
            verbose=True,
            llm=ollama_llm
        )
        
    @agent
    def planner(self) -> Agent:
        return Agent(
            config=self.agents_config['planner'],
            verbose=True,
            llm=ollama_llm,
            tools = [PlannerDivideTool(), PlannerEnrichTool()]
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
    # @task
    # def extract_terrain(self) -> Task:
    #     return Task(
    #         config=self.tasks_config['extract_terrain'], 
    #         output_file='terrain.json'
    #     )
    
    # @task
    # def extract_is_base(self) -> Task:
    #     return Task(
    #         config=self.tasks_config['extract_is_base'], 
    #         output_file='base.json'
    #     )
    
    # @task
    # def extract_communication_loss(self) -> Task:
    #     return Task(
    #         config=self.tasks_config['extract_communication_loss'], 
    #         output_file='communication.json'
    #     )
    # @task
    # def extract_high_radiation(self) -> Task:
    #     return Task(
    #         config=self.tasks_config['extract_high_radiation'], 
    #         output_file='radiation.json'
    #     )
    
    # @task
    # def extract_unstable(self) -> Task:
    #     return Task(
    #         config=self.tasks_config['extract_unstable'], 
    #         output_file='unstable.json'
    #     )
    
    # @task
    # def extract_dust_storms(self) -> Task:
    #     return Task(
    #         config=self.tasks_config['extract_dust_storms'], 
    #         output_file='dust_storms.json'
    #     )
    
    # @task
    # def extract_wind(self) -> Task:
    #     return Task(
    #         config=self.tasks_config['extract_wind'], 
    #         output_file='wind.json'
    #     )
    
    # @task
    # def extract_temperature(self) -> Task:
    #     return Task(
    #         config=self.tasks_config['extract_temperature'], 
    #         output_file='temperature.json'
    #     )
    
    # @task
    # def extract_edge_lengths(self) -> Task:
    #     return Task(
    #         config=self.tasks_config['extract_edge_lengths'], 
    #         output_file='edges.json'
    #     )

    @task
    def extract_martian_environment_data(self) -> Task:
        return Task(
            config=self.tasks_config['extract_martian_environment_data'], 
            output_file='environment_data.json',
            expected_output="A JSON dictionary containing all nodes, edges, and attributes extracted from the GraphML file."
        )
    
    @crew
    def crew(self) -> Crew:
        """Creates the MissionCrew crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge
        return Crew(agents=[self.extractor_graph()], tasks = [self.extract_martian_environment_data()], process = Process.sequential, verbose=True)
        # return Crew(
        #     agents=self.agents, # Automatically created by the @agent decorator
        #     tasks=self.tasks, # Automatically created by the @task decorator
        #     process=Process.sequential,
        #     verbose=True,
        #     # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        # )

if __name__ == "__main__":
    crew = MissionCrew().crew()
    result = crew.kickoff()
    print(result)

    