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

def _set_testing_data(race_manager):
    race_manager.season_data.pole_winner = "Alex Bowman"
    race_manager.race_weekend.drivers = [
        Driver(
            car_idx=0,
            name="Nick Kerling",
            car="79",
            team="Kerling Family Racing",
            points_eligibile=(True),
        ),
        Driver(
            car_idx=1,
            name="Alex Bowman",
            car="17",
            team="Hendrick Motorsports",
            points_eligibile=(False),
        ),
        Driver(
            car_idx=2,
            name="Justin Allgaier",
            car="7",
            team="JR Motorsports",
            points_eligibile=(True),
        ),
        Driver(
            car_idx=3,
            name="Sheldon Creed",
            car="00",
            team="Haas Factory Team",
            points_eligibile=(True),
        ),
        Driver(
            car_idx=4,
            name="Jesse Love",
            car="2",
            team="Richard Childress Racing",
            points_eligibile=(True),
        ),
        Driver(
            car_idx=5,
            name="Austin Hill",
            car="21",
            team="Richard Childress Racing",
            points_eligibile=(True),
        ),
        Driver(
            car_idx=6,
            name="Sammy Smith",
            car="8",
            team="JR Motorsports",
            points_eligibile=(True),
        ),
        Driver(
            car_idx=7,
            name="Ryan Sieg",
            car="39",
            team="RSS Racing",
            points_eligibile=(True),
        ),
        Driver(
            car_idx=8,
            name="Carson Kvapil",
            car="1",
            team="JR Motorsports",
            points_eligibile=(True),
        ),
        Driver(
            car_idx=9,
            name="Connor Zilisch",
            car="88",
            team="JR Motorsports",
            points_eligibile=(True),
        ),
        Driver(
            car_idx=10,
            name="Taylor Gray",
            car="54",
            team="Joe Gibbs Racing",
            points_eligibile=(True),
        ),
        Driver(
            car_idx=11,
            name="Parker Retzlaff",
            car="4",
            team="Alpha Prime Racing",
            points_eligibile=(True),
        ),
        Driver(
            car_idx=12,
            name="Corey Heim",
            car="24",
            team="Sam Hunt Racing",
            points_eligibile=(False),
        )
    ]
    race_manager.race_weekend.stage_results[0].stage_results = ["Alex Bowman", "Justin Allgaier", "Sheldon Creed", "Jesse Love", "Austin Hill",
                                                                "Sammy Smith", "Ryan Sieg", "Carson Kvapil", "Connor Zilisch", "Taylor Gray"]

    race_manager.race_weekend.stage_results[1].stage_results = ["Alex Bowman", "Corey Heim", "Nick Kerling", "Justin Allgaier", "Austin Hill",
                                                                "Sheldon Creed", "Jesse Love", "Parker Retzlaff", "Connor Zilisch", "Sammy Smith"]
    race_manager.race_weekend.stage_results[2].stage_results = []


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
    else:
        _set_testing_data(race_manager)

    print(race_manager.race_weekend.stage_results[2])

    PostRacePenalties.main(race_manager)
    PointsCalculator.main(race_manager)

    if race_manager.test_file_active:
        for driver in race_manager.race_weekend.drivers:
            print(json.dumps(driver.__dict__, indent=2))
        quit()
    race_results = []
    for stage in race_manager.race_weekend.stage_results:
        race_results.append(stage.stage_results)
    with open(Path.cwd() / "results" / "race_result.json", "w") as result_file:
        result_file.write(json.dumps(race_results, indent=4))

    return


if __name__ == "__main__":
    example_season_data = {'season_name': 'xfinity4', 'player_team_name': 'cac', 'season_series': 'XFINITY', 'iracing_roster_file': 'C:/Users/Nick/Documents/iRacing/airosters/xfinity4', 'iracing_season_file': 'C:/Users/Nick/Documents/iRacing/aiseasons/xfinity4.json', 'user_settings': {'stages_enabled': True, 'field_size': 38, 'race_distance_percent': 100, 'fuel_capacity': 100, 'tire_sets': 'UNLIMITED', 'pre_race_penalties': {'enabled': True, 'chance': 2, 'inspection_fail_chance_modifier': 2}, 'pit_penalties': {'enabled': True, 'chance': 8}, 'post_race_penalties': {'enabled': True, 'chance': 2}, 'debris_cautions': {'enabled': True, 'chance': 1}}}
    race_stage_lengths = [30, 60, 120]
    car_driver_map = convert_car_driver_mapping(example_season_data.get("season_series"))
    driver_data = convert_drivers(example_season_data.get("season_series"))
    start_race_manager(car_driver_map, driver_data, example_season_data, race_stage_lengths)
