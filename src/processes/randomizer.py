import json
import random
import os
import wikipediaapi
from pathlib import Path
from datetime import date
import dateutil.parser as dparser
import shutil

date_format = '%B %d, %Y'
today = date.today()

roster_path = Path("rosters")
ai_roster_path = Path.home()/"Documents"/"iRacing"/"airosters"

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

def get_convert_page_data(wiki, driver_name):
    page_py = wiki.page(driver_name)
    born_text = page_py.summary[page_py.summary.find("(")+1:page_py.summary.find(")")]
    date_obj = dparser.parse(born_text,fuzzy=True).date()

    return date_obj

def get_driver_age(driver_name):
    wiki = wikipediaapi.Wikipedia('MyProjectName (merlin@example.com)', 'en')
    if "Leland Honeyman" in driver_name:
        driver_name = "Leland Honeyman"

    try:
        date_obj = get_convert_page_data(wiki, driver_name)
    except ValueError:
        date_obj = get_convert_page_data(wiki, f"{driver_name} (racing driver)")

    return today.year - date_obj.year - ((today.month, today.day) < (date_obj.month, date_obj.day))

def set_attributes(driver_name, car, driver_tiers, car_list):
    if driver_name in driver_tiers["tier_1"]:
        skill_min = 92
        skill_max = 100
    elif driver_name in driver_tiers["tier_2"]:
        skill_min = 85
        skill_max = 95
    elif driver_name in driver_tiers["tier_3"]:
        skill_min = 75
        skill_max = 85
    elif driver_name in driver_tiers["tier_4"]:
        skill_min = 70
        skill_max = 82
    elif driver_name in driver_tiers["tier_5"]:
        skill_min = 62
        skill_max = 72
    elif driver_name in driver_tiers["tier_6"]:
        skill_min = 50
        skill_max = 65
    else:
        print(f"{driver_name} not found, fix it!")
        quit()

    if car_list[car]["car_tier"] == 1:
        car_smoothness = random.randint(25, 75)
    elif car_list[car]["car_tier"] == 2:
        car_smoothness = random.randint(0, 100)
    elif car_list[car]["car_tier"] == 3:
        car_smoothness = random.randint(-100, 150)
    elif car_list[car]["car_tier"] == 4:
        car_smoothness = random.randint(-150, 200)
    else:
        print(f"Fix car tier for {car}!")
        quit()

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
        strategy_min = 15
        strategy_max = 35
    elif car_list[car]["crew_tier"] == 4:
        pit_min = 60
        pit_max = 70
        strategy_min = 50
        strategy_max = 100
    else:
        print(f"Fix crew tier for {car}!")
        quit()

    driverSkill = random.randint(skill_min, skill_max)
    driverAggression = 500
    driverOptimism = 250
    driverSmoothness = car_smoothness
    driverAge = get_driver_age(driver_name)
    pitCrewSkill = random.randint(pit_min, pit_max)
    strategyRiskiness = random.randint(strategy_min, strategy_max)

    set_driver = Driver(driver_name, car, [driverSkill, driverAggression,
                                           driverOptimism, driverSmoothness,
                                           driverAge, pitCrewSkill, strategyRiskiness])

    return set_driver

def change_paint_scheme(car_num, driver_name, roster):
    try:
        paint_files = os.listdir(Path(roster_path/roster/car_num))
    except FileNotFoundError:
        print(f"No folder found for {car_num}")
        return

    if len(paint_files) == 1:
        print(f"No alternate schemes")
        return
    else:
        driver_paints = [file for file in paint_files
                         if driver_name.lower().replace(" ", "_")
                         in file]
        if len(driver_paints) == 0:
            new_paint_file = Path(roster_path/roster/car_num/random.choice(paint_files))
            print(f"Selected {new_paint_file}")
        else:
            new_paint_file = Path(roster_path/car_num/driver_paints[0])
            print(f"Selected {new_paint_file}")

    try:
        print("Attempting to copy file")
        shutil.copyfile(new_paint_file, Path(roster_path/roster/f"car_{car_num}.tga"))
    except:
        print("Uncategorized error, skipping copy operation")
        return

def open_files():
    with open(Path("src/assets/driver_tiers.json"), "r") as tier_file:
        driver_tiers = json.loads(tier_file.read())
    with open(Path("src/assets/cars.json"), "r") as car_file:
        car_list = json.loads(car_file.read())
    with open(Path("src/assets/schedule.json"), "r") as schedule_file:
        schedule_list = json.loads(schedule_file.read())
    return driver_tiers, car_list, schedule_list

def main(track, roster):
    driver_tiers, car_list, schedule_list = open_files()
    with open(Path(ai_roster_path/roster/"roster.json"), "r") as roster_file:
        driver_list = json.loads(roster_file.read())
    for roster_driver in driver_list["drivers"]:
        if car_list[roster_driver["carNumber"]]["type"] == "full_time_one_driver":
            print(f"Randomizing attributes for {roster_driver['driverName']} - #{roster_driver['carNumber']}")
            new_ratings = set_attributes(roster_driver['driverName'], roster_driver["carNumber"], driver_tiers, car_list)
        elif car_list[roster_driver["carNumber"]]["type"] == "full_time_multiple_drivers":
            scheduled_driver = schedule_list[track]["full_time"][roster_driver["carNumber"]]
            print(f"Randomizing attributes for {scheduled_driver} - #{roster_driver['carNumber']}")
            new_ratings = set_attributes(scheduled_driver, roster_driver["carNumber"], driver_tiers, car_list)
        elif car_list[roster_driver["carNumber"]]["type"] == "part_time":
            scheduled_driver = schedule_list[track]["part_time"][roster_driver["carNumber"]]
            if scheduled_driver:
                print(f"Randomizing attributes for {scheduled_driver} - #{roster_driver['carNumber']}")
                new_ratings = set_attributes(scheduled_driver, roster_driver["carNumber"], driver_tiers, car_list)
            else:
                print(f"No driver found for #{roster_driver['carNumber']} this week")
                roster_driver["driverName"] = "NO DRIVER"
                continue
        else:
            continue

        change_paint_scheme(roster_driver["carNumber"],
                            new_ratings.name,
                            roster)

        roster_driver["driverName"] = new_ratings.name
        roster_driver["driverSkill"] = new_ratings.driver_skill
        roster_driver["driverAggression"] = new_ratings.aggression
        roster_driver["driverOptimism"] = new_ratings.optimism
        roster_driver["driverSmoothness"] = new_ratings.smoothness
        roster_driver["pitCrewSkill"] = new_ratings.pit_skill
        roster_driver["strategyRiskiness"] = new_ratings.strategy
        roster_driver["driverAge"] = new_ratings.age

    with open(Path(ai_roster_path/roster/"roster.json"), "w", encoding="utf-8") as roster_file:
        json.dump(driver_list, roster_file, ensure_ascii=False, indent=4)

def perform_copy(roster_dir):
    try:
        shutil.copytree(Path(roster_path/roster_dir), Path(ai_roster_path/roster_dir), dirs_exist_ok=True)
        print("Roster directory successfully copied")
    except Exception as e:
        print(e)

if __name__ == "__main__":
    roster = "2025_Xfinity_Series_NSK_AI"
    perform_copy(roster)
    #race = input("Enter race designation: ")
    race = "daytona_1"
    main(race, roster)