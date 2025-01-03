"""
Massive credit to kutu for the pyirsdk linked below:
    https://github.com/kutu/pyirsdk/
"""

## Standard library imports
import logging
import os
import json
import time
import platform
import math
import tkinter as tk
from tkinter import filedialog
from pathlib import Path

## Third party imports
import irsdk
import pyautogui
import pygetwindow as gw
from pygetwindow import PyGetWindowException

## Local imports
from config.race_settings import RaceSettings
from services.core.stage import Stage
from services.session.practice_service import PracticeService
from services.session.qualifying_service import QualifyingService
from services.session.race_service import RaceService
from assets import tracks

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(module)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(Path(os.getcwd()) / "logs" / "debug.log"),
        logging.StreamHandler(),
    ],
)

test_file = Path(
    "C:\\Users\\Nick\\Documents\\iracing_ai_randomizer\\session_data\\dataracing.bin"
)


class State:
    ir_connected = False


class RaceWeekend:
    def __init__(self, track_short_name, track_long_name, race_length, player_car_num):
        self.track_short_name = track_short_name
        self.track_long_name = track_long_name
        self.race_length = race_length
        self.pre_race_penalties = []
        self.pole_winner = ""
        self.stage_1 = Stage()
        self.stage_2 = Stage()
        self.stage_3 = Stage(stage_end_lap=race_length)
        self.player_car_num = player_car_num

        self._set_stage_lengths()

    def _set_stage_lengths(self) -> None:
        if self.track_short_name in ["Daytona", "Atlanta", "Watkins Glen"]:
            stage_1_mod = 0.25
        elif self.track_short_name == "COTA":
            stage_1_mod = 0.31
        elif self.track_short_name in [
            "Phoenix",
            "Las Vegas",
            "Homestead",
            "Texas",
            "Charlotte",
            "Dover",
            "Kansas",
        ]:
            stage_1_mod = 0.225
        elif self.track_short_name in [
            "Martinsville",
            "Nashville",
            "Sebring",
            "Rockingham",
        ]:
            stage_1_mod = 0.24
        elif self.track_short_name == "Darlington":
            stage_1_mod = 0.307
        elif self.track_short_name == "Bristol":
            stage_1_mod = 0.285
        elif self.track_short_name in ["Talladega", "Pocono"]:
            stage_1_mod = 0.23
        elif self.track_short_name == "Sonoma":
            stage_1_mod = 0.26
        elif self.track_short_name in [
            "Indianapolis",
            "Iowa",
            "Charlotte Roval",
            "Chicago",
        ]:
            stage_1_mod = 0.30
        elif self.track_short_name == "Laguna Seca":
            stage_1_mod = 0.34
        elif self.track_short_name == "WWTR":
            stage_1_mod = 0.22

        self.stage_1.stage_end_lap = math.floor(self.race_length * stage_1_mod)
        self.stage_2.stage_end_lap = math.floor(
            self.stage_1.stage_end_lap * 2.15
            if self.track_short_name == "COTA"
            else self.stage_1.stage_end_lap * 2
        )


class RaceManager:
    def __init__(self, test_file=None):
        self.state = State()
        self.race_settings = RaceSettings()
        self.race_weekend = None
        self.practice_session_num = None
        self.practice_done = False
        self.qualifying_session_num = None
        self.qualifying_done = False
        self.race_session_num = None
        self.race_done = False
        self.ir = irsdk.IRSDK()
        self.ir.startup(test_file)
        if not test_file:
            self._connect()

    def send_iracing_command(self, command) -> None:
        """
        Issue a command to iRacing via pyautogui.typewrite library
        """
        while True:
            try:
                window = gw.getWindowsWithTitle("iRacing.com Simulator")[0]
                window.activate()
                logging.debug("Activated window")
            except PyGetWindowException:
                logging.error("PyGetWindowException error!")
                continue
            break
        logging.debug("Sending chat command")
        self.ir.chat_command(1)
        pyautogui.typewrite(command)
        pyautogui.press("enter")
        time.sleep(1)

    def define_sessions(self) -> None:
        event_sessions = self.ir["SessionInfo"]["Sessions"]
        practice_session = [
            session["SessionNum"]
            for session in event_sessions
            if session["SessionName"] == "PRACTICE"
        ]
        if practice_session:
            self.practice_session_num = practice_session[0]

        qualifying_session = [
            session["SessionNum"]
            for session in event_sessions
            if session["SessionName"] == "QUALIFY"
        ]
        if qualifying_session:
            self.qualifying_session_num = qualifying_session[0]

        race_session = [
            session["SessionNum"]
            for session in event_sessions
            if session["SessionName"] == "RACE"
        ]
        if race_session:
            self.race_session_num = race_session[0]

    def get_current_sessions(self) -> tuple[int, str]:
        self.ir.freeze_var_buffer_latest()
        current_session_num = self.ir["SessionNum"]
        current_session_name = [
            session["SessionName"]
            for session in self.ir["SessionInfo"]["Sessions"]
            if session["SessionNum"] == current_session_num
        ][0]

        return current_session_num, current_session_name

    def _check_iracing(self, state) -> None:
        if state.ir_connected and not (self.ir.is_initialized and self.ir.is_connected):
            state.ir_connected = False
            self.ir.shutdown()
            logging.info("irsdk disconnected")
        elif (
            not state.ir_connected
            and self.ir.startup()
            and self.ir.is_initialized
            and self.ir.is_connected
        ):
            state.ir_connected = True
            logging.info("irsdk connected")

    def _connect(self) -> None:
        try:
            while True:
                self._check_iracing(self.state)
                if self.state.ir_connected:
                    return
                logging.info("Waiting for connection to iRacing..")
                time.sleep(1)
        except KeyboardInterrupt:
            quit()


