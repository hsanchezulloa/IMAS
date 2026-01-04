from pydantic import BaseModel
from pathlib import Path
import json
import re

from crewai.flow import Flow, start, listen, and_, or_, router
from crews.mission_crew.mission_crew import MissionCrew
from crews.rover_crew.rover_crew import RoverCrew
from crews.drone_crew.drone_crew import DronesCrew
from crews.satellite_crew.satellite_crew import SatelliteCrew
from crews.integration_crew.integration_crew import IntegrationCrew


class ValidationResult(BaseModel):
    rover_ok: bool
    drone_ok: bool
    satellite_ok: bool

class MarsFlow(Flow):
    MAX_RETRIES = 3

    def __init__(self, mission_crew, rover_crew, drone_crew, satellite_crew, integration_crew):
        super().__init__()
        self.mission_crew = mission_crew
        self.rover_crew = rover_crew
        self.drone_crew = drone_crew
        self.satellite_crew = satellite_crew
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
        self.state["retries"] = 0  # ✅ reset retries once

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
    @listen(run_mission_analysis)
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
        return result

    @listen(run_mission_analysis)
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
        return result

    @listen(run_mission_analysis)
    def run_satellite_planning(self):
        print("Satellite planning")

        raw_text = Path("reporting_aggregation.md").read_text(encoding="utf-8", errors="ignore")
        mission_data = self.extract_json_object(raw_text)

        result = self.satellite_crew.crew().kickoff(
            inputs={"mission_report": mission_data["satellites"]}
        )

        self.state["satellite_plan"] = result
        return result

    # =========================
    # Validation

    @listen(or_(and_(run_rover_planning, run_drone_planning, run_satellite_planning),"revalidate"))
    def validate_plans(self, _) -> ValidationResult:
        print("Validating plans")

        rover_ok = len(str(self.state.get("rover_plan", ""))) > 20
        drone_ok = len(str(self.state.get("drone_plan", ""))) > 20
        satellite_ok = len(str(self.state.get("satellite_plan", ""))) > 20

        validation = ValidationResult(
            rover_ok=rover_ok,
            drone_ok=drone_ok,
            satellite_ok=satellite_ok,
        )

        self.state["validation"] = validation
        return validation


    # Decision (router)
    @router(validate_plans)
    def decision(self, validation: ValidationResult):

        if validation.rover_ok and validation.drone_ok and validation.satellite_ok:
            print("All plans valid")
            return "integrate"

        self.state["retries"] += 1
        print(f"Validation failed (attempt {self.state['retries']}/{self.MAX_RETRIES})")

        if self.state["retries"] >= self.MAX_RETRIES:
            raise RuntimeError("Too many replanning attempts")

        if not validation.rover_ok:
            return "replan_rover"
        if not validation.drone_ok:
            return "replan_drone"
        return "replan_satellite"


    # Replanning
    @listen("replan_rover")
    def retry_rover(self, _):
        print("Replanning rover")
        return self.run_rover_planning()

    @listen("replan_drone")
    def retry_drone(self, _):
        print("Replanning drone")
        return self.run_drone_planning()

    @listen("replan_satellite")
    def retry_satellite(self, _):
        print("Replanning satellite")
        return self.run_satellite_planning()

    # Validation again
    @listen(or_("replan_rover", "replan_drone", "replan_satellite"))
    def revalidate(self, _):
        return "revalidate"



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
        integration_crew=IntegrationCrew(),
    )

    flow.state["mission_report"] = mission_report
    flow.state["mars_graph"] = mars_graph
    flow.state["urls"] = urls

    result = flow.kickoff()

    print("\n=== FINAL MISSION PLAN ===\n")
    print(result)

    return result


if __name__ == "__main__":
    kickoff()
