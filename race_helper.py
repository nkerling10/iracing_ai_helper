import irsdk
import time
import random
from enum import Enum
# https://github.com/kutu/pyirsdk/blob/master/tutorials/02%20Using%20irsdk%20script.md


class iRacing:
    def __init__(self):
        self.field_size = 41
        self.penalty_chance = 100
        self.pre_race_penalty_chance = 100
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
        #self.ir.startup(test_file='session_data/data_practice.bin')
        self.ir.startup()
        self.main()

    @staticmethod
    def _get_flag(flag):
        if flag & irsdk.Flags.checkered:
            flag_color = 'checkered'
        else:
            if flag & irsdk.Flags.blue:
                flag_color = 'blue'
            elif flag & irsdk.Flags.black:
                flag_color = 'black'
            elif flag & irsdk.Flags.furled:
                flag_color = 'gray'
            elif flag & irsdk.Flags.red:
                flag_color = 'red'
            elif flag & irsdk.Flags.white:
                flag_color = 'white'
            elif flag & irsdk.Flags.yellow or flag & irsdk.Flags.yellow_waving \
                 or flag & irsdk.Flags.caution or flag & irsdk.Flags.caution_waving \
                 or flag & irsdk.Flags.debris:
                flag_color = 'yellow'
            elif flag & irsdk.Flags.green or flag & irsdk.Flags.green_held:
                flag_color = 'green'
            else:
                flag_color = 'green'

        return flag_color, flag & irsdk.Flags.repair

    def pit_penalty(self, car_num):
        if car_num == self.ir["DriverInfo"]["Drivers"][0]["CarNumberRaw"]:
            penalty = random.choice(self.penalties_player)
        else:
            penalty = random.choice(self.penalties)

        flag_color, _meatball = self._get_flag(self.ir['SessionFlags'])

        if flag_color == "green":
            print(f"Passthrough for #{car_num}: {penalty}")
            self.ir.chat_command(f"!bl {car_num} D")
            self.ir.chat_command(f"PENALTY #{car_num}: {penalty}")
        elif flag_color == "yellow":
            print(f"EOL for #{car_num}: {penalty}")
            self.ir.chat_command(f"!eol {car_num} PENALTY #{car_num}: {penalty}")

    # disqualify all cars who are named NO DRIVER
    def practice(self):
        dq_drivers = [driver["CarNumberRaw"] for driver in
                      self.ir["DriverInfo"]["Drivers"] if
                      driver["UserName"] == "NO DRIVER"]
        for number in dq_drivers:
            self.ir.chat_command(f"!dq {number} - car unused this week")

    # identify when the session is QUALIFYING
    def qualifying(self):
        qual_done = False
        while qual_done is False:
            self.ir.freeze_var_buffer_latest()
            if self.ir["SessionState"] != 6:
                print("waiting..")
                time.sleep(1)
            else:
                for position in self.ir["QualifyResultsInfo"]["Results"]:
                    if position["Position"] > self.field_size:
                        match = [driver["CarNumberRaw"] for driver in
                                 self.ir["DriverInfo"]["Drivers"] if
                                 driver["CarIdx"] == position["CarIdx"]][0]
                        self.ir.chat_command(f"!dq {match} - #{match} Missed the race")
                qual_done = True

    def _issue_pre_race_penalty(self, car_num):
        penalty = random.choice(self.pre_race_penalties)
        if penalty == "Failed Inspection x2":
            print(f"!eol {car_num} - #{car_num} to the rear: {penalty}")
            self.ir.chat_command(f"!eol {car_num} - #{car_num} to the rear: {penalty}")
        elif penalty == "Failed Inspection x3":
            print(f"!eol {car_num} - #{car_num} to the rear: {penalty}")
            print(f"!bl {car_num} D")
            self.ir.chat_command(f"!eol {car_num} - #{car_num} to the rear: {penalty}")
            self.ir.chat_command(f"!bl {car_num} D")
        elif penalty == "Unapproved Adjustments":
            print(f"!eol {car_num} - #{car_num} to the rear: {penalty}")
            self.ir.chat_command(f"!eol {car_num} - #{car_num} to the rear: {penalty}")

    def _pre_race_penalties(self):
        for driver in self.ir["DriverInfo"]["Drivers"]:
            if driver["CarIsPaceCar"] != 1:
                if random.randint(1, 100) < self.pre_race_penalty_chance:
                    self._issue_pre_race_penalty(driver["CarNumberRaw"])

    # identify when the session is RACE
    def race(self):
        self.ir.freeze_var_buffer_latest()
        self._pre_race_penalties()
        pit_tracking = []
        while True:
            if self.ir["Lap"] > -1:
                self.ir.freeze_var_buffer_latest()
                # get all cars currently on pit road
                cars_on_pit_road = [driver["CarNumberRaw"] for driver
                                    in self.ir["DriverInfo"]["Drivers"]
                                    if self.ir["CarIdxOnPitRoad"][driver["CarIdx"]
                                    and driver["UserName"] != "Pace Car"]
                                    is True]
                # if there is at least 1 car on pit road
                if len(cars_on_pit_road) > 0:
                    # for each car in this pulled instance
                    for car_num in cars_on_pit_road:
                        # if the car has not been processed this cycle
                        if car_num not in pit_tracking:
                            # track the car number
                            pit_tracking.append(car_num)
                            # calculate penalty chance
                            if random.randint(1, 100) < self.penalty_chance:
                                self.pit_penalty(car_num)
                        # if the car has already been processed, skip it
                        else:
                            continue
                    # check if any cars need to be removed from tracking
                    for car in pit_tracking:
                        if car not in cars_on_pit_road:
                            pit_tracking.remove(car)
                else:
                    pit_tracking = []
                    time.sleep(1)
            else:
                time.sleep(1)

    def main(self):
        practice = False
        qualifying = False
        race = False

        while practice is False:
            if self.ir["SessionNum"] == 0:
                self.practice()
                print("Practice is done")
                practice = True
            else:
                time.sleep(1)
        while qualifying is False:
            if self.ir["SessionNum"] == 1:
                self.qualifying()
                print("Qualifying is done")
                qualifying = True
            else:
                time.sleep(1)
        while race is False:
            if self.ir["SessionNum"] == 2:
                self.race()
                race = True
            else:
                time.sleep(1)

if __name__ == "__main__":
    iRacing()
