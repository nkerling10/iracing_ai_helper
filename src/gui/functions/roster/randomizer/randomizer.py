"""
Details to come...
"""

## Standard library imports
import json
import logging
import os
import random
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


class Driver:
    def __init__(self, name, car, attributes) -> None:
        self.name = name
        self.car = car
        self.driver_skill = attributes[0]
        self.aggression = attributes[1]
        self.optimism = attributes[2]
        self.smoothness = attributes[3]
        self.age = attributes[4]
        self.pit_skill = attributes[5]
        self.strategy = attributes[6]


def get_driver_age(driver_name, driver_birthdays):
    date_obj = dparser.parse(
        driver_birthdays.get(driver_name).get("birthday"), fuzzy=True
    ).date()
    return (
        today.year
        - date_obj.year
        - ((today.month, today.day) < (date_obj.month, date_obj.day))
    )


def set_attributes(driver_name, car, driver_tiers, car_list, driver_birthdays):
    if driver_name in driver_tiers["tier_1"]:
        skill_min = 91
        skill_max = 100
    elif driver_name in driver_tiers["tier_2"]:
        skill_min = 81
        skill_max = 90
    elif driver_name in driver_tiers["tier_3"]:
        skill_min = 71
        skill_max = 80
    elif driver_name in driver_tiers["tier_4"]:
        skill_min = 61
        skill_max = 70
    elif driver_name in driver_tiers["tier_5"]:
        skill_min = 51
        skill_max = 60
    elif driver_name in driver_tiers["tier_6"]:
        skill_min = 45
        skill_max = 55
    else:
        logger.critical(f"{driver_name} not found in tier file, fix it!")
        return

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
    driverAge = get_driver_age(driver_name, driver_birthdays)
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
        driver_paints = [
            file
            for file in paint_files
            if driver_name.lower().replace(" ", "_") in file
        ]
        if len(driver_paints) == 0:
            try:
                new_paint_file = Path(
                    f"{roster_dir}\\{car_num}\\{random.choice(paint_files)}"
                )
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


def open_files():
    with open(Path(f"{standard_file_path}/driver_tiers.json"), "r") as tier_file:
        driver_tiers = json.loads(tier_file.read())
    with open(Path(f"{standard_file_path}/cars.json"), "r") as car_file:
        car_list = json.loads(car_file.read())
    with open(Path(f"{standard_file_path}/schedule.json"), "r") as schedule_file:
        schedule_list = json.loads(schedule_file.read())
    with open(Path(f"{standard_file_path}/drivers.json"), "r") as driver_file:
        driver_birthdays = json.loads(driver_file.read())
    return driver_tiers, car_list, schedule_list, driver_birthdays


def main(race_index, roster_path):
    driver_tiers, car_list, schedule_list, driver_birthdays = open_files()
    with open(Path(roster_path), "r") as roster_file:
        driver_list = json.loads(roster_file.read())
    for roster_driver in driver_list["drivers"]:
        if car_list[roster_driver["carNumber"]]["type"] == "full_time_one_driver":
            logger.info(
                f"Randomizing attributes for {roster_driver['driverName']} - #{roster_driver['carNumber']}"
            )
            new_ratings = set_attributes(
                roster_driver["driverName"],
                roster_driver["carNumber"],
                driver_tiers,
                car_list,
                driver_birthdays,
            )
        elif (
            car_list[roster_driver["carNumber"]]["type"] == "full_time_multiple_drivers"
        ):
            scheduled_driver = schedule_list[race_index]["full_time"][
                roster_driver["carNumber"]
            ]
            if roster_driver["driverName"] != scheduled_driver:
                logger.debug(
                    f"Driver for this week is changing: {roster_driver["driverName"]} -> {scheduled_driver}"
                )
            logger.info(
                f"Randomizing attributes for {scheduled_driver} - #{roster_driver['carNumber']}"
            )
            new_ratings = set_attributes(
                scheduled_driver,
                roster_driver["carNumber"],
                driver_tiers,
                car_list,
                driver_birthdays,
            )
        elif car_list[roster_driver["carNumber"]]["type"] == "part_time":
            try:
                try:
                    scheduled_driver = schedule_list[race_index]["part_time"][
                        roster_driver["carNumber"]
                    ]
                except KeyError:
                    logger.warning(f"{roster_driver["carNumber"]} not found in race {race_index}, aborting")
                    return
                if roster_driver["driverName"] != scheduled_driver:
                    logger.debug(
                        f"Driver for this week is changing: {roster_driver["driverName"]} -> {scheduled_driver}"
                    )
                if not scheduled_driver:
                    logger.info(
                        f"No driver found for #{roster_driver['carNumber']} this week"
                    )
                    roster_driver["driverName"] = (
                        f"NODRIVER{roster_driver['carNumber']}"
                    )
                    continue
            except KeyError:
                logger.info(
                    f"No driver found for #{roster_driver['carNumber']} this week"
                )
                roster_driver["driverName"] = f"NODRIVER{roster_driver['carNumber']}"
                continue

            logger.info(
                f"Randomizing attributes for {scheduled_driver} - #{roster_driver['carNumber']}"
            )
            new_ratings = set_attributes(
                scheduled_driver,
                roster_driver["carNumber"],
                driver_tiers,
                car_list,
                driver_birthdays,
            )

        else:
            continue

        change_paint_scheme(roster_driver["carNumber"], new_ratings.name, roster_path)

        roster_driver["driverName"] = new_ratings.name
        roster_driver["driverSkill"] = new_ratings.driver_skill
        roster_driver["driverAggression"] = new_ratings.aggression
        roster_driver["driverOptimism"] = new_ratings.optimism
        roster_driver["driverSmoothness"] = new_ratings.smoothness
        roster_driver["pitCrewSkill"] = new_ratings.pit_skill
        roster_driver["strategyRiskiness"] = new_ratings.strategy
        roster_driver["driverAge"] = new_ratings.age

    with open(Path(roster_path), "w", encoding="utf-8") as roster_file:
        logger.info("Writing changes to file")
        json.dump(driver_list, roster_file, ensure_ascii=False, indent=4)
    logger.info("Roster write operations are complete")


def perform_copy(roster_path):
    roster_dir = Path(roster_path).parent
    roster_name = roster_path.split("\\")[-2]
    logger.info(
        f"Copying paints and roster from {roster_dir} into {ai_roster_path}/{roster_name}"
    )
    copy_files = [
        file
        for file in os.listdir(Path(roster_dir))
        if ".tga" in file or ".json" in file
    ]
    for file in copy_files:
        try:
            copyfile(
                Path(f"{roster_dir}\\{file}"), Path(ai_roster_path / roster_name / file)
            )
            logger.info(f"{file} copied successfully!")
        except Exception as e:
            logger.critical(e)
            continue
