## Standard library imports
import logging
import time

## Third party imports
import irsdk
import pyautogui
import pygetwindow as gw
import sqlite3
from pygetwindow import PyGetWindowException

logger = logging.getLogger(__name__)

class State:
    ir_connected = False


class SeasonData:
    def __init__(self):
        self.drivers_list = None
        self.cars_teams = None
        self.past_season_winners = None
        self.current_season_winners = None
        self.owner_points = None
        self.point_values = None
        self._pull_and_set_season_data()
    
    def _pull_and_set_season_data(self) -> None:
        """
            Pulls required season data from the database and self assigns it
        """
        ## TODO: rework these queries to be dynamic
        ## TODO: utilize the global db manager passed in from gui
        conn = sqlite3.connect("C:/Users/Nick/Documents/iracing_ai_helper/database/iracing_ai_helper.db")
        self.drivers_list=conn.cursor().execute("SELECT * FROM DRIVER WHERE DECLARED_POINTS == 'XFINITY'").fetchall()
        self.cars_teams = conn.cursor().execute("SELECT NUMBER, TEAM FROM CAR_XFINITY").fetchall()
        points_eligible=[driver[0] for driver in conn.cursor().execute("SELECT NAME FROM DRIVER WHERE DECLARED_POINTS == 'XFINITY'").fetchall()]
        self.declared_points = points_eligible
        prev_season_winners=[value for value in conn.cursor().execute("SELECT * FROM XFINITY_2024_WINNERS").fetchall()]
        self.past_season_winners = prev_season_winners[0]
        self.current_season_winners=[value[0] for value in conn.cursor().execute("SELECT NAME, WINS FROM XFINITY_2025_POINTS_DRIVER WHERE WINS != 0 or NULL").fetchall()],
        self.owner_points=conn.cursor().execute("SELECT * FROM XFINITY_2025_POINTS_OWNER").fetchall()
        self.point_values=[value[0] for value in conn.cursor().execute("SELECT POINTS FROM POINTS_AWARDED_TABLE").fetchall()]
        conn.close()


class Track:
    def __init__(self):
        self.track_id = 0
        self.track_short_name = None
        self.track_long_name = None
        self.track_turns = 0


class Stage:
    def __new__(cls, stage_num):
        instance = super().__new__(cls)
        return instance

    def __init__(self, stage_num):
        self.stage = stage_num
        self.stage_end_lap = 0
        self.stage_results = []
        self.pit_penalties = []
        self.stage_ending_early = False
        self.pits_are_closed = False
        self.last_lap_notice = False
        self.stage_complete = False
        self.advance_to_next_stage = False


class RaceData:
    def __init__(self):
        self.driver_caridx_map = None
        self.pre_race_penalties = []
        self.pole_winner = ""
        self.player_car_num = 0


class RaceSettings:
    def __init__(self):
        self.field_size = 10
        self.penalty_chance = 8
        self.inspection_fail_chance_one = 2
        self.inspection_fail_chance_two = 4
        self.inspection_fail_chance_three = 6
        self.debris_caution_chance = 0
        self.unapproved_adjustments_chance = 1
        self.penalties_player = [
            "Crew members over the wall too soon",
            "Too many men over the wall",
            "Tire violation",
        ]
        self.penalties = [
            "Speeding - Too fast entering",
            "Speeding - Too fast exiting",
            "Crew members over the wall too soon",
            "Too many men over the wall",
            "Tire violation",
        ]
        self.pre_race_penalties = [
            "Unapproved Adjustments",
        ]


class RaceWeekend:
    def __init__(self):
        self.race_length = 0
        self.track = Track()
        self.race_settings = RaceSettings()
        self.race_data = RaceData()
        self.drivers = []
        self.stage_results = [Stage(1), Stage(2)]
        self.race_results = []
        self.weekend_points = []


class RaceManager:
    def __init__(self, test_file: bool = False):
        self.state = State()
        self.season_data = SeasonData()
        self.race_weekend = RaceWeekend()
        self.practice_session_num = None
        self.practice_done = False
        self.qualifying_session_num = None
        self.qualifying_done = False
        self.race_session_num = None
        self.race_done = False
        self.ir = irsdk.IRSDK()
        if test_file:
            self.ir.startup("C:/Users/Nick/Documents/iracing_ai_helper/session_data/race_finished.bin")
        else:
            self._connect()
        self._set_weekend_data()

    def send_iracing_command(self, command: str) -> None:
        """
        Issue a command to iRacing via pyautogui.typewrite library
        """
        while True:
            try:
                window = gw.getWindowsWithTitle("iRacing.com Simulator")[0]
                window.activate()
                logger.debug("Activated window")
            except PyGetWindowException:
                logger.error("PyGetWindowException error!")
                time.sleep(0.5)
            break
        logger.debug(f"Sending chat command: {command}")
        self.ir.chat_command(1)
        time.sleep(0.5)
        pyautogui.typewrite(command)
        pyautogui.press("enter")
        time.sleep(0.5)

    def _define_sessions(self) -> None:
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

    def _get_current_sessions(self) -> tuple[int, str]:
        self.ir.freeze_var_buffer_latest()
        current_session_num = self.ir["SessionNum"]
        current_session_name = [
            session["SessionName"]
            for session in self.ir["SessionInfo"]["Sessions"]
            if session["SessionNum"] == current_session_num][0]

        return current_session_num, current_session_name

    def _check_iracing(self, state: object) -> None:
        if state.ir_connected and not (self.ir.is_initialized and self.ir.is_connected):
            state.ir_connected = False
            self.ir.shutdown()
            logger.info("irsdk disconnected")
        elif (
            not state.ir_connected
            and self.ir.startup()
            and self.ir.is_initialized
            and self.ir.is_connected
        ):
            state.ir_connected = True
            logger.info("irsdk connected")

    def _connect(self) -> None:
        try:
            while True:
                self._check_iracing(self.state)
                if self.state.ir_connected:
                    return
                logger.info("Waiting for connection to iRacing..")
                time.sleep(1)
        except KeyboardInterrupt:
            quit()

    def _set_weekend_data(self) -> None:
        self._define_sessions()
        self.race_weekend.track.track_short_name=self.ir["WeekendInfo"]["TrackDisplayShortName"]
        self.race_weekend.track.track_long_name=self.ir["WeekendInfo"]["TrackDisplayName"],
        self.race_weekend.race_length=self.ir["SessionInfo"]["Sessions"][self.race_session_num]["SessionLaps"],
        self.race_weekend.race_data.player_car_num=self.ir["DriverInfo"]["Drivers"][0]["CarNumber"],
        self.race_weekend.race_data.driver_caridx_map=[{"name": driver["UserName"], "car": driver["CarNumber"]} for driver in self.ir["DriverInfo"]["Drivers"] if driver["UserName"] != "Pace Car"]
