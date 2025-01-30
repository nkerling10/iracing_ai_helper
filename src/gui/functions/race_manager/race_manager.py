"""
Massive credit to kutu for the pyirsdk linked below:
    https://github.com/kutu/pyirsdk/
"""

## Standard library imports
import logging
import random
import sys
import time
from pathlib import Path

## Third party imports
import irsdk

## Local imports
sys.path.append(f"{str(Path.cwd())}\\src")
from gui.functions.race_manager.setup.race_setup import RaceManager
from gui.functions.race_manager.setup.driver import Driver

from gui.functions.race_manager.services.practice_service import PracticeService
from gui.functions.race_manager.services.qualifying_service import QualifyingService
from gui.functions.race_manager.services.race_service import RaceService
from gui.functions.race_manager.services.points_calculator import PointsCalculator
from gui.functions.race_manager.services.points_importer import PointsImporter
from gui.functions.race_manager.services.post_race_penalties import PostRacePenalties

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
                        team=(
                            race_manager.race_weekend.race_data.player_team_name
                            if driver["CarNumber"]
                            == race_manager.race_weekend.race_data.player_car_num
                            else [
                                car[1]
                                for car in race_manager.season_data.cars_teams
                                if car[0] == driver["CarNumber"]
                            ][0]
                        ),
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


def main(
    season_settings: dict = {},
    db_path: str = "",
    stage_1_end: int = 0,
    stage_2_end: int = 0,
    race_end: int = 0,
    launcher: bool = False,
):
    race_manager = RaceManager(
        stage_1_end, stage_2_end, race_end, test_file=False if launcher else True
    )
    race_manager.race_weekend.race_data.player_team_name = season_settings.get(
        "player_team_name"
    )
    race_manager.race_weekend.race_settings.field_size = season_settings.get(
        "field_size", 10
    )
    race_manager.race_weekend.race_settings.pre_race_penalties_enabled = (
        season_settings.get("pre_race_penalties_enabled", True)
    )
    race_manager.race_weekend.race_settings.pre_race_penalties_chance = (
        season_settings.get("pre_race_penalties_chance", 2)
    )
    race_manager.race_weekend.race_settings.inspection_fail_chance_modifier = (
        season_settings.get("inspection_fail_chance_modifier", 2)
    )
    race_manager.race_weekend.race_settings.debris_cautions_enabled = (
        season_settings.get("debris_cautions_enabled", False)
    )
    race_manager.race_weekend.race_settings.debris_cautions_chance = (
        season_settings.get("debris_cautions_chance", 0)
    )
    race_manager.race_weekend.race_settings.post_race_penalties_enabled = (
        season_settings.get("post_race_penalties_enabled", True)
    )
    race_manager.race_weekend.race_settings.post_race_penalties_chance = (
        season_settings.get("post_race_penalties_chance", 2)
    )

    if race_manager.test_file_active:
        race_manager.race_weekend.stage_results[0].stage_results = random.shuffle([
            "Austin Hill",
            "Justin Allgaier",
            "Harrison Burton",
            "Sammy Smith",
            "Brandon Jones",
            "Daniel Dye",
            "William Sawalich",
            "Jesse Love",
            "Sheldon Creed",
            "Christian Eckes",
        ])
        race_manager.race_weekend.stage_results[1].stage_results = random.shuffle([
            "Austin Hill",
            "Justin Allgaier",
            "Sammy Smith",
            "Brandon Jones",
            "Sheldon Creed",
            "Harrison Burton",
            "Daniel Dye",
            "William Sawalich",
            "Jesse Love",
            "Christian Eckes",
        ])
        race_manager.race_weekend.stage_results[2].stage_results = race_manager.ir[
            "SessionInfo"
        ]["Sessions"][0]["ResultsPositions"]
    cars_to_dq = set_drivers(race_manager)
    if not race_manager.test_file_active:
        loop(race_manager, cars_to_dq)

    PostRacePenalties.main(race_manager)
    PointsCalculator.main(race_manager)
    PointsImporter(
        race_manager,
        f"{season_settings.get("season_series", "series")}_{season_settings.get("season_name", "season")}".upper(),
        db_path
    )


if __name__ == "__main__":
    main()
