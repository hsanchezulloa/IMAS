from pydantic import BaseModel
from pathlib import Path
import json
import re
from crewai.flow import Flow, start, listen, or_, router

from crews.mission_crew.mission_crew import MissionCrew
from crews.rover_crew.rover_crew import RoverCrew
from crews.drone_crew.drone_crew import DronesCrew
from crews.satellite_crew.satellite_crew import SatelliteCrew
from crews.validation_crew.validation_crew import ValidationCrew
from crews.integration_crew.integration_crew import IntegrationCrew, FinalMissionReport
from rendering import to_markdown


class ValidationResult(BaseModel):
    rover_ok: bool
    drone_ok: bool
    satellite_ok: bool


class MarsFlow(Flow):
    MAX_RETRIES = 3

    def __init__(
        self,
        mission_crew,
        rover_crew,
        drone_crew,
        satellite_crew,
        validation_crew,
        integration_crew,
    ):
        super().__init__()
        self.mission_crew = mission_crew
        self.rover_crew = rover_crew
        self.drone_crew = drone_crew
        self.satellite_crew = satellite_crew
        self.validation_crew = validation_crew
        self.integration_crew = integration_crew

    # Utils
    def extract_json_object(self, text: str) -> dict:
        m = re.search(r"```json\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
        if m:
            return json.loads(m.group(1))
        m = re.search(r"(\{[\s\S]*\})", text)
        if not m:
            raise ValueError("No JSON object found")
        return json.loads(m.group(1))

    # Mission crew
    @start()
    def run_mission_analysis(self):
        print("Mission analysis")
        mission_report = self.state.get("mission_report")
        result = self.mission_crew.crew().kickoff(inputs={"mission_report": mission_report})
        self.state["mission"] = result

        # init state
        self.state["retries"] = 0
        self.state["validating"] = False

        # IMPORTANT: clear plans at start
        self.state["rover_plan"] = None
        self.state["drone_plan"] = None
        self.state["satellite_plan"] = None

        # trigger initial planning explicitly
    
    @listen(run_mission_analysis)
    def kickoff_planning(self, _):
        return "plan_all"

    # ---------- PLANNERS ----------
    @listen(or_("plan_all", "replan_rover"))
    def run_rover_planning(self, trigger=None):
        # Only run on initial plan_all or rover replan
        if trigger not in ("plan_all", "replan_rover"):
            return
        print("Rover planning")

        report_priority = self.extract_json_object(
            Path("report_priority.json").read_text(encoding="utf-8")
        )
        rovers = self.state.get("rovers")
        hazards = self.state.get("hazards")

        result = self.rover_crew.crew().kickoff(
            inputs={"report_priority": report_priority, "rovers": rovers, "hazards": hazards}
        )
        self.state["rover_plan"] = result
        return "rover_ready"

    @listen(or_("plan_all", "replan_drone"))
    def run_drone_planning(self, trigger=None):
        if trigger not in ("plan_all", "replan_drone"):
            return
        print("Drone planning")

        report_priority = self.extract_json_object(
            Path("report_priority.json").read_text(encoding="utf-8")
        )
        drones = self.state.get("drones")
        hazards = self.state.get("hazards")

        result = self.drone_crew.crew().kickoff(
            inputs={"report_priority": report_priority, "drones": drones, "hazards": hazards}
        )
        self.state["drone_plan"] = result
        return "drone_ready"

    @listen(or_("plan_all", "replan_satellite"))
    def run_satellite_planning(self, trigger=None):
        if trigger not in ("plan_all", "replan_satellite"):
            return
        print("Satellite planning")

        report_priority = self.extract_json_object(
            Path("report_priority.json").read_text(encoding="utf-8")
        )
        report_hazard_constraints = self.extract_json_object(
            Path("report_hazard_constraints.json").read_text(encoding="utf-8")
        )
        satellite_json = self.state.get("satellite_json")

        result = self.satellite_crew.crew().kickoff(
            inputs={
                "report_priority": report_priority,
                "satellite_json": satellite_json,
                "report_hazard_constraints": report_hazard_constraints,
            }
        )
        self.state["satellite_plan"] = result
        return "satellite_ready"

    # ---------- VALIDATION ----------
    # Only validate when a planner FINISHES (prevents "Waiting..." loops)
    @listen(or_("rover_ready", "drone_ready", "satellite_ready"))
    def validate_plans(self, _):
        # anti-duplicate
        if self.state.get("validating"):
            print("Validation already running, skipping duplicate call")
            return None

        # only validate when all plans exist
        if not all(
            [
                self.state.get("rover_plan"),
                self.state.get("drone_plan"),
                self.state.get("satellite_plan"),
            ]
        ):
            print("Waiting for all plans...")
            return None

        self.state["validating"] = True
        try:
            print("Integration Crew is validating individual routes...")

            reporting_aggregation = self.extract_json_object(
                Path("reporting_aggregation.json").read_text(encoding="utf-8")
            )
            routes_satellite = self.extract_json_object(
                Path("routes_satellite.json").read_text(encoding="utf-8")
            )
            routes_drone = self.extract_json_object(
                Path("routes_drone.json").read_text(encoding="utf-8")
            )
            routes_rover = self.extract_json_object(
                Path("routes_rover.json").read_text(encoding="utf-8")
            )
            hazards = self.state.get("hazards")

            validation_output = self.validation_crew.crew().kickoff(
                inputs={
                    "reporting_aggregation": reporting_aggregation,
                    "routes_rover": routes_rover,
                    "routes_satellite": routes_satellite,
                    "routes_drone": routes_drone,
                    "hazards": hazards,
                }
            )

            try:
                res = self.extract_json_object(validation_output.raw)
                validation = ValidationResult(
                    rover_ok=res.get("rover_ok", False),
                    drone_ok=res.get("drone_ok", False),
                    satellite_ok=res.get("satellite_ok", False),
                )
                self.state["feedback"] = res.get("feedback", "No specific feedback provided.")
            except Exception as e:
                print(f"Validation parsing failed: {e}")
                validation = ValidationResult(rover_ok=False, drone_ok=False, satellite_ok=False)

            self.state["validation"] = validation
            return validation
        finally:
            self.state["validating"] = False

    # ---------- DECISION ----------
    @router(validate_plans)
    def decision(self, validation):
        # If validation didn't run yet (missing plans), do nothing.
        if validation is None:
            return None

        if validation.rover_ok and validation.drone_ok and validation.satellite_ok:
            print("All plans valid")
            return "integrate"

        self.state["retries"] = self.state.get("retries", 0) + 1
        print(f"Validation failed (attempt {self.state['retries']}/{self.MAX_RETRIES})")

        if self.state["retries"] >= self.MAX_RETRIES:
            raise RuntimeError("Too many replanning attempts")

        # clear only the failing plan and trigger correct replan event
        if not validation.rover_ok:
            self.state["rover_plan"] = None
            return "replan_rover"

        if not validation.drone_ok:
            self.state["drone_plan"] = None
            return "replan_drone"

        self.state["satellite_plan"] = None
        return "replan_satellite"

    # ---------- INTEGRATION ----------
    @listen(decision)
    def integrate_plans(self, decision_value):
        if decision_value != "integrate":
            return

        sample_collector_rover = Path("sample_collector_rover.md").read_text(encoding="utf-8")
        routes_rover = self.extract_json_object(Path("routes_rover.json").read_text(encoding="utf-8"))

        sample_collector_drone = Path("sample_collector_drone.md").read_text(encoding="utf-8")
        routes_drone = self.extract_json_object(Path("routes_drone.json").read_text(encoding="utf-8"))

        sample_collector_satellite = Path("image_capture_satellite.md").read_text(encoding="utf-8")
        routes_satellite = self.extract_json_object(Path("routes_satellite.json").read_text(encoding="utf-8"))

        print("Integrating plans")
        final = self.integration_crew.crew().kickoff(
            inputs={
                "sample_collector_rover": sample_collector_rover,
                "routes_rover": routes_rover,
                "sample_collector_drone": sample_collector_drone,
                "routes_drone": routes_drone,
                "sample_collector_satellite": sample_collector_satellite,
                "routes_satellite": routes_satellite,
            }
        )

        self.state["final_plan"] = final

        raw_output = final.raw if hasattr(final, "raw") else final
        parsed = self.extract_json_object(raw_output)
        report = FinalMissionReport(**parsed)

        markdown = to_markdown(report)
        with open("final_mission_report.md", "w", encoding="utf-8") as f:
            f.write(markdown)

        return markdown


# Entry point
def kickoff():
    mission_report = Path("inputs/mission_report.md").read_text(encoding="utf-8")
    rovers = Path("inputs/rovers.json").read_text(encoding="utf-8")
    drones = Path("inputs/drones.json").read_text(encoding="utf-8")
    satellite_json = Path("inputs/satellites.json").read_text(encoding="utf-8")

    flow = MarsFlow(
        mission_crew=MissionCrew(),
        rover_crew=RoverCrew(),
        drone_crew=DronesCrew(),
        satellite_crew=SatelliteCrew(),
        validation_crew=ValidationCrew(),
        integration_crew=IntegrationCrew(),
    )
    flow.state["mission_report"] = mission_report
    flow.state["rovers"] = rovers
    flow.state["drones"] = drones
    flow.state["satellite_json"] = satellite_json
    flow.state["hazards"] = False

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
        validation_crew=ValidationCrew(),
        integration_crew=IntegrationCrew(),
    )
    flow.plot()


if __name__ == "__main__":
    kickoff()
    # plot()
