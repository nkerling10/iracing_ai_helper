"""
Details to come...
"""

## Standard library imports
import json
import logging
import os
import random
import sqlite3
from datetime import date
from pathlib import Path
from shutil import copyfile

## Third party imports
import dateutil.parser as dparser

## Local imports

## Global vars
logger = logging.getLogger(__name__)
date_format = "%B %d, %Y"
today = date.today()
ai_roster_path = Path.home() / "Documents" / "iRacing" / "airosters"
standard_file_path = f"{os.getcwd()}/src/gui/functions/roster/randomizer/files"

DRIVER_NAME_COLUMN = 0
DRIVER_BIRTHDAY_COLUMN = 1
DRIVER_SPECIALTY_COLUMN = 3
CUP_TIER_COLUMN = 4
XFINITY_TIER_COLUMN = 5
TRUCKS_TIER_COLUMN = 6
ARCA_TIER_COLUMN = 7

class Car:
    def __init__(self, number: int, car_info: tuple):
        self.number = number
        self.team = car_info[1]
        self.status = car_info[2]
        self.car_tier = car_info[3]
        self.pit_crew_tier = car_info[4]
        self.strategy_tier = car_info[5]

class Driver:
    def __init__(self, randomizer: object, car_entry: dict) -> None:
        self.car = Car(car_entry.get("carNumber"),
                       [car for car in randomizer.cars if car[0] == car_entry.get("carNumber")][0])
        self.name = self._assign_driver(randomizer, car_entry)
        self.driver_skill = 0 if f"NODRIVER{self.car}" == self.name else car_entry.get("driverSkill")
        self.aggression = 0 if f"NODRIVER{self.car}" == self.name else car_entry.get("driverAggression")
        self.optimism = 0 if f"NODRIVER{self.car}" == self.name else car_entry.get("driverOptimism")
        self.smoothness = 0 if f"NODRIVER{self.car}" == self.name else car_entry.get("driverSmoothness")
        self.pit_skill = 0 if f"NODRIVER{self.car}" == self.name else car_entry.get("pitCrewSkill")
        self.strategy = 0 if f"NODRIVER{self.car}" == self.name else car_entry.get("strategyRiskiness")
        self.age = 0 if f"NODRIVER{self.car}" == self.name else self._calc_driver_age(randomizer)
        self.paint_file = car_entry.get("carTgaName")
        self.tier = None if f"NODRIVER{self.car}" == self.name \
                    else [driver[randomizer.driver_table_columns.index(f"{randomizer.series}_TIER")]
                    for driver in randomizer.drivers if self.name == driver[0]][0]
        
    def _assign_driver(self, randomizer: object, car_entry: dict) -> str:
        week_driver = [pair for pair in randomizer.car_assigns if pair[0] == self.car]
        if week_driver:
            if week_driver[0][1] != None:
                return week_driver[0][1]
            return f"NODRIVER{self.car}"
        return car_entry.get("driverName")

    def _calc_driver_age(self, randomizer: object) -> int:
        date_obj = dparser.parse([driver[randomizer.driver_table_columns.index("BIRTHDAY")] for driver in
                                  randomizer.drivers if self.name == driver[0]][0], fuzzy=True).date()
        return today.year - date_obj.year - ((today.month, today.day) < (date_obj.month, date_obj.day))


