from pydantic import BaseModel
from crewai.flow import Flow, start, listen, and_
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
    MAX_RETRIES = 2
    def __init__(self,
        mission_crew,
        rover_crew,
        drone_crew,
        satellite_crew,
        integration_crew,):
        super().__init__()
        self.mission_crew = mission_crew
        self.rover_crew = rover_crew
        self.drone_crew = drone_crew
        self.satellite_crew = satellite_crew
        self.integration_crew = integration_crew
    #mission analysis
    @start()
    def run_mission_analysis(self, mission_report: str):
        print("Mission analysis")
        result = self.mission_crew.crew().kickoff(inputs={"mission_report": mission_report})
        self.state["mission"] = result
        self.state["retries"] = 0
        return result
    
    #planning (parallel)
    @listen(run_mission_analysis)
    def run_rover_planning(self, mission):
        print("Rover planning")
        result = self.rover_crew.crew().kickoff(inputs={"mission_report": mission["rovers"]})
        self.state["rover_plan"] = result
        return result

    @listen(run_mission_analysis)
    def run_drone_planning(self, mission):
        print("Drone planning")
        result = self.drone_crew.crew().kickoff(inputs={"mission_report": mission["drones"]})
        self.state["drone_plan"] = result
        return result

    @listen(run_mission_analysis)
    def run_satellite_planning(self, mission):
        print("Satellite planning")
        result = self.satellite_crew.crew().kickoff(inputs={"mission_report": mission["satellites"]})
        self.state["satellite_plan"] = result
        return result

    #valiadation (and)
    @listen(and_(run_rover_planning,run_drone_planning,run_satellite_planning))
    def validate_plans(self, _) -> ValidationResult:
        print("Validating plans")
        rover_ok = len(self.state["rover_plan"]) > 20
        drone_ok = len(self.state["drone_plan"]) > 20
        satellite_ok = len(self.state["satellite_plan"]) > 20
        validation = ValidationResult(
            rover_ok=rover_ok,
            drone_ok=drone_ok,
            satellite_ok=satellite_ok)
        self.state["validation"] = validation
        return validation

    #decision: loop o integrar
    @listen(validate_plans)
    def decision(self, validation: ValidationResult):
        if (
            validation.rover_ok
            and validation.drone_ok
            and validation.satellite_ok):
            print("All plans valid")
            return "integrate"

        self.state["retries"] += 1
        print(f"Validation failed - retry {self.state['retries']}")

        if self.state["retries"] >= self.MAX_RETRIES:
            raise RuntimeError("Too many replanning attempts")
        return "replan"

    #replan (loop)
    @listen(decision)
    def replan(self, decision):
        if decision != "replan":
            return

        print("Replanning all crews")
        return self.run_mission_analysis(self.state["mission"])

    #integration
    @listen(decision)
    def integrate_plans(self, decision):
        if decision != "integrate":
            return
        print("[Flow] Integrating plans")

        final = self.integration_crew.crew().kickoff(
            inputs={
                "rover_plan": self.state["rover_plan"],
                "drone_plan": self.state["drone_plan"],
                "satellite_plan": self.state["satellite_plan"],
            }
        )
        self.state["final_plan"] = final
        return final

def kickoff(mission_report: str):
    flow = MarsFlow(
        mission_crew=MissionCrew(),
        rover_crew=RoverCrew(),
        drone_crew=DronesCrew(),
        satellite_crew=SatelliteCrew(),
        integration_crew=IntegrationCrew())
    return flow.kickoff(inputs={"mission_report": mission_report})


def plot():
    flow = MarsFlow(
        mission_crew=MissionCrew(),
        rover_crew=RoverCrew(),
        drone_crew=DronesCrew(),
        satellite_crew=SatelliteCrew(),
        integration_crew=IntegrationCrew())
    flow.plot()


if __name__ == "__main__":
    plot()
