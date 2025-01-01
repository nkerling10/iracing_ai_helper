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
from pathlib import Path
from enum import Enum
from datetime import datetime

from config.race_weekend import RaceWeekend
from config.race_settings import RaceSettings
# 
os.makedirs(Path(os.getcwd())/"logs", exist_ok=True)


class iRacing:
    def __init__(self):
        pass

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



def _test_print_stage_lengths(event):
    print(f"Stage 1: lap {event.stage_1_end_lap}")
    print(f"Stage 2: lap {event.stage_2_end_lap}")
    print(f"Stage 2 -> End: {event.race_laps - event.stage_2_end_lap} laps")
    quit()
