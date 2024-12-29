import irsdk
import time
import random
import json
import os
import pyautogui
import pygetwindow as gw
import logging
from pathlib import Path
from enum import Enum
from playsound import playsound
from datetime import datetime
# https://github.com/kutu/pyirsdk/blob/master/tutorials/02%20Using%20irsdk%20script.md

os.makedirs(f"{os.getcwd()}/logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(f"{os.getcwd()}/logs/{datetime.now()}.log"),
        logging.StreamHandler()
    ]
)

class State:
    ir_connected = False

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
        window = gw.getWindowsWithTitle("iRacing.com Simulator")[0]
        window.activate()
        self.ir.chat_command(1)
        time.sleep(0.5)
        pyautogui.typewrite(command)
        pyautogui.press("enter")

    @staticmethod
    def _get_flag(flag):
        '''
            Big thanks to fruzyna for this function
                source: https://github.com/fruzyna/iracing-apps
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

        return flag_color, flag & irsdk.Flags.repair

    def _pit_penalty(self, car_num):
        if car_num == self.ir["DriverInfo"]["Drivers"][0]["CarNumber"]:
            penalty = random.choice(self.penalties_player)
        else:
            penalty = random.choice(self.penalties)

        flag_color, _meatball = self._get_flag(self.ir["SessionFlags"])

        if flag_color == "green":
            logging.info(f"PENALTY - Passthrough for #{car_num}: {penalty}")
            self._send_iracing_command(f"!bl {car_num} D")
            self._send_iracing_command(f"PENALTY #{car_num}: {penalty}")
        elif flag_color == "yellow":
            logging.info(f"EOL for #{car_num}: {penalty}")
            self._send_iracing_command(f"!eol {car_num} PENALTY #{car_num}: {penalty}")

    # disable chat for all drivers to stop them from posting
    # when they are pitting
    def _disable_chat(self):
        for driver in self.ir["DriverInfo"]["Drivers"]:
            if driver["CarIsAI"] == 1:
                self._send_iracing_command(f"!nchat {driver['UserName'].replace(' ', '.')}")

    # disqualify all cars who are named NO DRIVER
    def _practice(self):
        logging.info("Starting practice handler")
        #self._send_iracing_command("!nchat")
        #self._disable_chat()
        dq_drivers = [driver["CarNumber"] for driver in
                      self.ir["DriverInfo"]["Drivers"] if
                      "NO DRIVER" in driver["UserName"]]
        for number in dq_drivers:
           logging.info(f"Disqualifying car {number} for NO DRIVER name")
           self._send_iracing_command(f"!dq {number} Car unused this week.")

    # identify when the session is QUALIFYING
    def _qualifying(self):
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

    def _issue_pre_race_penalty(self, car_num):
        penalty = random.choice(self.pre_race_penalties)
        if penalty == "Failed Inspection x2":
            logging.info(f"#{car_num} to the rear: {penalty}")
            self._send_iracing_command(f"!eol {car_num} #{car_num} to the rear: {penalty}")
        elif penalty == "Failed Inspection x3":
            logging.info(f"#{car_num} to the rear: {penalty}")
            logging.info(f"#{car_num} drivethrough")
            self._send_iracing_command(f"!eol {car_num}")
            self._send_iracing_command(f"!bl {car_num} D")
            self._send_iracing_command(f"#{car_num} to the rear plus drivethrough penalty: {penalty}")
        elif penalty == "Unapproved Adjustments":
            logging.info(f"#{car_num} to the rear: {penalty}")
            self._send_iracing_command(f"!eol {car_num} #{car_num} to the rear: {penalty}")

    def _pre_race_penalties(self):
        for driver in self.ir["DriverInfo"]["Drivers"]:
            if driver["CarIsPaceCar"] != 1:
                if random.randint(1, 100) < self.pre_race_penalty_chance:
                    self._issue_pre_race_penalty(driver["CarNumber"])

    def _race(self):
        logging.info("Starting race handler, sleeping for 5 seconds")
        time.sleep(5)
        logging.info("Playing sound file")
        playsound(os.path.join(os.getcwd(), "src/start-your-engines.mp3"))
        # wait 20 seconds for AI cars to grid
        # start the grid or else it will wait 5 minutes for DQ'd cars
        logging.info("Sleeping for 20 seconds")
        time.sleep(20)
        logging.info("Issuing gridstart command")
        self._send_iracing_command("!gridstart")
        self.ir.freeze_var_buffer_latest()
        logging.info("Issuing pre-race penalties")
        self._pre_race_penalties()
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
                    # check if any cars need to be removed from tracking
                    for car in pit_tracking:
                        if car not in cars_on_pit_road:
                            logging.info(f"{car} is no longer on pit road, checking for penalty")
                            pit_tracking.remove(car)
                            # calculate penalty chance once car leaves pit road
                            if random.randint(1, 100) < self.penalty_chance:
                                self._pit_penalty(car_num)
                else:
                    logging.info("No cars on pit road")
                    pit_tracking = []
                    time.sleep(1)
            else:
                logging.info("Lap is not >0, sleeping")
                time.sleep(1)

    def _check_iracing(self, state):
        if state.ir_connected and not (self.ir.is_initialized and self.ir.is_connected):
            state.ir_connected = False
            self.ir.shutdown()
            logging.info("irsdk disconnected")
        elif not state.ir_connected and self.ir.startup() and self.ir.is_initialized and self.ir.is_connected:
            state.ir_connected = True
            logging.info("irsdk connected")

    def _process_race(self):
        logging.info("Starting race processor!")

        while True:
            self.ir.freeze_var_buffer_latest()
            current_session = self.ir["SessionNum"]
            session_name = [session["SessionName"] for session in
                            self.ir["SessionInfo"]["Sessions"] if
                            session["SessionNum"] == current_session][0]
            logging.info(f"Current session: {current_session} - {session_name}")
            if current_session == 0:
                if session_name == "PRACTICE":
                    self._practice()
                if session_name == "QUALIFYING":
                    self._practice()
                    self._qualifying()
            elif current_session == 1:
                if session_name == "QUALIFYING":
                    self._practice()
                    self._qualifying()
                if session_name == "RACE":
                    self._race()
            elif current_session == 2:
                self._race()
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
    logging.info("App startup")
    iRacing()