class Randomizer:
    def __init__(self, config: object, series: str, single_race: bool, db: object=None):
        self.db = db
        self.config = config
        self.series = series
        self.roster = {}
        self.roster_prev = {}
        self.drivers = []
        self.driver_table_columns = []
        self.cars = []
        self.car_assigns = []
        self._randomize(single_race)

    def _randomize(self, mode: str):
        # 1. load roster file
        # DONE
        self._load_roster(mode)
        # 2. pull required data
        # DONE
        self._pull_required_data()
        # 3. assign drivers for the race and randomize driver attributes
        self._assign_and_randomize_drivers()
        # 4. randomize paint schemes
        self._randomize_paints()
        # 5. store data for comparison (+/- from last week, maybe a historical record week by week)
        self._store_driver_attribute_compare()
        # 6. write changes to file
        self._write_changes_to_file()

    def _load_roster(self, single_race=True) -> None:
        local_file = Path.cwd() / "base_files" / "rosters" / "2025_Xfinity_Series" / "roster.json"
        with open(local_file if single_race is True else self.config.season_file, "r") as roster_file:
            self.roster = json.loads(roster_file.read())
            self.roster_prev = self.roster

    def _pull_required_data(self):
        self.drivers = self.db.execute(f"SELECT * FROM DRIVER").fetchall()
        self.driver_table_columns = [column[1] for column in self.db.execute(f"PRAGMA table_info(DRIVER);").fetchall()]
        self.cars = self.db.execute(f"SELECT * FROM CAR_{self.series}").fetchall()
        self.car_assigns = self.db.execute(
            f"SELECT CAR, WEEK_1 FROM {self.series}_DRIVER_CAR_MAPPING").fetchall()

    def _assign_and_randomize_drivers(self):
        for car_entry in self.roster["drivers"]:
            roster_driver = Driver(self, car_entry)
            #randomize attributes
            roster_driver_updated = self._randomize_attributes(roster_driver)
            print(f"{roster_driver_updated.name}: Skill {roster_driver_updated.driver_skill}")
            #update values
            #car_entry = self._update_roster_car_entry(roster_driver_updated, car_entry)
        quit()

    @staticmethod
    def _randomize_attributes(roster_driver: dict) -> dict:
        # randomize skill
        if roster_driver.tier == 1:
            roster_driver.driver_skill = random.randint(95, 100)
        elif roster_driver.tier == 2:
            roster_driver.driver_skill = random.randint(90, 97)
        elif roster_driver.tier == 3:
            roster_driver.driver_skill = random.randint(85, 92)
        elif roster_driver.tier == 4:
            roster_driver.driver_skill = random.randint(80, 87)
        elif roster_driver.tier == 5:
            roster_driver.driver_skill = random.randint(75, 80)
        elif roster_driver.tier == 6:
            roster_driver.driver_skill = random.randint(70, 75)
        elif roster_driver.tier == 7:
            roster_driver.driver_skill = random.randint(60, 69)
        elif roster_driver.tier == 8:
            roster_driver.driver_skill = random.randint(50, 59)
        # randomize aggression*** this is static set for testing
        roster_driver.aggression = 999
        # randomize optimism*** this is static set for testing
        roster_driver.optimism = 500
        # randomize smoothness
        # iracing scale of 0-100 (loose -> tight), midpoint of 50
        if roster_driver.car.car_tier == 1:
            roster_driver.smoothness = random.randint(40, 60)
        elif roster_driver.car.car_tier == 2:
            roster_driver.smoothness = random.randint(20, 80)
        elif roster_driver.car.car_tier == 3:
            roster_driver.smoothness = random.randint(0, 100)
        elif roster_driver.car.car_tier == 4:
            roster_driver.smoothness = random.randint(-50, 150)
        elif roster_driver.car.car_tier == 5:
            roster_driver.smoothness = random.randint(-100, 200)
        # randomize pit skill
        if roster_driver.car.pit_crew_tier == 1:
            roster_driver.pit_skill = random.randint(90, 100)
        elif roster_driver.car.pit_crew_tier == 2:
            roster_driver.pit_skill = random.randint(80, 90)
        elif roster_driver.car.pit_crew_tier == 3:
            roster_driver.pit_skill = random.randint(70, 80)
        elif roster_driver.car.pit_crew_tier == 4:
            roster_driver.pit_skill = random.randint(60, 70)
        elif roster_driver.car.pit_crew_tier == 5:
            roster_driver.pit_skill = random.randint(50, 60)
        # randomize strategy riskiness
        if roster_driver.car.strategy_tier == 1:
            roster_driver.strategy = random.randint(25, 50)
        elif roster_driver.car.strategy_tier == 2:
            roster_driver.strategy = random.randint(35, 65)
        elif roster_driver.car.strategy_tier == 3:
            roster_driver.strategy = random.randint(50, 75)
        elif roster_driver.car.strategy_tier == 4:
            roster_driver.strategy = random.randint(65, 85)
        elif roster_driver.car.strategy_tier == 5:
            roster_driver.strategy = random.randint(75, 100)
        
        return roster_driver

    @staticmethod
    def _update_roster_car_entry(roster_driver: dict, car_entry: dict) -> dict:
        car_entry["driverName"] = roster_driver.driver_name
        car_entry["driverSkill"] = roster_driver.driver_skill
        car_entry["driverAggression"] = roster_driver.aggression
        car_entry["driverOptimism"] = roster_driver.optimism
        car_entry["driverSmoothness"] = roster_driver.smoothness
        car_entry["pitCrewSkill"] = roster_driver.pit_skill
        car_entry["strategyRiskiness"] = roster_driver.strategy
        car_entry["driverAge"] = roster_driver.age

        return car_entry

    def _randomize_paints(self):
        pass

    def _store_driver_attribute_compare(self):
        pass

    def _write_changes_to_file(self):
        with open("", "w", encoding="utf-8") as roster_file:
            logger.info("Writing changes to file")
            json.dump(driver_list, roster_file, ensure_ascii=False, indent=4)



