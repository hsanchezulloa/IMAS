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
from crews.integration_crew.integration_crew import IntegrationCrew, FinalMissionReport
from rendering import to_markdown


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


    # Mission crew
    @start()
    def run_mission_analysis(self):
        print("Mission analysis")
        mission_report = self.state.get("mission_report")
        result = self.mission_crew.crew().kickoff(inputs={"mission_report": mission_report,})
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
    # Rover crew
    @listen(or_(run_mission_analysis, "replan_rover"))
    def run_rover_planning(self):
        print("Rover planning")
        report_priority = self.extract_json_object(Path("report_priority.json").read_text(encoding="utf-8"))
        rovers = self.state.get("rovers")
        hazards = self.state.get("hazards")
        result = self.rover_crew.crew().kickoff(inputs={"report_priority": report_priority, "rovers": rovers, "hazards": hazards})
        self.state["rover_plan"] = result
        return "rover_ready"

    # Drone crew
    @listen(or_(run_mission_analysis, "replan_drone"))
    def run_drone_planning(self):
        print("Drone planning")
        report_priority = self.extract_json_object(Path("report_priority.json").read_text(encoding="utf-8"))
        drones = self.state.get("drones")
        hazards = self.state.get("hazards")
        result = self.drone_crew.crew().kickoff(inputs={"report_priority": report_priority, "drones": drones, "hazards": hazards})
        self.state["drone_plan"] = result
        return "drone_ready"

    # Satellite crew
    @listen(or_(run_mission_analysis, "replan_satellite"))
    def run_satellite_planning(self):
        print("Satellite planning")
        report_priority = self.extract_json_object(Path("report_priority.json").read_text(encoding="utf-8"))
        report_hazard_constraints = self.extract_json_object(Path("report_hazard_constraints.json").read_text(encoding="utf-8"))
        satellite_json = self.state.get("satellite_json")
        result = self.satellite_crew.crew().kickoff(inputs={"report_priority": report_priority, "satellite_json": satellite_json, 'report_hazard_constraints': report_hazard_constraints})

        self.state["satellite_plan"] = result
        return "satellite_ready"

    # Validation
    # @listen(or_(and_(run_rover_planning, run_drone_planning, run_satellite_planning), and_("replan_rover", run_rover_planning), and_("replan_drone", run_drone_planning), and_("replan_satellite", run_satellite_planning)))
    @listen(or_(
    and_(run_rover_planning, run_drone_planning, run_satellite_planning),
    run_rover_planning,
    run_drone_planning,
    run_satellite_planning
))

    def validate_plans(self, _) -> ValidationResult:
        print("Integration Crew is validating individual routes...")
        # if not all([self.state.get("rover_plan"), self.state.get("drone_plan"), self.state.get("satellite_plan")]):
        #     return
        # We call the validation_crew specifically for validation
        if self.state.get("validating"):
            print("Validation already running, skipping duplicate call")
            return

        self.state["validating"] = True
        if not all([
            self.state.get("rover_plan"),
            self.state.get("drone_plan"),
            self.state.get("satellite_plan")
        ]):
            print("Waiting for all plans...")
            self.state["validating"] = False
            return

        reporting_aggregation = self.extract_json_object(Path("reporting_aggregation.json").read_text(encoding="utf-8"))
        routes_satellite = self.extract_json_object(Path("routes_satellite.json").read_text(encoding="utf-8"))
        routes_drone = self.extract_json_object(Path("routes_drone.json").read_text(encoding="utf-8"))
        routes_rover = self.extract_json_object(Path("routes_rover.json").read_text(encoding="utf-8"))
        hazards = self.state.get("hazards")
        validation_output = self.validation_crew.crew().kickoff(inputs={"reporting_aggregation": reporting_aggregation, "routes_rover": routes_rover, "routes_satellite": routes_satellite, "routes_drone": routes_drone, "hazards": hazards})

        # Extract the JSON results from the validation agents
        try:
            res = self.extract_json_object(validation_output.raw)
            validation = ValidationResult(rover_ok=res.get("rover_ok", False), drone_ok=res.get("drone_ok", False), satellite_ok=res.get("satellite_ok", False))
            # Store feedback in state so the replanning agents know what went wrong
            self.state["feedback"] = res.get("feedback", "No specific feedback provided.")
        except Exception as e:
            print(f"Validation parsing failed: {e}")
            # Default to False if parsing fails to force a retry
            validation = ValidationResult(rover_ok=False, drone_ok=False, satellite_ok=False)
        self.state["validation"] = validation
        self.state["validating"] = False
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

        # if not validation.rover_ok:
        #     return "replan_rover"
        # if not validation.drone_ok:
        #     return "replan_drone"
        # return "replan_satellite"
        if not validation.rover_ok:
            self.state["rover_plan"] = None
            return "replan_rover"

        if not validation.drone_ok:
            self.state["drone_plan"] = None
            return "replan_drone"

        self.state["satellite_plan"] = None
        return "replan_satellite"

    
    # Integration
    @listen(decision)
    def integrate_plans(self, decision):
        if decision != "integrate":
            return
        sample_collector_rover = Path("sample_collector_rover.md").read_text(encoding="utf-8")
        routes_rover = self.extract_json_object(Path("routes_rover.json").read_text(encoding="utf-8"))
        sample_collector_drone = Path("sample_collector_drone.md").read_text(encoding="utf-8")
        routes_drone = self.extract_json_object(Path("routes_drone.json").read_text(encoding="utf-8"))
        sample_collector_satellite = Path("image_capture_satellite.md").read_text(encoding="utf-8")
        routes_satellite = self.extract_json_object(Path("routes_satellite.json").read_text(encoding="utf-8"))
        print("Integrating plans")
        final = self.integration_crew.crew().kickoff(inputs={"sample_collector_rover": sample_collector_rover, "routes_rover": routes_rover, "sample_collector_drone": sample_collector_drone, "routes_drone": routes_drone, "sample_collector_satellite":sample_collector_satellite, "routes_satellite":routes_satellite})
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
    
    flow = MarsFlow(mission_crew = MissionCrew(), rover_crew = RoverCrew(), drone_crew = DronesCrew(), satellite_crew = SatelliteCrew(), validation_crew = ValidationCrew(), integration_crew = IntegrationCrew(),)
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
        validation_crew = ValidationCrew(),
        integration_crew=IntegrationCrew())
    flow.plot()


