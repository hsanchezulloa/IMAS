from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List

ollama_llm = LLM(
    model="ollama/deepseek-r1:14b", 
    base_url="http://localhost:11434",
    temperature=0.1,
    timeout=3600
)


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

    def to_markdown(self) -> str:
        toc = "\n".join(f"- {item}" for item in self.table_of_contents)

        return f"""# {self.title}
    ## Table of Contents
    {toc}

    {self.rover_section}

    {self.drone_section}

    {self.satellite_section}

    ## Conclusion
    {self.conclusion}
    """


@CrewBase
class IntegrationCrew():
    """Integration Crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"


    @agent
    def integrator_rover(self) -> Agent:
        return Agent(
            config=self.agents_config['integrator_rover'],
            verbose=True,
            llm=ollama_llm,
        )
    
    @agent
    def integrator_drone(self) -> Agent:
        return Agent(
            config=self.agents_config['integrator_drone'],
            verbose=True,
            llm=ollama_llm,
        )
    
    @agent
    def integrator_satellite(self) -> Agent:
        return Agent(
            config=self.agents_config['integrator_satellite'],
            verbose=True,
            llm=ollama_llm,
        )
    
    @agent
    def writer(self) -> Agent:
        return Agent(
            config=self.agents_config['writer'],
            verbose=True,
            llm=ollama_llm,
            
        )


    @task
    def task_integrator_rover(self) -> Task:
        return Task(
            config=self.tasks_config['task_integrator_rover'],
            output_file = 'integrator_rover.md',
            async_execution=True
        )

    @task
    def task_integrator_drone(self) -> Task:
        return Task(
            config=self.tasks_config['task_integrator_drone'],
            output_file = 'integrator_drone.md',
            async_execution=True
        )
    
    @task
    def task_integrator_satellite(self) -> Task:
        return Task(
            config=self.tasks_config['task_integrator_satellite'], 
            output_file = 'integrator_satellite.md',
            async_execution=True
        )

    
    @task
    def task_writer(self) -> Task:
        return Task(
            config=self.tasks_config['task_writer'], 
            context=[self.task_integrator_rover(), self.task_integrator_drone(), self.task_integrator_satellite()],
            output_file='final_report.json',
            output_pydantic=FinalMissionReport
        )


    @crew
    def crew(self) -> Crew:
        """Creates the IntegrationCrew crew"""
        
        return Crew(
            agents=self.agents, 
            tasks=self.tasks, 
            process=Process.sequential,
            verbose=True,
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

