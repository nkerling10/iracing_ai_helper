import json
import random
import os

road_course_tracks = [
    "cota",
    "sonoma",
    "laguna seca",
    "chicago",
    "watkins glen",
    "charlotte roval",
    "sebring"
]

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

def set_attributes(driver_name, car, driver_tiers, road_course):
    if driver_name in driver_tiers["tier_1"]:
        skill_min = 85
        skill_max = 100
        aggression_min = 85
        aggression_max = 100
        smoothness_min = 80
        smoothness_max = 105
        age_min = 40
        age_max = 60
        pit_min = 90
        pit_max = 100
        strategy_min = 1
        strategy_max = 10
    elif driver_name in driver_tiers["tier_2"]:
        skill_min = 80
        skill_max = 95
        aggression_min = 75
        aggression_max = 95
        smoothness_min = 70
        smoothness_max = 95
        age_min = 50
        age_max = 70
        pit_min = 85
        pit_max = 95
        strategy_min = 10
        strategy_max = 20
    elif driver_name in driver_tiers["tier_3"]:
        skill_min = 75
        skill_max = 90
        aggression_min = 65
        aggression_max = 85
        smoothness_min = 60
        smoothness_max = 85
        age_min = 60
        age_max = 80
        pit_min = 75
        pit_max = 90
        strategy_min = 20
        strategy_max = 30
    elif driver_name in driver_tiers["tier_4"]:
        skill_min = 70
        skill_max = 85
        aggression_min = 55
        aggression_max = 75
        smoothness_min = 45
        smoothness_max = 70
        age_min = 70
        age_max = 80
        pit_min = 65
        pit_max = 85
        strategy_min = 30
        strategy_max = 40
    elif driver_name in driver_tiers["tier_5"]:
        skill_min = 65
        skill_max = 80
        aggression_min = 50
        aggression_max = 70
        smoothness_min = 40
        smoothness_max = 65
        age_min = 80
        age_max = 100
        pit_min = 50
        pit_max = 75
        strategy_min = 50
        strategy_max = 80
    elif driver_name in driver_tiers["tier_6"]:
        skill_min = 60
        skill_max = 75
        aggression_min = 45
        aggression_max = 65
        smoothness_min = 35
        smoothness_max = 60
        age_min = 80
        age_max = 110
        pit_min = 30
        pit_max = 60
        strategy_min = 70
        strategy_max = 100
    else:
        print(f"{driver_name} not found, fix it!")
        quit()

    driverSkill = random.randint(skill_min, skill_max)
    driverAggression = random.randint(aggression_min, aggression_max)
    driverOptimism = 150
    driverSmoothness = 150 if road_course is True else random.randint(smoothness_min, smoothness_max)
    driverAge = random.randint(age_min, age_max)
    pitCrewSkill = random.randint(pit_min, pit_max)
    strategyRiskiness = random.randint(strategy_min, strategy_max)

    set_driver = Driver(driver_name, car, [driverSkill, driverAggression,
                                           driverOptimism, driverSmoothness,
                                           driverAge, pitCrewSkill, strategyRiskiness])

    return set_driver
    
def open_files():
    with open(f"{os.path.dirname(os.path.abspath(__file__))}/driver_tiers.json", "r") as tier_file:
        driver_tiers = json.loads(tier_file.read())
    with open(f"{os.path.dirname(os.path.abspath(__file__))}/cars.json", "r") as car_file:
        car_list = json.loads(car_file.read())
    with open(f"{os.path.dirname(os.path.abspath(__file__))}/schedule.json", "r") as schedule_file:
        schedule_list = json.loads(schedule_file.read())
    return driver_tiers, car_list, schedule_list

def main(track):
    road_course = False
    if track in road_course_tracks:
        road_course = True
    driver_tiers, car_list, schedule_list = open_files()
    with open(f"{os.path.dirname(os.path.abspath(__file__))}/rosters/2025_Xfinity_Series_NSK_AI/roster.json", "r") as roster_file:
        driver_list = json.loads(roster_file.read())
    for roster_driver in driver_list["drivers"]:
        if roster_driver["carNumber"] in car_list["full_time_one_driver"]:
            print(f"Randomizing attributes for {roster_driver['driverName']} - #{roster_driver['carNumber']}")
            new_ratings = set_attributes(roster_driver['driverName'], roster_driver["carNumber"], driver_tiers, road_course)
        elif roster_driver["carNumber"] in car_list["full_time_multiple_drivers"]:
            scheduled_driver = schedule_list[track]["full_time"][roster_driver["carNumber"]]
            print(f"Randomizing attributes for {scheduled_driver} - #{roster_driver['carNumber']}")
            new_ratings = set_attributes(scheduled_driver, roster_driver["carNumber"], driver_tiers, road_course)
        elif roster_driver["carNumber"] in car_list["part_time"]:
            scheduled_driver = schedule_list[track]["part_time"][roster_driver["carNumber"]]
            if scheduled_driver:
                print(f"Randomizing attributes for {scheduled_driver} - #{roster_driver['carNumber']}")
                new_ratings = set_attributes(scheduled_driver, roster_driver["carNumber"], driver_tiers, road_course)
            else:
                print(f"No driver found for #{roster_driver['carNumber']} this week")
                roster_driver["driverName"] = "NO DRIVER"
                continue
        else:
            continue

        roster_driver["driverName"] = new_ratings.name
        roster_driver["driverSkill"] = new_ratings.driver_skill
        roster_driver["driverAggression"] = new_ratings.aggression
        roster_driver["driverOptimism"] = new_ratings.optimism
        roster_driver["driverSmoothness"] = new_ratings.smoothness
        roster_driver["pitCrewSkill"] = new_ratings.pit_skill
        roster_driver["strategyRiskiness"] = new_ratings.strategy
        roster_driver["driverAge"] = new_ratings.age

        ##set drivers to different car make if necessary
        if roster_driver["driverName"] in ["Chad Finchum", "David Starr"] and roster_driver["carNumber"] == "14":
            roster_driver["carPath"] = "stockcars2\\mustang2019"
            roster_driver["carId"] = 115
        elif roster_driver["driverName"] in ["JJ Yeley", "CJ McLaughlin"] and roster_driver["carNumber"] == "14":
            roster_driver["carPath"] = "stockcars2\\camaro2019"
            roster_driver["carId"] = 114


    with open(f"{os.path.dirname(os.path.abspath(__file__))}/rosters/2025_Xfinity_Series_NSK_AI/roster.json", "w", encoding="utf-8") as roster_file:
        json.dump(driver_list, roster_file, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main("daytona_1")