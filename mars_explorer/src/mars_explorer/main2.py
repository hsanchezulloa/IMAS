from pydantic import BaseModel
from pathlib import Path
import json
import re
from crewai.flow import Flow, start, listen, and_, or_, router
from crews.mission_crew.mission_crew import MissionCrew
from crews.rover_crew.rover_crew import RoverCrew
from crews.drone_crew.drone_crew import DronesCrew
from crews.satellite_crew.satellite_crew import SatelliteCrew
from crews.validation_crew.validation_crew import ValidationCrew
from crews.integration_crew.integration_crew import IntegrationCrew


class ValidationResult(BaseModel):
    rover_ok: bool
    drone_ok: bool
    satellite_ok: bool

class MarsFlow(Flow):
    MAX_RETRIES = 3

    def __init__(self, mission_crew, rover_crew, drone_crew, satellite_crew, validation_crew, integration_crew):
        super().__init__()
        self.mission_crew = mission_crew
        self.rover_crew = rover_crew
        self.drone_crew = drone_crew
        self.satellite_crew = satellite_crew
        self.validation_crew = validation_crew
        self.integration_crew = integration_crew


    # Mission analysis

    @start()
    def run_mission_analysis(self):
        print("Mission analysis")

        mission_report = self.state.get("mission_report")
        mars_graph = self.state.get("mars_graph")
        urls = self.state.get("urls")

        result = self.mission_crew.crew().kickoff(
            inputs={
                "mission_report": mission_report,
                "mars_graph": mars_graph,
                "urls": urls,
            }
        )

        self.state["mission"] = result
        self.state["retries"] = 0 

        return result


    # Utils
    def extract_json_object(self, text: str) -> dict:
        m = re.search(r"```json\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
        if m:
            return json.loads(m.group(1))

        m = re.search(r"(\{[\s\S]*\})", text)
        if not m:
            raise ValueError("No JSON object found")
        return json.loads(m.group(1))


    # Planning (parallel)
    @listen(or_(run_mission_analysis, "replan_rover"))
    def run_rover_planning(self):
        print("Rover planning")

        mars_graph = self.state.get("mars_graph")
        raw_text = Path("reporting_aggregation.md").read_text(encoding="utf-8", errors="ignore")
        mission_data = self.extract_json_object(raw_text)

        result = self.rover_crew.crew().kickoff(
            inputs={
                "mission_report": mission_data["rovers"],
                "mars_graph": mars_graph,
            }
        )

        self.state["rover_plan"] = result
        return "rover_ready"

    @listen(or_(run_mission_analysis, "replan_drone"))
    def run_drone_planning(self):
        print("Drone planning")

        mars_graph = self.state.get("mars_graph")
        raw_text = Path("reporting_aggregation.md").read_text(encoding="utf-8", errors="ignore")
        mission_data = self.extract_json_object(raw_text)

        result = self.drone_crew.crew().kickoff(
            inputs={
                "mission_report": mission_data["drones"],
                "mars_graph": mars_graph,
            }
        )

        self.state["drone_plan"] = result
        return "drone_ready"

    @listen(or_(run_mission_analysis, "replan_satellite"))
    def run_satellite_planning(self):
        print("Satellite planning")

        raw_text = Path("reporting_aggregation.md").read_text(encoding="utf-8", errors="ignore")
        mission_data = self.extract_json_object(raw_text)

        result = self.satellite_crew.crew().kickoff(
            inputs={"mission_report": mission_data["satellites"]}
        )

        self.state["satellite_plan"] = result
        return "satellite_ready"


    # Validation

    @listen(or_(run_rover_planning, run_drone_planning, run_satellite_planning))
    def validate_plans(self, _) -> ValidationResult:
        print("Integration Crew is validating individual routes...")
        if not all([self.state.get("rover_plan"), self.state.get("drone_plan"), self.state.get("satellite_plan")]):
            return
        # We call the validation_crew specifically for validation
        # Tip: You can use a specific task name if your crew has multiple tasks
        validation_output = self.validation_crew.crew().kickoff(
            inputs={
                "rover_plan": str(self.state.get("rover_plan")),
                "drone_plan": str(self.state.get("drone_plan")),
                "satellite_plan": str(self.state.get("satellite_plan")),
                "mars_graph": self.state.get("mars_graph"),
                "context": "VALIDATION_MODE" # Helper flag for your agents
            }
        )

        # Extract the JSON results from the validation agents
        try:
            res = self.extract_json_object(validation_output.raw)
            validation = ValidationResult(
                rover_ok=res.get("rover_ok", False),
                drone_ok=res.get("drone_ok", False),
                satellite_ok=res.get("satellite_ok", False)
            )
            # Store feedback in state so the replanning agents know what went wrong
            self.state["feedback"] = res.get("feedback", "No specific feedback provided.")
        except Exception as e:
            print(f"Validation parsing failed: {e}")
            # Default to False if parsing fails to force a retry
            validation = ValidationResult(rover_ok=False, drone_ok=False, satellite_ok=False)

        self.state["validation"] = validation
        return validation

    # Decision (router)
    @router(validate_plans)
    def decision(self, validation: ValidationResult):

        if validation.rover_ok and validation.drone_ok and validation.satellite_ok:
            print("All plans valid")
            return "integrate"

        self.state["retries"] = self.state.get("retries", 0) + 1
        print(f"Validation failed (attempt {self.state['retries']}/{self.MAX_RETRIES})")

        if self.state["retries"] >= self.MAX_RETRIES:
            raise RuntimeError("Too many replanning attempts")

        if not validation.rover_ok:
            return "replan_rover"
        if not validation.drone_ok:
            return "replan_drone"
        return "replan_satellite"

    # Integration

    @listen(decision)
    def integrate_plans(self, decision):
        if decision != "integrate":
            return

        print("Integrating plans")

        final = self.integration_crew.crew().kickoff(
            inputs={
                "rover_plan": str(self.state["rover_plan"]),
                "drone_plan": str(self.state["drone_plan"]),
                "satellite_plan": str(self.state["satellite_plan"]),
            }
        )

        self.state["final_plan"] = final
        return final



# Entry point

def kickoff():
    mission_report = Path("inputs/mission_report.md").read_text(encoding="utf-8")
    mars_graph = Path("inputs/mars_terrain_graph.graphml").read_text(encoding="utf-8")
    urls = ["https://science.nasa.gov/mars/facts/"]

    flow = MarsFlow(
        mission_crew=MissionCrew(),
        rover_crew=RoverCrew(),
        drone_crew=DronesCrew(),
        satellite_crew=SatelliteCrew(),
        validation_crew = ValidationCrew(),
        integration_crew=IntegrationCrew(),
    )

    flow.state["mission_report"] = mission_report
    flow.state["mars_graph"] = mars_graph
    flow.state["urls"] = urls

    result = flow.kickoff()

    print("\n=== FINAL MISSION PLAN ===\n")
    print(result)

    return result
def plot():
    flow = MarsFlow(
        mission_crew=MissionCrew(),
        rover_crew=RoverCrew(),
        drone_crew=DronesCrew(),
        satellite_crew=SatelliteCrew(),
        validation_crew = ValidationCrew(),
        integration_crew=IntegrationCrew())
    flow.plot()

if __name__ == "__main__":
    # kickoff()
    plot()