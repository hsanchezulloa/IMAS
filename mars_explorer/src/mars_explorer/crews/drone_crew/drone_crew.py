from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from crews.drone_crew.tools_drone.custom_tool import BatchDroneFlightTool
from pathlib import Path

ollama_llm = LLM(
    model="ollama/deepseek-r1:14b", 
    base_url="http://localhost:11434",
    temperature=0.1
)

@CrewBase
class DronesCrew():
    """DronesCrew crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    @agent
    def extractor(self) -> Agent:
        return Agent(
            config=self.agents_config["extractor"],
            llm = ollama_llm,
        )
    
    @agent
    def flight_planner(self) -> Agent:
        return Agent(
            config=self.agents_config['flight_planner'],
            verbose=True,
            llm=ollama_llm,
            tools = [BatchDroneFlightTool()]
        )

    @agent
    def sample_collector(self) -> Agent:
        return Agent(
            config=self.agents_config['sample_collector'],
            llm=ollama_llm,
            verbose=True
        )

    @task
    def final_nodes(self) -> Task:
        return Task(
            config=self.tasks_config["final_nodes"],
        )
    
    @task
    def reporting_route(self) -> Task:
        return Task(
            config=self.tasks_config['reporting_route'],
            context=[self.final_nodes()],
            output_file='routes_drone.json',
        )

    @task
    def generate_sampling(self) -> Task:
        return Task(
            config=self.tasks_config['generate_sampling'],
            output_file='sample_collector_drone.md',
            async_execution=True
        )

    @crew
    def crew(self) -> Crew:
        """Creates the DronesCrew crew"""

        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )


if __name__ == '__main__':
    crew = DronesCrew().crew()
    report_priority = Path("report_priority.json").read_text(encoding="utf-8")
    drones = Path("inputs/drones.json").read_text(encoding="utf-8")
    result = crew.kickoff(inputs={'report_priority': report_priority, 'drones': drones})

