## Standard library imports
import json
import logging
import time
from pathlib import Path

## Third party imports
import irsdk
import pyautogui
import pygetwindow as gw
from pygetwindow import PyGetWindowException

logger = logging.getLogger(__name__)


class State:
    ir_connected = False


class SeasonData:
    def __init__(self, season_data, car_driver_map, driver_data):
        self.season_data = season_data
        self.drivers_list = driver_data
        self.declared_points = [k for k,_r in driver_data.items() if _r["DECLARED_POINTS"] == season_data.get("season_series")]
        self.car_driver_map = car_driver_map
        self.past_season_winners = self._past_season_winners(self.season_data.get("season_series"))
        self.current_season_winners = None
        self.owner_points = self._set_owner_points()
        self.driver_points = self._set_driver_points()
        self.point_values = self._set_point_values(self.season_data.get("season_series"))

    @staticmethod
    def _past_season_winners(season_series: str):
        with open(Path.cwd() / "src" / "data" / f"2024_{season_series}_WINNERS.json", "r") as winners_file:
            return json.loads(winners_file.read())

    def _set_owner_points(self):
        points_file = Path.cwd() / "src" / "data" / f"{self.season_data.get("season_series")}_{self.season_data.get("season_name")}_owner_points.json"
        try:
            with open(points_file, "r") as owner_points_file:
                return json.loads(owner_points_file.read())
        except FileNotFoundError:
            with open(points_file, "w") as new_owner_points_file:
                new_owner_points_file.write(json.dumps({}, indent=4))
                return {}

    def _set_driver_points(self):
        points_file = Path.cwd() / "src" / "data" / f"{self.season_data.get("season_series")}_{self.season_data.get("season_name")}_driver_points.json"
        try:
            with open(points_file, "r") as driver_points_file:
                return json.loads(driver_points_file.read())
        except FileNotFoundError:
            with open(points_file, "w") as new_driver_points_file:
                new_driver_points_file.write(json.dumps({}, indent=4))
                return {}

    @staticmethod
    def _set_point_values(season_series: str):
        point_index = []
        with open(Path.cwd() / "src" / "data" / f"{season_series}_POINT_VALUES.json", "r") as points_file:
            points = json.loads(points_file.read())
        for each in points:
            point_index.append(each.get("POINTS"))
        return point_index


class Track:
    def __init__(self):
        self.track_id = 0
        self.track_short_name = None
        self.track_long_name = None
        self.track_turns = 0


class Stage:
    def __new__(cls, stage_num, stage_end_lap):
        instance = super().__new__(cls)
        return instance

    def __init__(self, stage_num: int, stage_end_lap: int):
        self.stage = stage_num
        self.stage_end_lap = stage_end_lap
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
        self.player_car_num = ""
        self.player_team_name = ""


class RaceSettings:
    def __init__(self):
        self.field_size = 0
        self.stage_cautions = True
        self.penalty_chance = 0
        self.pre_race_penalties_enabled = True
        self.pre_race_penalties_chance = 2
        self.inspection_fail_chance_modifier = 2
        self.debris_cautions_enabled = False
        self.debris_cautions_chance = 0
        self.unapproved_adjustments_chance = 0
        self.post_race_penalties_enabled = True
        self.post_race_penalties_chance = 2
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
    def __init__(self, race_stage_lengths: list):
        self.race_length = race_stage_lengths[-1]
        self.track = Track()
        self.race_settings = RaceSettings()
        self.race_data = RaceData()
        self.drivers = []
        self.stage_results = self._build_stages(race_stage_lengths)
        self.weekend_points = []

    @staticmethod
    def _build_stages(race_stage_lengths: list) -> list[object]:
        race_stages = []
        stage_count = 1
        for stage in race_stage_lengths:
            race_stages.append(Stage(stage_count, stage))
            stage_count += 1
        return race_stages

class RaceManager:
    def __init__(
        self,
        season_data: dict,
        car_driver_map: dict,
        driver_data: dict,
        race_stages: list,
        test_file: bool = False,
    ):
        self.state = State()
        self.season_data = SeasonData(season_data, car_driver_map, driver_data)
        self.race_weekend = RaceWeekend(race_stages)
        self.observe = False
        self.practice_session_num = None
        self.practice_done = False
        self.qualifying_session_num = None
        self.qualifying_done = False
        self.race_session_num = None
        self.race_done = False
        self.test_file_active = True if test_file else False
        self.ir = irsdk.IRSDK()
        if test_file:
            self.ir.startup(
                "C:/Users/Nick/Documents/iracing_ai_helper/session_data/race_finished.bin"
            )
        else:
            self._connect()
        self._set_weekend_data()

    def send_iracing_command(self, command: str) -> None:
        """
        Issue a command to iRacing via pyautogui.typewrite library
        """
        while True:
            window = gw.getWindowsWithTitle("iRacing.com Simulator")[0]
            try:
                window.activate()
                logger.debug("Activated window")
                break
            except PyGetWindowException:
                logger.error("PyGetWindowException error!")
                time.sleep(0.5)
        logger.debug(f"Sending chat command: {command}")
        self.ir.chat_command(1)
        time.sleep(0.5)
        pyautogui.typewrite(command)
        pyautogui.press("enter")
        time.sleep(0.2)

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
            if session["SessionNum"] == current_session_num
        ][0]

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
        with open("C:/Users/Nick/Documents/iracing_ai_helper/src/assets/references/iracing_tracks.json", "r") as track_file:
            tracks = json.loads(track_file.read())
        
        if self.ir["WeekendInfo"]["TrackID"] not in tracks:
            tracks[self.ir["WeekendInfo"]["TrackID"]] = {
                "iracing_name": self.ir["WeekendInfo"]["TrackName"],
                "long_name": self.ir["WeekendInfo"]["TrackDisplayName"],
                "short_name": self.ir["WeekendInfo"]["TrackDisplayShortName"]
            }
        else:
            if self.ir["WeekendInfo"]["TrackID"]["iracing_name"] == "":
                tracks[self.ir["WeekendInfo"]["TrackID"]].update(iracing_name=self.ir["WeekendInfo"]["TrackName"])

        with open("C:/Users/Nick/Documents/iracing_ai_helper/src/assets/references/iracing_tracks.json", "w") as track_file:
             json.dump(tracks, track_file, ensure_ascii=False, indent=4)

        self.race_weekend.track.track_short_name = self.ir["WeekendInfo"][
            "TrackDisplayShortName"
        ]
        self.race_weekend.track.track_long_name = self.ir["WeekendInfo"][
            "TrackDisplayName"
        ]
        self.race_weekend.race_length = self.ir["SessionInfo"]["Sessions"][
            self.race_session_num
        ]["SessionLaps"]
        self.race_weekend.race_data.player_car_num = self.ir["DriverInfo"]["Drivers"][
            0
        ]["CarNumber"]
        self.race_weekend.race_data.driver_caridx_map = [
            {"name": driver["UserName"], "car": driver["CarNumber"]}
            for driver in self.ir["DriverInfo"]["Drivers"]
            if driver["UserName"] != "Pace Car"
        ]
