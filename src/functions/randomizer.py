"""
Details to come...
"""

## Standard library imports
import json
import logging
import os
import random
import sys
from datetime import date
from os.path import exists
from pathlib import Path
from shutil import copyfile

## Third party imports
import dateutil.parser as dparser

## Local imports
sys.path.append(f"{str(Path.cwd())}/src")
from assets.misc.data_converter import convert_car_driver_mapping, convert_drivers

## Global vars
logger = logging.getLogger(__name__)

date_format = "%B %d, %Y"
today = date.today()


class Car:
    def __init__(self, number: int, car_info: tuple):
        self.number = number
        self.team = car_info.get("team")
        self.status = car_info.get("car_status")
        self.car_tier = car_info.get("car_tier")
        self.pit_crew_tier = car_info.get("pitcrew_tier")
        self.strategy_tier = car_info.get("strategy_tier")


class Driver:
    def __init__(self, randomizer: object, car_entry: dict) -> None:
        self.car = Car(
            car_entry.get("carNumber"),
            randomizer.car_assigns[car_entry.get("carNumber")],
        )
        self.name = self._assign_driver(randomizer, car_entry)
        self.driver_skill = (
            0
            if f"NODRIVER{self.car.number}" == self.name
            else car_entry.get("driverSkill")
        )
        self.aggression = (
            0
            if f"NODRIVER{self.car.number}" == self.name
            else car_entry.get("driverAggression")
        )
        self.optimism = (
            0
            if f"NODRIVER{self.car.number}" == self.name
            else car_entry.get("driverOptimism")
        )
        self.smoothness = (
            0
            if f"NODRIVER{self.car.number}" == self.name
            else car_entry.get("driverSmoothness")
        )
        self.pit_skill = (
            0
            if f"NODRIVER{self.car.number}" == self.name
            else car_entry.get("pitCrewSkill")
        )
        self.strategy = (
            0
            if f"NODRIVER{self.car.number}" == self.name
            else car_entry.get("strategyRiskiness")
        )
        self.age = (
            0
            if f"NODRIVER{self.car.number}" == self.name
            else self._calc_driver_age(randomizer)
        )
        self.tier = (
            None
            if f"NODRIVER{self.car.number}" == self.name
            else randomizer.drivers[self.name].get(f"{randomizer.season_data.get("season_series")}_TIER")
        )

    def _assign_driver(self, randomizer: object, car_entry: dict) -> str:
        week_driver = randomizer.car_assigns[car_entry.get("carNumber")]
        if week_driver.get("fulltime_driver") is None and week_driver.get("assigned_drivers").get(f"WEEK_{randomizer.week}") is None:
            return f"NODRIVER{self.car.number}"
        elif week_driver.get("fulltime_driver") is not None:
            return week_driver.get("fulltime_driver")
        elif week_driver.get("assigned_drivers").get(f"WEEK_{randomizer.week}") is None:
            return f"NODRIVER{self.car.number}"
        else:
            return week_driver.get("assigned_drivers").get(f"WEEK_{randomizer.week}")

    def _calc_driver_age(self, randomizer: object) -> int:
        try:
            date_obj = dparser.parse(
                randomizer.drivers[self.name].get("BIRTHDAY"),
                fuzzy=True,
            ).date()
        except IndexError:
            print(self.car.number)
            logger.error(
                f"Error with {self.name} - either invalid name or birthday, defaulting to 50"
            )
            return 50
        return (
            today.year
            - date_obj.year
            - ((today.month, today.day) < (date_obj.month, date_obj.day))
        )


class Randomizer:
    def __init__(
        self,
        season_data: dict,
        week: int,
        random_paints: bool = True,
    ):
        self.season_data = season_data
        self.roster_path = Path(season_data.get("iracing_roster_file"))
        self.roster = {}
        self.drivers = convert_drivers(season_data.get("season_series"))
        self.car_assigns = convert_car_driver_mapping(season_data.get("season_series"))
        self.week = week
        self.randomize_paints = random_paints
        self._randomize()

    def _randomize(self) -> None:
        self._load_roster()
        self._assign_and_randomize_drivers()
        self._write_changes_to_file()

    def _load_roster(self) -> None:
        with open(self.roster_path / "roster.json", "r") as roster_file:
            self.roster = json.loads(roster_file.read())

    def _assign_and_randomize_drivers(self) -> None:
        for car_entry in self.roster["drivers"]:
            roster_driver = Driver(self, car_entry)
            car_entry["driverName"] = roster_driver.name
            if "NODRIVER" not in roster_driver.name:
                roster_driver_updated = self._randomize_attributes(roster_driver)
                car_entry["driverSkill"] = roster_driver_updated.driver_skill
                car_entry["driverAggression"] = roster_driver_updated.aggression
                car_entry["driverOptimism"] = roster_driver_updated.optimism
                car_entry["driverSmoothness"] = roster_driver_updated.smoothness
                car_entry["pitCrewSkill"] = roster_driver_updated.pit_skill
                car_entry["strategyRiskiness"] = roster_driver_updated.strategy
                car_entry["driverAge"] = roster_driver_updated.age
                if self.randomize_paints is True:
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
        roster_driver.optimism = -500
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
            paint_files = os.listdir(
                self.roster_path / roster_driver_updated.car.number
            )
        except FileNotFoundError:
            logger.warning(f"No folder found for {roster_driver_updated.car.number}")
            return

        if len(paint_files) == 1:
            logger.debug(
                f"No alternate schemes found for {roster_driver_updated.car.number}"
            )
            if not exists(self.roster_path / f"{roster_driver_updated.car.number}.tga"):
                logger.debug(
                    f"{roster_driver_updated.car.number}.tga doesn't exist, creating"
                )
                new_paint_file = (
                    self.roster_path
                    / roster_driver_updated.car.number
                    / [file for file in paint_files][0]
                )
            else:
                return
        else:
            driver_paints = [
                file
                for file in paint_files
                if roster_driver_updated.name.lower().replace(" ", "_") in file
            ]
            if len(driver_paints) == 0:
                try:
                    new_paint_file = (
                        self.roster_path
                        / roster_driver_updated.car.number
                        / random.choice(paint_files)
                    )
                except IndexError:
                    logging.debug(
                        f"No paint files found for {roster_driver_updated.car.number}"
                    )
                    return
            else:
                new_paint_file = (
                    self.roster_path
                    / roster_driver_updated.car.number
                    / driver_paints[0]
                )

            logger.info(f"Selected {str(new_paint_file).split('\\')[-1]}")

        logger.debug(f"Attempting to copy file {new_paint_file}")
        try:
            copyfile(
                new_paint_file,
                self.roster_path / f"car_{roster_driver_updated.car.number}.tga",
            )
            logger.info(
                f"Sucessfully copied to {self.roster_path}\\car_{roster_driver_updated.car.number}.tga"
            )
        except:
            logger.warning("Uncategorized error, skipping copy operation")
            return

    def _write_changes_to_file(self) -> None:
        with open(self.roster_path / "roster.json", "w", encoding="utf-8") as roster_file:
            logger.info("Writing changes to file")
            json.dump(self.roster, roster_file, ensure_ascii=False, indent=4)
