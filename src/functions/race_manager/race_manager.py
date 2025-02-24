"""
Massive credit to kutu for the pyirsdk linked below:
    https://github.com/kutu/pyirsdk/
"""

## Standard library imports
import logging
import json
import sys
import time
from pathlib import Path

## Third party imports
import irsdk

## Local imports
sys.path.append(f"{str(Path.cwd())}/src")
from functions.race_manager.setup.race_setup import RaceManager
from functions.race_manager.setup.driver import Driver

from functions.race_manager.services.practice_service import PracticeService
from functions.race_manager.services.qualifying_service import QualifyingService
from functions.race_manager.services.race_service import RaceService
from functions.race_manager.services.points_calculator import PointsCalculator
from functions.race_manager.services.points_importer import PointsImporter
from functions.race_manager.services.post_race_penalties import PostRacePenalties
from assets.misc.data_converter import convert_car_driver_mapping, convert_drivers

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
        and race_manager.ir["SessionInfo"]["Sessions"][race_manager.qualifying_session_num]["ResultsOfficial"] == 0
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
                        car_idx=driver["CarIdx"],
                        name=driver["UserName"],
                        car=driver["CarNumber"],
                        team=race_manager.race_weekend.race_data.player_car_num
                            if driver["CarIsAI"] == 0
                            else race_manager.season_data.car_driver_map[driver["CarNumber"]]["team"],
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
            if race_manager.ir["SessionState"] == 6:
                return
            current_session_race(race_manager)
        else:
            time.sleep(1)


def start_race_manager(
    car_driver_map: dict,
    driver_data: dict,
    season_data: dict = {},
    race_stage_lengths: list = [],
    launcher: bool = False,
):
    race_manager = RaceManager(
        season_data,
        car_driver_map,
        driver_data,
        race_stage_lengths,
        test_file=False if launcher else True,
    )

    cars_to_dq = set_drivers(race_manager)
    if not race_manager.test_file_active:
        loop(race_manager, cars_to_dq)

    PostRacePenalties.main(race_manager)
    PointsCalculator.main(race_manager)
    race_results = {}
    for stage in race_manager.race_weekend.stage_results:
        race_results += stage
    with open(Path.cwd() / "results" / "race_result.json", "w") as result_file:
        result_file.write(json.dumps(result_file, indent=4))

    return


if __name__ == "__main__":
    example_season_data = {'season_name': 'xfinity4', 'player_team_name': 'cac', 'season_series': 'XFINITY', 'iracing_roster_file': 'C:/Users/Nick/Documents/iRacing/airosters/xfinity4', 'iracing_season_file': 'C:/Users/Nick/Documents/iRacing/aiseasons/xfinity4.json', 'user_settings': {'stages_enabled': True, 'field_size': 38, 'race_distance_percent': 100, 'fuel_capacity': 100, 'tire_sets': 'UNLIMITED', 'pre_race_penalties': {'enabled': True, 'chance': 2, 'inspection_fail_chance_modifier': 2}, 'pit_penalties': {'enabled': True, 'chance': 8}, 'post_race_penalties': {'enabled': True, 'chance': 2}, 'debris_cautions': {'enabled': True, 'chance': 1}}}
    race_stage_lengths = [30, 60, 120]
    car_driver_map = convert_car_driver_mapping(example_season_data.get("season_series"))
    driver_data = convert_drivers(example_season_data.get("season_series"))
    start_race_manager(car_driver_map, driver_data, example_season_data, race_stage_lengths)
