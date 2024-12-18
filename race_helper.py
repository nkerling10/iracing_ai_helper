import irsdk
import time
import random
from enum import Enum
# https://github.com/kutu/pyirsdk/blob/master/tutorials/02%20Using%20irsdk%20script.md

class IRacingMemoryFlagType(Enum):
    # global flags
    checkered = 0x0001
    white = 0x0002
    green = 0x0004
    yellow = 0x0008
    red = 0x0010
    blue = 0x0020
    debris = 0x0040
    crossed = 0x0080
    yellow_waving = 0x0100
    one_lap_to_green = 0x0200
    green_held = 0x0400
    ten_to_go = 0x0800
    five_to_go = 0x1000
    random_waving = 0x2000
    caution = 0x4000
    caution_waving = 0x8000

    # drivers black flags
    black = 0x010000
    disqualify = 0x020000
    servicible = 0x040000  # car is allowed service (not a flag)
    furled = 0x080000
    repair = 0x100000

    # start lights
    start_hidden = 0x10000000
    start_ready = 0x20000000
    start_set = 0x40000000
    start_go = 0x80000000

class IRacingGUIFlagType(Enum):
    IRACING_NO_FLAG = 0
    IRACING_BLUE_FLAG = 1
    IRACING_MEATBALL_FLAG = 2
    IRACING_BLACK_FLAG = 3
    IRACING_YELLOW_FLAG = 4
    IRACING_GREEN_FLAG = 5
    IRACING_WHITE_FLAG = 6
    IRACING_CHEQUERED_FLAG = 7
    IRACING_RED_FLAG = 8


class iRacing:
    def __init__(self):
        self.field_size = 41
        self.penalty_chance = 8
        self.penalties = ["Speeding - Too fast entering",
                          "Speeding - Too fast exiting",
                          "Crew members over the wall too soon",
                          "Too many men over the wall",
                          "Tire violation"]
        self.penalty_log = {}
        self.ir = irsdk.IRSDK()
        self.ir.startup(test_file='session_data/data_qualify.bin')
        self.main()

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
                        self.ir.chat_command(f"!dq {match} - Missed the race")
                qual_done = True

    # identify when the session is RACE
    def race(self):
        self.pit_penalty(10, 0, 0)
        quit()

        while True:
            self.ir.freeze_var_buffer_latest()
            if self.ir["Lap"] > -2:
                cars_on_pit_road = [[driver["CarNumberRaw"], driver["CarIdx"]]
                                    for driver in self.ir["DriverInfo"]["Drivers"]
                                    if self.ir["CarIdxOnPitRoad"][driver["CarIdx"]]
                                    is True]
                if len (cars_on_pit_road) > 0:
                    for car_num, car_idx in cars_on_pit_road:
                        car_is_on_lap = self.ir["CarIdxLap"][car_idx]
                        if car_idx not in self.penalty_log:
                            self.penalty_log[car_idx] = {}
                        if car_is_on_lap in self.penalty_log[car_idx]:
                            continue
                        self.penalty_log[car_idx].update({car_is_on_lap: ""})
                        if random.randint(1, 100) < self.penalty_chance:
                            self.pit_penalty(car_num, car_idx, car_is_on_lap)
            else:
                time.sleep(1)

    def pit_penalty(self, car_num, car_idx, car_is_on_lap):
        memory_flags = []
        active_flags = []

        penalty = random.choice(self.penalties)

        session_flag = self.ir["SessionFlags"]
        print(session_flag)
        for flag in IRacingMemoryFlagType:
            if IRacingMemoryFlagType(flag).value and session_flag == IRacingMemoryFlagType(flag).value:
                print(flag)
                memory_flags.append(flag)
        print(memory_flags)
        if IRacingMemoryFlagType.yellow in memory_flags or IRacingMemoryFlagType.yellow_waving in memory_flags:
            active_flags.append(IRacingGUIFlagType.IRACING_YELLOW_FLAG)

        print(active_flags)
        quit()
        if len(active_flags) == 0 or len(active_flags) > 1:
            print(f"Passthrough for {car_num}: {penalty}")
            #self.ir.chat_command(f"!bl {car_num} D")
            #self.ir.chat_command(f"PENALTY #{car_num}: {penalty}")
        elif active_flags[0] == "yellow":
            print(f"EOL for {car_num}: {penalty}")
            #self.ir.chat_command(f"!eol {car_num} PENALTY #{car_num}: {penalty}")

        self.penalty_log[car_idx].update({car_is_on_lap: penalty})


    def main(self):
        practice = False
        qualifying = False
        race = False
        """
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
        """
        while race is False:
            if self.ir["SessionNum"] == 0:
                self.race()
                race = True
            else:
                time.sleep(1)

if __name__ == "__main__":
    iRacing()