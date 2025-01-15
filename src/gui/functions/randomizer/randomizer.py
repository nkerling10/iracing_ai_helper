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
        self.driver_skill = 0 if f"NODRIVER{self.car.number}" == self.name else car_entry.get("driverSkill")
        self.aggression = 0 if f"NODRIVER{self.car.number}" == self.name else car_entry.get("driverAggression")
        self.optimism = 0 if f"NODRIVER{self.car.number}" == self.name else car_entry.get("driverOptimism")
        self.smoothness = 0 if f"NODRIVER{self.car.number}" == self.name else car_entry.get("driverSmoothness")
        self.pit_skill = 0 if f"NODRIVER{self.car.number}" == self.name else car_entry.get("pitCrewSkill")
        self.strategy = 0 if f"NODRIVER{self.car.number}" == self.name else car_entry.get("strategyRiskiness")
        self.age = 0 if f"NODRIVER{self.car.number}" == self.name else self._calc_driver_age(randomizer)
        self.tier = None if f"NODRIVER{self.car.number}" == self.name \
                    else [driver[randomizer.driver_table_columns.index(f"{randomizer.season_settings.get('season_series')}_TIER")]
                    for driver in randomizer.drivers if self.name == driver[0]][0]
        
    def _assign_driver(self, randomizer: object, car_entry: dict) -> str:
        week_driver = [pair for pair in randomizer.car_assigns if pair[0] == self.car.number]
        if week_driver:
            if week_driver[0][1] is None:
                return f"NODRIVER{self.car.number}"
            else:
                return week_driver[0][1]

        return car_entry.get("driverName")

    def _calc_driver_age(self, randomizer: object) -> int:
        try:
            date_obj = dparser.parse([driver[randomizer.driver_table_columns.index("BIRTHDAY")] for driver in
                                        randomizer.drivers if self.name == driver[0]][0], fuzzy=True).date()
        except IndexError:
            print(self.name)
            quit()
        return today.year - date_obj.year - ((today.month, today.day) < (date_obj.month, date_obj.day))


class Randomizer:
    def __init__(self, config, season_settings, db, random_paints=True):
        self.db = db
        self.config = config
        self.season_settings = season_settings
        self.roster_path = self.config.iracing_folder / "airosters" / self.season_settings.get("roster_name")
        self.roster = {}
        self.roster_prev = {}
        self.drivers = []
        self.driver_table_columns = []
        self.cars = []
        self.car_assigns = []
        self.randomize_paints = random_paints
        self._randomize()

    def _randomize(self) -> None:
        # 1. load roster file
        # DONE
        self._load_roster()
        # 2. pull required data
        # DONE
        self._pull_required_data()
        # 3. assign drivers for the race and randomize driver attributes
        # DONE
        self._assign_and_randomize_drivers()
        # 5. store data for comparison (+/- from last week, maybe a historical record week by week)
        #self._store_driver_attribute_compare()
        # 6. write changes to file
        # DONE
        self._write_changes_to_file()

    def _load_roster(self) -> None:
        with open(self.roster_path / "roster.json", "r") as roster_file:
            self.roster = json.loads(roster_file.read())
            self.roster_prev = self.roster

    def _pull_required_data(self) -> None:
        self.drivers = self.db.execute_select_columns_query("DRIVER")
        self.driver_table_columns = self.db._get_db_table_columns("DRIVER")
        self.cars = self.db.execute_select_columns_query(f"CAR_{self.season_settings.get('season_series')}")
        self.car_assigns = self.db.execute_select_columns_query(table=f"{self.season_settings.get('season_series')}_DRIVER_CAR_MAPPING", columns="CAR, WEEK_1")

    def _assign_and_randomize_drivers(self) -> None:
        for car_entry in self.roster["drivers"]:
            roster_driver = Driver(self, car_entry)
            roster_driver_updated = self._randomize_attributes(roster_driver)
            car_entry["driverName"] = roster_driver_updated.name
            car_entry["driverSkill"] = roster_driver_updated.driver_skill
            car_entry["driverAggression"] = roster_driver_updated.aggression
            car_entry["driverOptimism"] = roster_driver_updated.optimism
            car_entry["driverSmoothness"] = roster_driver_updated.smoothness
            car_entry["pitCrewSkill"] = roster_driver_updated.pit_skill
            car_entry["strategyRiskiness"] = roster_driver_updated.strategy
            car_entry["driverAge"] = roster_driver_updated.age
            if self.randomize_paints is True and "NODRIVER" not in roster_driver_updated.name:
                self._randomize_paint_scheme(roster_driver_updated)


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
            roster_driver.smoothness = random.randint(35, 65)
        elif roster_driver.car.car_tier == 2:
            roster_driver.smoothness = random.randint(25, 75)
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


    def _randomize_paint_scheme(self, roster_driver_updated: object) -> str:
        try:
            paint_files = os.listdir(self.roster_path / roster_driver_updated.car.number)
        except FileNotFoundError:
            logger.warning(f"No folder found for {roster_driver_updated.car.number}")
            return

        if len(paint_files) == 1:
            logger.debug(f"No alternate schemes found for {roster_driver_updated.car.number}")
            return
        else:
            driver_paints = [file for file in paint_files if roster_driver_updated.name.lower().replace(" ", "_") in file]
            if len(driver_paints) == 0:
                try:
                    new_paint_file =self.roster_path / roster_driver_updated.car.number / random.choice(paint_files)
                except IndexError:
                    logging.debug(f"No paint files found for {roster_driver_updated.car.number}")
                    return
            else:
                new_paint_file = self.roster_path / roster_driver_updated.car.number / driver_paints[0]

            logger.info(f"Selected {str(new_paint_file).split('\\')[-1]}")

        logger.debug(f"Attempting to copy file {new_paint_file}")
        try:
            copyfile(new_paint_file, self.roster_path / f"car_{roster_driver_updated.car.number}.tga")
            logger.info(f"Sucessfully copied to {self.roster_path} / car_{roster_driver_updated.car.number}.tga")
        except:
            logger.warning("Uncategorized error, skipping copy operation")
            return


    def _store_driver_attribute_compare(self):
        pass


    def _write_changes_to_file(self) -> None:
        with open(self.roster_path / "roster.json",
                   "w", encoding="utf-8") as roster_file:
            logger.info("Writing changes to file")
            json.dump(self.roster, roster_file, ensure_ascii=False, indent=4)


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
    Randomizer()