def set_attributes(driver_name, car, driver_tiers, car_list, driver_birthdays):
    if car_list[car]["car_tier"] == 1:
        car_smoothness = random.randint(25, 75)
    elif car_list[car]["car_tier"] == 2:
        car_smoothness = random.randint(0, 100)
    elif car_list[car]["car_tier"] == 3:
        car_smoothness = random.randint(-100, 150)
    elif car_list[car]["car_tier"] == 4:
        car_smoothness = random.randint(-150, 200)
    else:
        logger.critical(f"Fix car tier for {car} in car file!")
        return

    if car_list[car]["crew_tier"] == 1:
        pit_min = 90
        pit_max = 100
        strategy_min = 1
        strategy_max = 20
    elif car_list[car]["crew_tier"] == 2:
        pit_min = 80
        pit_max = 90
        strategy_min = 10
        strategy_max = 25
    elif car_list[car]["crew_tier"] == 3:
        pit_min = 70
        pit_max = 80
        strategy_min = 20
        strategy_max = 50
    elif car_list[car]["crew_tier"] == 4:
        pit_min = 60
        pit_max = 70
        strategy_min = 50
        strategy_max = 100
    else:
        logger.critical(f"Fix crew tier for {car} in car file!")
        return

    driverSkill = random.randint(skill_min, skill_max)
    driverAggression = 999
    driverOptimism = 500
    driverSmoothness = car_smoothness
    driverAge = _get_driver_age(driver_name, driver_birthdays)
    pitCrewSkill = random.randint(pit_min, pit_max)
    strategyRiskiness = random.randint(strategy_min, strategy_max)

    set_driver = Driver(
        driver_name,
        car,
        [
            driverSkill,
            driverAggression,
            driverOptimism,
            driverSmoothness,
            driverAge,
            pitCrewSkill,
            strategyRiskiness,
        ],
    )

    return set_driver


def change_paint_scheme(car_num, driver_name, roster_path):
    roster_dir = Path(roster_path).parent
    try:
        paint_files = os.listdir(Path(f"{roster_dir}\\{car_num}"))
    except FileNotFoundError:
        logger.warning(f"No folder found for {car_num}")
        return

    if len(paint_files) == 1:
        logger.debug(f"No alternate schemes found for {car_num}")
        return
    else:
        driver_paints = [file for file in paint_files if driver_name.lower().replace(" ", "_") in file]
        if len(driver_paints) == 0:
            try:
                new_paint_file = Path(f"{roster_dir}\\{car_num}\\{random.choice(paint_files)}")
            except IndexError:
                logging.debug(f"No paint files found for {car_num}")
                return
        else:
            new_paint_file = Path(f"{roster_dir}\\{car_num}\\{driver_paints[0]}")

        logger.info(f"Selected {str(new_paint_file).split('\\')[-1]}")

    logger.debug(f"Attempting to copy file {new_paint_file}")
    try:
        copyfile(new_paint_file, Path(f"{roster_dir}\\car_{car_num}.tga"))
        logger.info(f"Sucessfully copied to {Path(f"{roster_dir}\\car_{car_num}.tga")}")
    except:
        logger.warning("Uncategorized error, skipping copy operation")
        return


def perform_copy(roster_path):
    roster_dir = Path(roster_path).parent
    roster_name = roster_path.split("\\")[-2]
    logger.info(f"Copying paints and roster from {roster_dir} into {ai_roster_path}/{roster_name}")
    copy_files = [file for file in os.listdir(Path(roster_dir)) if ".tga" in file or ".json" in file]
    for file in copy_files:
        try:
            copyfile(Path(f"{roster_dir}\\{file}"), Path(ai_roster_path / roster_name / file))
            logger.info(f"{file} copied successfully!")
        except Exception as e:
            logger.critical(e)
            continue


if __name__ == "__main__":
    conn = sqlite3.connect("C:\\Users\\Nick\\Documents\\iracing_ai_helper\\database\\iracing_ai_helper.db")
    cursor = conn.cursor()
    Randomizer(config=None, series="XFINITY", single_race=True, db=cursor)
