import irsdk
import time
import random
import json
import os
import pyautogui
import pygetwindow as gw
from pygetwindow import PyGetWindowException
import logging
import sounddevice as sd
import soundfile as sf
import math
from pathlib import Path
from enum import Enum
from datetime import datetime
# https://github.com/kutu/pyirsdk/blob/master/tutorials/02%20Using%20irsdk%20script.md

os.makedirs(Path(os.getcwd())/"logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(Path(os.getcwd())/"logs"/"debug.log"),
        logging.StreamHandler()
    ]
)

class State:
    ir_connected = False

class Race:
    def __init__(self, track, laps):
        self.track = track
        self.pre_race_penalties = []
        self.in_race_penalties = []
        self.pole_winner = ""
        self.race_laps = laps
        self.stage_1_end_lap = 0
        self.stage_1_results = []
        self.stage_2_end_lap = 0
        self.stage_2_results = []
        self.stage_3_end_lap = laps
        self.stage_3_results = []

        self._set_stage_lengths()
    
    def _set_stage_lengths(self):
        if self.track in ["Daytona", "Atlanta", "Watkins Glen"]:
            stage_1_mod = .25
        elif self.track == "COTA":
            stage_1_mod = .31
        elif self.track in ["Phoenix", "Las Vegas", "Homestead",
                            "Texas", "Charlotte", "Dover", "Kansas"]:
            stage_1_mod = .225
        elif self.track in ["Martinsville", "Nashville", "Sebring", "Rockingham"]:
            stage_1_mod = .24
        elif self.track == "Darlington":
            stage_1_mod = .307
        elif self.track == "Bristol":
            stage_1_mod = .285
        elif self.track in ["Talladega", "Pocono"]:
            stage_1_mod = .23
        elif self.track == "Sonoma":
            stage_1_mod = .26
        elif self.track in ["Indianapolis", "Iowa", "Charlotte Roval", "Chicago"]:
            stage_1_mod = .30
        elif self.track == "Laguna Seca":
            stage_1_mod = .34
        elif self.track == "WWTR":
            stage_1_mod = .22
        
        self.stage_1_end_lap = math.floor(self.race_laps * stage_1_mod)
        self.stage_2_end_lap = self.stage_1_end_lap * 2.15 if self.track == "COTA" else 2

