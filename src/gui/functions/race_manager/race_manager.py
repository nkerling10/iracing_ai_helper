"""
Massive credit to kutu for the pyirsdk linked below:
    https://github.com/kutu/pyirsdk/
"""

## Standard library imports
import logging
import time

## Third party imports
import irsdk

## Local imports
from setup.race_setup import RaceManager
from setup.driver import Driver

from services.practice_service import PracticeService
from services.qualifying_service import QualifyingService
from services.race_service import RaceService
from services.points_calculator import PointsCalculator
from services.points_importer import PointsImporter
from services.post_race_penalties import PostRacePenalties

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
        irsdk.IRSDK.parse_to(
            race_manager.ir,
            to_file="C:/Users/Nick/Documents/iracing_ai_helper/session_data/practice_logic_start.bin",
        )
        PracticeService.practice(race_manager, cars_to_dq)
        race_manager.practice_done = True
        irsdk.IRSDK.parse_to(
            race_manager.ir,
            to_file="C:/Users/Nick/Documents/iracing_ai_helper/session_data/practice_logic_complete.bin",
        )
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
        irsdk.IRSDK.parse_to(
            race_manager.ir,
            to_file="C:/Users/Nick/Documents/iracing_ai_helper/session_data/qualify_logic_start.bin",
        )
        QualifyingService.qualifying(race_manager)
        irsdk.IRSDK.parse_to(
            race_manager.ir,
            to_file="C:/Users/Nick/Documents/iracing_ai_helper/session_data/qualify_logic_complete.bin",
        )
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
                        team="Kerling Motorsports" if driver["CarNumber"] == race_manager.race_weekend.race_data.player_car_num else
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


def main(db_path, driver_points_table, owner_points_table, field_size = None, penalty_chance = None,
         inspection_fail_chance_one = None, inspection_fail_chance_two = None, inspection_fail_chance_three = None,
         debris_caution_chance = None, unapproved_adjustments_chance = None, post_race_penalty_chance = None):
    race_manager = RaceManager(test_file=True)
    race_manager.race_weekend.race_settings.field_size = field_size
    race_manager.race_weekend.race_settings.penalty_chance = penalty_chance
    race_manager.race_weekend.race_settings.inspection_fail_chance_one = inspection_fail_chance_one
    race_manager.race_weekend.race_settings.inspection_fail_chance_two = inspection_fail_chance_two
    race_manager.race_weekend.race_settings.inspection_fail_chance_three = inspection_fail_chance_three
    race_manager.race_weekend.race_settings.debris_caution_chance = debris_caution_chance
    race_manager.race_weekend.race_settings.unapproved_adjustments_chance = unapproved_adjustments_chance
    race_manager.race_weekend.race_settings.post_race_penalty_chance = post_race_penalty_chance
    
    if race_manager.test_file_active:
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
        race_manager.race_weekend.stage_results[2].stage_results = race_manager.ir["SessionInfo"]["Sessions"][0]["ResultsPositions"]
    cars_to_dq = set_drivers(race_manager)
    """
    loop(race_manager, cars_to_dq)
    """
    if race_manager.race_weekend.race_settings.post_race_penalty_chance > 0:
        PostRacePenalties
    PointsCalculator.main(race_manager)
    PointsImporter(race_manager, db_path, driver_points_table, owner_points_table)


if __name__ == "__main__":
    field_size = 10
    penalty_chance = 8
    inspection_fail_chance_one = 2
    inspection_fail_chance_two = 4
    inspection_fail_chance_three = 6
    debris_caution_chance = 0
    unapproved_adjustments_chance = 1
    post_race_penalty_chance = 0
    db_path = "C:/Users/Nick/Documents/iracing_ai_helper/database/iracing_ai_helper.db"
    driver_points_table = "XFINITY_XFINITY_TEST_SEASON1_POINTS_DRIVER"
    owner_points_table = "XFINITY_XFINITY_TEST_SEASON1_POINTS_OWNER"
    main(db_path, driver_points_table, owner_points_table, field_size, penalty_chance,
         inspection_fail_chance_one, inspection_fail_chance_two, inspection_fail_chance_three,
         debris_caution_chance, unapproved_adjustments_chance, post_race_penalty_chance)