if __name__ == "__main__":
    kickoff()
    # plot()


from pydantic import BaseModel
from pathlib import Path
import json
import re
from crewai.flow import Flow, start, listen, router

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

    # ---------- START ----------
    @start()
    def run_mission_analysis(self):
        print("Mission analysis")

        mission_report = self.state.get("mission_report")
        result = self.mission_crew.crew().kickoff(
            inputs={"mission_report": mission_report}
        )

        self.state["mission"] = result
        self.state["retries"] = 0
        self.state["validating"] = False

        self.state["rover_plan"] = None
        self.state["drone_plan"] = None
        self.state["satellite_plan"] = None

        return result

    # ---------- PLANNERS ----------

    @listen(run_mission_analysis)
    def run_rover_planning(self, _):
        print("Rover planning")

        report_priority = self.extract_json_object(
            Path("report_priority.json").read_text()
        )
        rovers = self.state.get("rovers")
        hazards = self.state.get("hazards")

        result = self.rover_crew.crew().kickoff(
            inputs={
                "report_priority": report_priority,
                "rovers": rovers,
                "hazards": hazards,
            }
        )

        self.state["rover_plan"] = result
        return result

    @listen(run_mission_analysis)
    def run_drone_planning(self, _):
        print("Drone planning")

        report_priority = self.extract_json_object(
            Path("report_priority.json").read_text()
        )
        drones = self.state.get("drones")
        hazards = self.state.get("hazards")

        result = self.drone_crew.crew().kickoff(
            inputs={
                "report_priority": report_priority,
                "drones": drones,
                "hazards": hazards,
            }
        )

        self.state["drone_plan"] = result
        return result

    @listen(run_mission_analysis)
    def run_satellite_planning(self, _):
        print("Satellite planning")

        report_priority = self.extract_json_object(
            Path("report_priority.json").read_text()
        )
        report_hazard_constraints = self.extract_json_object(
            Path("report_hazard_constraints.json").read_text()
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
        return result

    # ---------- VALIDATION ----------

    @listen(run_rover_planning)
    @listen(run_drone_planning)
    @listen(run_satellite_planning)
    def validate_plans(self, _):

        if self.state.get("validating"):
            return

        if not all(
            [
                self.state.get("rover_plan"),
                self.state.get("drone_plan"),
                self.state.get("satellite_plan"),
            ]
        ):
            print("Waiting for all plans...")
            return

        self.state["validating"] = True

        try:
            print("Validating routes...")

            reporting_aggregation = self.extract_json_object(
                Path("reporting_aggregation.json").read_text()
            )
            routes_satellite = self.extract_json_object(
                Path("routes_satellite.json").read_text()
            )
            routes_drone = self.extract_json_object(
                Path("routes_drone.json").read_text()
            )
            routes_rover = self.extract_json_object(
                Path("routes_rover.json").read_text()
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

            res = self.extract_json_object(validation_output.raw)

            validation = ValidationResult(
                rover_ok=res.get("rover_ok", False),
                drone_ok=res.get("drone_ok", False),
                satellite_ok=res.get("satellite_ok", False),
            )

            self.state["feedback"] = res.get("feedback", "")
            self.state["validation"] = validation
            return validation

        finally:
            self.state["validating"] = False

    # ---------- DECISION ----------

    @router(validate_plans)
    def decision(self, validation):

        if validation is None:
            return

        if (
            validation.rover_ok
            and validation.drone_ok
            and validation.satellite_ok
        ):
            return "integrate"

        self.state["retries"] += 1

        if self.state["retries"] >= self.MAX_RETRIES:
            raise RuntimeError("Too many retries")

        if not validation.rover_ok:
            self.state["rover_plan"] = None
            return self.run_rover_planning

        if not validation.drone_ok:
            self.state["drone_plan"] = None
            return self.run_drone_planning

        self.state["satellite_plan"] = None
        return self.run_satellite_planning

    # ---------- INTEGRATION ----------

    @listen(decision)
    def integrate_plans(self, decision_value):

        if decision_value != "integrate":
            return

        print("Integrating final mission")

        sample_collector_rover = Path(
            "sample_collector_rover.md"
        ).read_text()
        routes_rover = self.extract_json_object(
            Path("routes_rover.json").read_text()
        )

        sample_collector_drone = Path(
            "sample_collector_drone.md"
        ).read_text()
        routes_drone = self.extract_json_object(
            Path("routes_drone.json").read_text()
        )

        sample_collector_satellite = Path(
            "image_capture_satellite.md"
        ).read_text()
        routes_satellite = self.extract_json_object(
            Path("routes_satellite.json").read_text()
        )

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

        raw = final.raw if hasattr(final, "raw") else final
        parsed = self.extract_json_object(raw)
        report = FinalMissionReport(**parsed)

        markdown = to_markdown(report)
        Path("final_mission_report.md").write_text(markdown)

        return markdown


# ---------- ENTRY ----------

def kickoff():
    flow = MarsFlow(
        mission_crew=MissionCrew(),
        rover_crew=RoverCrew(),
        drone_crew=DronesCrew(),
        satellite_crew=SatelliteCrew(),
        validation_crew=ValidationCrew(),
        integration_crew=IntegrationCrew(),
    )

    flow.state["mission_report"] = Path(
        "inputs/mission_report.md"
    ).read_text()
    flow.state["rovers"] = Path(
        "inputs/rovers.json"
    ).read_text()
    flow.state["drones"] = Path(
        "inputs/drones.json"
    ).read_text()
    flow.state["satellite_json"] = Path(
        "inputs/satellites.json"
    ).read_text()
    flow.state["hazards"] = False

    result = flow.kickoff()
    print("\n=== FINAL PLAN ===\n", result)


if __name__ == "__main__":
    kickoff()
