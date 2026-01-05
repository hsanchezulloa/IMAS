from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List
# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators
ollama_llm = LLM(
    model="ollama/deepseek-r1:14b", 
    base_url="http://localhost:11434",
    temperature=0.1
)
# class FinalMissionReport(BaseModel):
#     title: str = Field(..., description="The main title of the mission report.")
#     table_of_contents: str = Field(..., description="A markdown list of clickable links to sections.")
#     rover_section: str = Field(..., description="The complete integrated_rover.md content.")
#     drone_section: str = Field(..., description="The complete integrated_drone.md content.")
#     satellite_section: str = Field(..., description="The complete integrated_satellite.md content.")
#     conclusion: str = Field(..., description="A brief scientific summary of the joint mission readiness.")

class FinalMissionReport(BaseModel):
    title: str = Field(
        ..., description="The main title of the mission report."
    )

    table_of_contents: List[str] = Field(
        ..., description="List of section titles in order."
    )

    rover_section: str = Field(
        ..., description="The complete integrated_rover.md content."
    )

    drone_section: str = Field(
        ..., description="The complete integrated_drone.md content."
    )

    satellite_section: str = Field(
        ..., description="The complete integrated_satellite.md content."
    )

    conclusion: str = Field(
        ..., description="A brief scientific summary of the joint mission readiness."
    )

@CrewBase
class IntegrationCrew():
    """Integration Crew"""

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
    def integrator_rover(self) -> Agent:
        return Agent(
            config=self.agents_config['integrator_rover'], # type: ignore[index]
            verbose=True,
            llm=ollama_llm,
        )
    
    @agent
    def integrator_drone(self) -> Agent:
        return Agent(
            config=self.agents_config['integrator_drone'], # type: ignore[index]
            verbose=True,
            llm=ollama_llm,
        )
    
    @agent
    def integrator_satellite(self) -> Agent:
        return Agent(
            config=self.agents_config['integrator_satellite'], # type: ignore[index]
            verbose=True,
            llm=ollama_llm,
        )
    
    @agent
    def writer(self) -> Agent:
        return Agent(
            config=self.agents_config['writer'], # type: ignore[index]
            verbose=True,
            llm=ollama_llm,
            
        )

    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    @task
    def task_integrator_rover(self) -> Task:
        return Task(
            config=self.tasks_config['task_integrator_rover'], # type: ignore[index]
            output_file = 'integrator_rover.md',
        )

    @task
    def task_integrator_drone(self) -> Task:
        return Task(
            config=self.tasks_config['task_integrator_drone'], # type: ignore[index]
            output_file = 'integrator_drone.md',
        )
    
    @task
    def task_integrator_satellite(self) -> Task:
        return Task(
            config=self.tasks_config['task_integrator_satellite'], # type: ignore[index]
            output_file = 'integrator_satellite.md',
        )

    
    @task
    def task_writer(self) -> Task:
        return Task(
            config=self.tasks_config['task_writer'], # type: ignore[index]
            context=[self.task_integrator_rover(), self.task_integrator_drone(), self.task_integrator_satellite()],
            output_file='final_report.md',
            output_pydantic=FinalMissionReport
        )


    @crew
    def crew(self) -> Crew:
        """Creates the IntegrationCrew crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        
        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )

if __name__ == "__main__":
    crew = IntegrationCrew().crew()
    sample_collector_rover = Path("sample_collector_rover.md").read_text(encoding="utf-8")
    routes_rover = Path("routes_rover.json").read_text(encoding="utf-8")
    sample_collector_drone = Path("sample_collector_drone.md").read_text(encoding="utf-8")
    routes_drone = Path("routes_drone.json").read_text(encoding="utf-8")
    sample_collector_satellite = Path("image_capture_satellite.md").read_text(encoding="utf-8")
    routes_satellite= Path("routes_satellite.json").read_text(encoding="utf-8")
    result = crew.kickoff(inputs = {'routes_rover': routes_rover, 'sample_collector_rover': sample_collector_rover, 'routes_drone': routes_drone, 'sample_collector_drone':sample_collector_drone, 'routes_satellite': routes_satellite, 'sample_collector_satellite': sample_collector_satellite})

    # report_data = result.pydantic
    # report_data.satellite_section
