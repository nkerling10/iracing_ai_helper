"""
Massive credit to kutu for the pyirsdk linked below:
    https://github.com/kutu/pyirsdk/
"""

## Standard library imports
import logging
import time

## Local imports
from setup.race_setup import RaceManager
from setup.driver import Driver

from services.practice_service import PracticeService
from services.qualifying_service import QualifyingService
from services.race_service import RaceService
from services.points_calculator import PointsCalculator
from services.points_importer import PointsImporter

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(module)s [%(levelname)s] %(message)s",
    handlers=[
        # FileHandler(Path(os.getcwd()) / "logs" / "debug.log"),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(__name__)


def current_session_practice(race_manager, cars_to_dq):
    ## Regardless if a weekend actually has a practice session
    ## Execute the practice stage as long as the first session is not completed
    if race_manager.ir["SessionInfo"]["Sessions"][race_manager.practice_session_num][
        "ResultsOfficial"
    ] == 0 or (
        race_manager.practice_session_num is None
        and race_manager.ir["SessionInfo"]["Sessions"][
            race_manager.qualifying_session_num
        ]["ResultsOfficial"]
        == 0
    ):
        PracticeService.practice(race_manager, cars_to_dq)
        race_manager.practice_done = True
        logger.info("Practice operations are complete!")
    else:
        logger.debug("Practice stage does not need to be executed, skipping")
        race_manager.practice_done = True


def current_session_qualify(race_manager):
    ## Perform the qualifying session operations
    ## Execute the operations as long as the session has not been completed
    if race_manager.ir["SessionInfo"]["Sessions"][race_manager.qualifying_session_num][
        "ResultsOfficial"
    ] == 0 or (
        race_manager.qualifying_session_num is None
        and race_manager.ir["SessionInfo"]["Sessions"][race_manager.race_session_num][
            "ResultsOfficial"
        ]
        == 0
    ):
        QualifyingService.qualifying(race_manager)
        race_manager.qualifying_done = True
        logger.info("Qualifying operations are complete!")
    else:
        logger.debug("Qualifying stage does not need to be executed, skipping")
        race_manager.qualifying_done = True


def current_session_race(race_manager):
    if (
        race_manager.qualifying_session_num is None
        or race_manager.ir["SessionInfo"]["Sessions"][
            race_manager.qualifying_session_num
        ]["ResultsOfficial"]
        == 1
    ):
        RaceService.race(race_manager)
        return


def set_drivers(race_manager):
    cars_to_dq = []
    for driver in race_manager.ir["DriverInfo"]["Drivers"]:
        if driver["CarIsPaceCar"] == 0:
            if "NODRIVER" not in driver["UserName"]:
                race_manager.race_weekend.drivers.append(
                    Driver(
                        name=driver["UserName"],
                        car=driver["CarNumber"],
                        team="Kerling Motorsports" if driver["CarNumber"] == race_manager.race_weekend.race_data.player_car_num[0] else
                            [car[1] for car in race_manager.season_data.cars_teams if car[0] == driver["CarNumber"]][0],
                        points_eligibile=(
                            True
                            if driver["UserName"]
                            in race_manager.season_data.declared_points
                            or driver["CarIsAI"] == 0
                            else False
                        ),
                    )
                )
            else:
                cars_to_dq.append(driver["CarNumber"])
    return cars_to_dq


def loop(race_manager, cars_to_dq):
    while True:
        ## Figure out what session is currently active
        ## This will prove useful if the app crashes during any session
        _current_session_num, current_session_name = (
            race_manager._get_current_sessions()
        )
        if current_session_name == "PRACTICE" and race_manager.practice_done is False:
            current_session_practice(race_manager, cars_to_dq)
        elif (
            current_session_name in ["QUALIFYING", "QUALIFY"]
            and race_manager.qualifying_done is False
        ):
            current_session_qualify(race_manager)
        elif current_session_name == "RACE":
            current_session_race(race_manager)
        else:
            time.sleep(1)


def main():
    race_manager = RaceManager(test_file=True)
    race_manager.race_weekend.race_results = race_manager.ir["SessionInfo"]["Sessions"][0]["ResultsPositions"]
    
    race_manager.race_weekend.stage_results[0].stage_results = ["Austin Hill",
                                                                "Justin Allgaier",
                                                                "Harrison Burton",
                                                                "Sammy Smith",
                                                                "Brandon Jones",
                                                                "Daniel Dye",
                                                                "William Sawalich",
                                                                "Jesse Love",
                                                                "Sheldon Creed",
                                                                "Christian Eckes"]
    race_manager.race_weekend.stage_results[1].stage_results = ["Austin Hill",
                                                                "Justin Allgaier",
                                                                "Sammy Smith",
                                                                "Brandon Jones",
                                                                "Sheldon Creed",
                                                                "Harrison Burton",
                                                                "Daniel Dye",
                                                                "William Sawalich",
                                                                "Jesse Love",
                                                                "Christian Eckes"]
    cars_to_dq = set_drivers(race_manager)
    """
    loop(race_manager, cars_to_dq)
    """
    PointsCalculator.main(race_manager)
    PointsImporter(race_manager)


if __name__ == "__main__":
    main()