def practice(race_manager) -> None:
    PracticeService.practice(race_manager)


def qualifying(race_manager) -> None:
    QualifyingService.qualifying(race_manager)


def race(race_manager) -> None:
    RaceService.race(race_manager)


def loop(race_manager) -> None:
    while True:
        ## Figure out what session is currently active
        ## This will prove useful if the app crashes during any session
        _current_session_num, current_session_name = race_manager.get_current_sessions()
        if current_session_name == "PRACTICE" and race_manager.practice_done is False:
            ## Regardless if a weekend actually has a practice session
            ## Execute the practice stage as long as the first session is not completed
            if race_manager.ir["SessionInfo"]["Sessions"][
                race_manager.practice_session_num
            ]["ResultsOfficial"] == 0 or (
                race_manager.practice_session_num is None
                and race_manager.ir["SessionInfo"]["Sessions"][
                    race_manager.qualifying_session_num
                ]["ResultsOfficial"]
                == 0
            ):
                practice(race_manager)
                race_manager.practice_done = True
                logging.info("Practice operations are complete!")
            else:
                logging.debug("Practice stage does not need to be executed, skipping")
                race_manager.practice_done = True

        elif (
            current_session_name == "QUALIFYING"
            and race_manager.qualifying_done is False
        ):
            ## Perform the qualifying session operations
            ## Execute the operations as long as the session has not been completed
            if race_manager.ir["SessionInfo"]["Sessions"][
                race_manager.qualifying_session_num
            ]["ResultsOfficial"] == 0 or (
                race_manager.qualifying_session_num is None
                and race_manager.ir["SessionInfo"]["Sessions"][
                    race_manager.race_session_num
                ]["ResultsOfficial"]
                == 0
            ):
                qualifying(race_manager)
                race_manager.qualifying_done = True
                logging.info("Qualifying operations are complete!")
            else:
                logging.debug("Qualifying stage does not need to be executed, skipping")
                race_manager.qualifying_done = True

        elif current_session_name == "RACE":
            if (
                race_manager.qualifying_session_num is None
                or race_manager.ir["SessionInfo"]["Sessions"][
                    race_manager.qualifying_session_num
                ]["ResultsOfficial"]
                == 1
            ):
                race(race_manager)

        else:
            time.sleep(1)


def set_weekend_data(race_manager) -> None:
    ## Identify which sessions exist in the "race weekend"
    race_manager.define_sessions()
    ## Set the initially required data
    race_manager.race_weekend = RaceWeekend(
        track_short_name=race_manager.ir["WeekendInfo"]["TrackDisplayShortName"],
        track_long_name=race_manager.ir["WeekendInfo"]["TrackDisplayName"],
        race_length=race_manager.ir["SessionInfo"]["Sessions"][
            race_manager.race_session_num
        ]["SessionLaps"],
        player_car_num=race_manager.ir["DriverInfo"]["Drivers"][0]["CarNumber"],
    )


def main() -> None:
    # race_manager = RaceManager(test_file)
    race_manager = RaceManager()
    ## Once iRacing is connected, set required weekend data
    set_weekend_data(race_manager)
    ## After data is set, proceed to looping logic
    loop(race_manager)


if __name__ == "__main__":
    main()


def get_next_race(ai_season_file):
    for event in ai_season_file.get("events"):
        if not event.get("results"):
            next_event = tracks.Track(event.get("trackId")).name
            return f"{next_event} is the next race"


def main2():
    root = tk.Tk()
    root.withdraw()

    if platform.system() == "Darwin":
        default = Path.cwd() / "seasons"
    else:
        default = Path.home() / "Documents" / "iRacing" / "aiseasons"
    """
    file_select = filedialog.askopenfilename(initialdir=default)
    """
    file_select = Path(default / "2025 NSK Xfinity Series_withresults.json")
    with open(file_select, "r") as file:
        ai_season_file = json.loads(file.read())

    if ai_season_file["carId"] in [114, 115, 116]:
        season_type = "Xfinity"
    if ai_season_file["carId"] in [111, 123, 155]:
        season_type = "Truck"

    print(get_next_race(ai_season_file))
