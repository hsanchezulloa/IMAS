#!/usr/bin/env python
from random import randint

from pydantic import BaseModel

from crewai.flow import Flow, listen, start, and_


# from IMAS.mars_explorer.src.mars_explorer.crews.drone_crew import DronesCrew
# from IMAS.mars_explorer.src.mars_explorer.crews.integration_crew import IntegrationCrew
# from IMAS.mars_explorer.src.mars_explorer.crews.mission_crew import MissionCrew
# from IMAS.mars_explorer.src.mars_explorer.crews.rover_crew import RoverCrew
# from IMAS.mars_explorer.src.mars_explorer.crews.satellite_crew import SatelliteCrew

from crews.drone_crew.drone_crew import DronesCrew
from crews.integration_crew.integration_crew import IntegrationCrew
from crews.mission_crew.mission_crew import MissionCrew
from crews.rover_crew.rover_crew import RoverCrew
from crews.satellite_crew.satellite_crew import SatelliteCrew

class MarsFlow(Flow):
    """
    Global orchestration flow for the Mars multi-agent mission.
    """

    def __init__(
        self,
        mission_crew,
        rover_crew,
        drone_crew,
        satellite_crew,
        integration_crew,
    ):
        super().__init__()
        self.mission_crew = mission_crew
        self.rover_crew = rover_crew
        self.drone_crew = drone_crew
        self.satellite_crew = satellite_crew
        self.integration_crew = integration_crew

        # self.state = {}

    # --------------------------------------------------
    # 1. Mission analysis & aggregation
    # --------------------------------------------------
    @start()
    def run_mission_analysis(self, mission_report: str):
        """
        INPUT:
        - mission_report (raw external mission description)

        OUTPUT:
        - processed_mission_crew = {
                "rovers": ...,
                "drones": ...,
                "satellites": ...
            }
        """
        print("[Flow] Running Mission Crew")

        processed_mission_crew = self.mission_crew.crew().kickoff(
            inputs={"mission_report": mission_report}
        )

        self.state["processed_mission_crew"] = processed_mission_crew
        return processed_mission_crew

    # --------------------------------------------------
    # 2. Rover planning
    # --------------------------------------------------
    @listen(run_mission_analysis)
    def run_rover_planning(self, processed_mission_crew):
        print("[Flow] Running Rover Crew")

        rover_report = processed_mission_crew["rovers"]

        rover_result = self.rover_crew.crew().kickoff(
            inputs={"mission_report": rover_report}
        )

        self.state["rover_plan"] = rover_result
        return rover_result

    # --------------------------------------------------
    # 3. Drone planning
    # --------------------------------------------------
    @listen(run_mission_analysis)
    def run_drone_planning(self, processed_mission_crew):
        print("[Flow] Running Drone Crew")

        drone_report = processed_mission_crew["drones"]

        drone_result = self.drone_crew.crew().kickoff(
            inputs={"mission_report": drone_report}
        )

        self.state["drone_plan"] = drone_result
        return drone_result

    # --------------------------------------------------
    # 4. Satellite planning
    # --------------------------------------------------
    @listen(run_mission_analysis)
    def run_satellite_planning(self, processed_mission_crew):
        print("[Flow] Running Satellite Crew")

        satellite_report = processed_mission_crew["satellites"]

        satellite_result = self.satellite_crew.crew().kickoff(
            inputs={"mission_report": satellite_report}
        )

        self.state["satellite_plan"] = satellite_result
        return satellite_result
    # --------------------------------------------------
    # 5. Integration & conflict resolution
    # --------------------------------------------------
    @listen(and_(run_rover_planning, run_drone_planning, run_satellite_planning))
    def integrate_plans(self, _):
        print("[Flow] Integrating all plans")

        final_plan = self.integration_crew.crew().kickoff(
            inputs={
                "rover_plan": self.state["rover_plan"],
                "drone_plan": self.state["drone_plan"],
                "satellite_plan": self.state["satellite_plan"],
            }
        )

        self.state["final_plan"] = final_plan
        return final_plan




def kickoff(mission_report):
    mars_flow = MarsFlow(
        mission_crew=MissionCrew(),
        rover_crew=RoverCrew(),
        drone_crew=DronesCrew(),
        satellite_crew=SatelliteCrew(),
        integration_crew=IntegrationCrew(),
    )
    final_plan = mars_flow.kickoff(inputs={"mission_report": mission_report})


def plot():
    mars_flow = MarsFlow(
        mission_crew=MissionCrew(),
        rover_crew=RoverCrew(),
        drone_crew=DronesCrew(),
        satellite_crew=SatelliteCrew(),
        integration_crew=IntegrationCrew(),
    )
    mars_flow.plot()


if __name__ == "__main__":
    plot()
