from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from pydantic import BaseModel
from crews.rover_crew.tools_rover.custom_tool import RoverPathfindingTool, MultiRoverNodeAssignerTool
from pathlib import Path

ollama_llm = LLM(
    model='ollama/deepseek-r1:14b',
    base_url='http://localhost:11434',
    temperature=0.1,
    timeout=3600
)
class RouteOutput(BaseModel):
    # Since the tool returns a Dict[str, Any], we can use a generic dict 
    # or define it more strictly.
    results: dict
@CrewBase
class RoverCrew:
    """Rover Crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def extractor(self) -> Agent:
        return Agent(
            config=self.agents_config["extractor"],
            llm = ollama_llm,
        )
        
    @agent
    def route_planner(self) -> Agent:
        return Agent(
            config=self.agents_config["route_planner"],
            tools = [RoverPathfindingTool()],
            llm = ollama_llm,
            max_iter=3,
            cache=False,
            verbose=False
        )
    
    @agent
    def ranking(self) -> Agent:
        return Agent(
            config=self.agents_config["ranking"],
            tools = [MultiRoverNodeAssignerTool()],
            llm = ollama_llm,
            max_iter=3,
            allow_delegation=False,
            cache=False,
            verbose=True
        )

    @agent
    def sample_collector(self) -> Agent:
        return Agent(
            config=self.agents_config["sample_collector"],
            llm = ollama_llm
        )

    @task
    def final_nodes(self) -> Task:
        return Task(
            config=self.tasks_config["final_nodes"],
        )

    @task
    def reporting_route(self) -> Task:
        return Task(
            config=self.tasks_config["reporting_route"],
            context=[self.final_nodes()],
            output_json=RouteOutput,
            output_file='possible_routes_rover.json',
        )
    
    @task
    def task_ranking(self) -> Task:
        return Task(
            config=self.tasks_config["task_ranking"],
            context=[self.reporting_route()],
            output_file='routes_rover.json',
        )

    @task
    def reporting_sampling(self) -> Task:
        return Task(
            config=self.tasks_config["reporting_sampling"],
            output_file='sample_colllector_rover.md',
            async_execution=True
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Research Crew"""
        return Crew(
            agents=[self.extractor(), self.route_planner(), self.ranking()],
            tasks=[self.final_nodes(), self.reporting_route(), self.task_ranking()],
            process=Process.sequential,
            verbose=True
        )
        # return Crew(
        #     agents=self.agents,
        #     tasks=self.tasks,
        #     process=Process.sequential,
        #     verbose=True,
        # )


if __name__ == '__main__':
    crew = RoverCrew().crew()
    # routes_rover = json.loads(Path("possible_routes_rover.json").read_text(encoding="utf-8"))
    # report_priority = Path("report_priority.json").read_text(encoding="utf-8")
    # rovers = Path("inputs/rovers.json").read_text(encoding="utf-8")
    # result = crew.kickoff(inputs={'report_priority': report_priority, 'rovers': rovers})

    report_priority = Path("report_priority.json").read_text(encoding="utf-8")
    rovers = Path("inputs/rovers.json").read_text(encoding="utf-8")
    result = crew.kickoff(inputs={'report_priority': report_priority, 'rovers': rovers})
    # print(result.raw)