class iRacing:
    def __init__(self):
        self.field_size = 50
        self.penalty_chance = 8
        self.pre_race_penalty_chance = 5
        self.penalties_player = ["Crew members over the wall too soon",
                                 "Too many men over the wall",
                                 "Tire violation"]
        self.penalties = ["Speeding - Too fast entering",
                          "Speeding - Too fast exiting",
                          "Crew members over the wall too soon",
                          "Too many men over the wall",
                          "Tire violation"]
        self.pre_race_penalties = ["Failed Inspection x2",
                                   "Failed Inspection x3",
                                   "Unapproved Adjustments"]
        self.ir = irsdk.IRSDK()
        #self.ir.startup(test_file="C:\\Users\\Nick\\Documents\\iracing_ai_randomizer\\session_data\\qual_ending.bin")
        self.ir.startup()
        
        self.main()

    def _send_iracing_command(self, command):
        '''
            Issue a command to iRacing via pyautogui.typewrite library
        '''
        while True:
            try:
                window = gw.getWindowsWithTitle("iRacing.com Simulator")[0]
                window.activate()
            except PyGetWindowException:
                continue
            break
        self.ir.chat_command(1)
        time.sleep(1)
        pyautogui.typewrite(command)
        pyautogui.press("enter")

    @staticmethod
    def _get_flag(flag):
        '''
            Big thanks to `fruzyna` for this function
                source: https://github.com/fruzyna/iracing-apps
            
            Determines the current flag status of the race, used when
                issuing pit penalty
        '''
        if flag & irsdk.Flags.checkered:
            flag_color = "checkered"
        else:
            if flag & irsdk.Flags.blue:
                flag_color = "blue"
            elif flag & irsdk.Flags.black:
                flag_color = "black"
            elif flag & irsdk.Flags.furled:
                flag_color = "gray"
            elif flag & irsdk.Flags.red:
                flag_color = "red"
            elif flag & irsdk.Flags.white:
                flag_color = "white"
            elif flag & irsdk.Flags.yellow or flag & irsdk.Flags.yellow_waving \
                 or flag & irsdk.Flags.caution or flag & irsdk.Flags.caution_waving \
                 or flag & irsdk.Flags.debris:
                flag_color = "yellow"
            elif flag & irsdk.Flags.green or flag & irsdk.Flags.green_held:
                flag_color = "green"
            else:
                flag_color = "green"

        return flag_color

    def _pit_penalty(self, car_num):
        '''
            Select and issue a pit penalty to designated car number
        '''
        if car_num == self.ir["DriverInfo"]["Drivers"][0]["CarNumber"]:
            penalty = random.choice(self.penalties_player)
        else:
            penalty = random.choice(self.penalties)

        flag_color = self._get_flag(self.ir["SessionFlags"])

        if flag_color == "green":
            logging.info(f"PENALTY: Passthrough for #{car_num}: {penalty}")
            self._send_iracing_command(f"!bl {car_num} D")
            self._send_iracing_command(f"PENALTY #{car_num}: {penalty}")
        elif flag_color == "yellow":
            logging.info(f"PENALTY: EOL for #{car_num}: {penalty}")
            self._send_iracing_command(f"!eol {car_num} PENALTY #{car_num}: {penalty}")

    def _disable_chat(self):
        '''
            disable chat for all drivers 1 by 1
                to stop them from posting when they are pitting
        '''
        for driver in self.ir["DriverInfo"]["Drivers"]:
            if driver["CarIsAI"] == 1:
                self._send_iracing_command(f"!nchat {driver['UserName'].replace(' ', '.')}")

    def _practice(self):
        '''
            1. Disqualify all drivers who are named NODRIVER{car_num}
            2. Calculate any pre-race penalties
        '''
        logging.info("Starting practice handler")
        #self._send_iracing_command("!nchat")
        #self._disable_chat()
        dq_drivers = [driver["CarNumber"] for driver in
                      self.ir["DriverInfo"]["Drivers"] if
                      "NODRIVER" in driver["UserName"]]
        for number in dq_drivers:
           logging.info(f"Disqualifying car {number} for NODRIVER name")
           self._send_iracing_command(f"!dq {number} Car unused this week.")

        logging.info("Issuing pre-race penalties")
        return self._pre_race_penalties()

    def _qualifying(self, weekend):
        '''
            Disqualify cars that qualify outside the designated
                field size in self.field_size
        '''
        logging.info("Starting qualifying handler")
        qual_done = False
        while qual_done is False:
            self.ir.freeze_var_buffer_latest()
            if self.ir["SessionState"] != 6:
                logging.info("Session state is not finalized..")
                time.sleep(1)
            else:
                while True:
                    logging.info("Session state is finalized, waiting for official results..")
                    self.ir.freeze_var_buffer_latest()
                    if self.ir["SessionInfo"]["Sessions"][1]["ResultsOfficial"] != 1:
                        logging.info("Waiting for results to become official..")
                        time.sleep(1)
                    else:
                        logging.info("Qualifying results are now official.")
                        break
                for position in self.ir["SessionInfo"]["Sessions"][1]["ResultsPositions"]:
                    if position["Position"] > self.field_size:
                        match = [driver["CarNumber"] for driver in
                                self.ir["DriverInfo"]["Drivers"] if
                                driver["CarIdx"] == position["CarIdx"]
                                and "NO DRIVER" not in driver["UserName"]]
                        if match:
                            logging.info(f"{match[0]} car missed the race")
                            self._send_iracing_command(f"!dq {match[0]} #{match[0]} missed the race")
                    
                    qual_done = True
        weekend.pole_winner = 

    def _issue_pre_race_penalty(self, penalty_cars):
        '''
            Issue a pit penalty to each car as necessary
        '''
        for car_num in penalty_cars:
            penalty = random.choice(self.pre_race_penalties)
            if penalty in ["Failed Inspection x2", "Unapproved Adjustments"]:
                logging.info(f"#{car_num} to the rear: {penalty}")
                self._send_iracing_command(f"!eol {car_num}")
                self._send_iracing_command(f"PENALTY: #{car_num} to the rear: {penalty}")
            elif penalty in ["Failed Inspection x3"]:
                logging.info(f"#{car_num} to the rear: {penalty}")
                logging.info(f"#{car_num} drivethrough")
                self._send_iracing_command(f"!eol {car_num}")
                self._send_iracing_command(f"!bl {car_num} D")
                self._send_iracing_command(f"PENALTY: #{car_num} to the rear plus drivethrough penalty: {penalty}")

    def _pre_race_penalties(self):
        '''
            Calculate pre-race penalties for each driver in the field
        '''
        penalty_cars = []
        for driver in self.ir["DriverInfo"]["Drivers"]:
            if driver["CarIsPaceCar"] != 1:
                if random.randint(1, 100) < self.pre_race_penalty_chance:
                    penalty_cars.append(driver["CarNumber"])
        return penalty_cars

    def _pre_race_events(self, penalty_cars):
        '''
            Handle all desired pre-race events

            Currently Implemented:
            1. Play `start your engines` sound file
            2. Issue gridstart command after waiting 30 seconds
            3. Issue pre-race penalties that were calculated
            4. TODO: Set up autostage/race result exporter
        '''
        logging.info("Playing sound file")
        try:
            sd.default.device = "Speakers (Realtek(R) Audio), MME"
            data, fs = sf.read(Path(f"{os.getcwd()}\\src\\assets\\start-your-engines.wav"), dtype='float32')  
            sd.play(data, fs)
        except Exception as e:
            logging.info(e)
        # wait 30 seconds for AI cars to grid
        self._send_iracing_command(f"Race will start in 30 seconds.")
        self._send_iracing_command(f"REMEMBER TO OPEN AUTOSTAGES!")
        logging.info("Sleeping for 30 seconds")
        time.sleep(30)
        logging.info("Issuing gridstart command")
        self._send_iracing_command("!gridstart")
        self.ir.freeze_var_buffer_latest()
        logging.info("Sleeping for 5 seconds")
        time.sleep(5)
        logging.info("Issuing pre-race penalties")
        self._issue_pre_race_penalty(penalty_cars)

    def _race(self, penalty_cars):
        logging.info("Starting race handler")
        self._pre_race_events(penalty_cars)
        pit_tracking = []
        while True:
            if self.ir["Lap"] > 0:
                self.ir.freeze_var_buffer_latest()
                # get all cars currently on pit road
                cars_on_pit_road = [driver["CarNumber"] for driver
                                    in self.ir["DriverInfo"]["Drivers"]
                                    if self.ir["CarIdxOnPitRoad"][driver["CarIdx"]]
                                    and driver["UserName"] != "Pace Car"]
                # if there is at least 1 car on pit road
                if len(cars_on_pit_road) > 0:
                    # for each car in this pulled instance
                    for car_num in cars_on_pit_road:
                        # if the car has not been processed this cycle
                        if car_num not in pit_tracking:
                            # track the car number
                            logging.info(f"Tracking pitstop for {car_num}")
                            pit_tracking.append(car_num)
                        # if the car has already been processed, skip it
                        else:
                            continue
                    # track for when a car leaves pit road
                    for car in pit_tracking:
                        if car not in cars_on_pit_road:
                            logging.info(f"{car} left pit road, penalty check")
                            # calculate penalty chance once car leaves pit road
                            if random.randint(1, 100) < self.penalty_chance:
                                self._pit_penalty(car_num)
                            pit_tracking.remove(car)
                else:
                    time.sleep(1)
            else:
                logging.info("Waiting for race to start..")
                time.sleep(1)

    def _check_iracing(self, state):
        if state.ir_connected and not (self.ir.is_initialized and self.ir.is_connected):
            state.ir_connected = False
            self.ir.shutdown()
            logging.info("irsdk disconnected")
        elif not state.ir_connected and self.ir.startup() and self.ir.is_initialized and self.ir.is_connected:
            state.ir_connected = True
            logging.info("irsdk connected")

    @staticmethod
    def _define_sessions(event_sessions):
        practice_session = [session["SessionNum"] for session in
                            event_sessions if
                            session["SessionName"] == "PRACTICE"][0]
        qualifying_session = [session["SessionNum"] for session in
                              event_sessions if
                              session["SessionName"] == "QUALIFY"][0]
        race_session = [session["SessionNum"] for session in
                        event_sessions if
                        session["SessionName"] == "RACE"][0]

    def _process_race(self):
        event_sessions = self.ir["SessionInfo"]["Sessions"]
        logging.info("Starting race processor!")
        self._define_sessions(event_sessions)
        race_session = [session["SessionNum"] for session in
                        self.ir["SessionInfo"]["Sessions"] if
                        session["SessionType"] == "Race"][0]
        weekend = Race(self.ir["WeekendInfo"]["TrackDisplayShortName"],
                       self.ir["SessionInfo"]["Sessions"][race_session]["SessionLaps"])
        penalties_set = False
        while True:
            self.ir.freeze_var_buffer_latest()
            current_session = self.ir["SessionNum"]
            session_name = [session["SessionName"] for session in
                            self.ir["SessionInfo"]["Sessions"] if
                            session["SessionNum"] == current_session][0]
            logging.info(f"Current session: {current_session} - {session_name}")
            if current_session == 0:
                if session_name == "PRACTICE":
                    if penalties_set is False:
                        penalty_cars = self._practice()
                        penalties_set = True
                if session_name == "QUALIFYING":
                    if penalties_set is False:
                        penalty_cars = self._practice()
                        penalties_set = True
                    self._qualifying(weekend)
            elif current_session == 1:
                if session_name == "QUALIFYING":
                    if penalties_set is False:
                        penalty_cars = self._practice()
                        penalties_set = True
                    self._qualifying(weekend)
                if session_name == "RACE":
                    self._race(penalty_cars)
            elif current_session == 2:
                self._race(penalty_cars)
            else:
                time.sleep(1)

    def main(self):
        state = State()
        try:
            while True:
                self._check_iracing(state)
                if state.ir_connected:
                    self._process_race()
                logging.info("Waiting for connection to iRacing..")
                time.sleep(1)
        except KeyboardInterrupt:
            pass


if __name__ == '__main__':
    event = Race("Darlington", 147)
    print(f"Stage 1: lap {event.stage_1_end_lap}")
    print(f"Stage 2: lap {event.stage_2_end_lap}")
    print(f"Stage 2 -> End: {event.laps - event.stage_2_end_lap} laps")
    quit()
    logging.info("App startup")
    iRacing()
