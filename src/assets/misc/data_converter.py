import json
import re
from pathlib import Path


def sort_dict_keys_with_numbers(input_dict):
    """Sorts dictionary keys with numbers alphanumerically."""
    return dict(sorted(input_dict.items(), key=lambda item: [convert(c) for c in re.split('([0-9]+)', item[0])]))

def convert(text):
    """Helper function to convert strings to integers where applicable."""
    return int(text) if text.isdigit() else text.lower()

def convert_car_driver_mapping(series: str = "XFINITY"):
    with open(Path.cwd() / "src" / "data" / f"2025_{series}_DRIVER_CAR_MAPPING.json", "r") as map_file:
        orig_file = json.loads(map_file.read())
    
    car_details = {}

    for entry in orig_file:
        car_details[entry["CAR"]] = {}
        if entry["FULLTIME_DRIVER"] is not None:
            car_details[entry["CAR"]].update(fulltime_driver=entry["FULLTIME_DRIVER"])
        else:
            car_details[entry["CAR"]]["assigned_drivers"] = {}
            for key, values in entry.items():
                if "WEEK" in key and values is not None:
                    car_details[entry["CAR"]]["assigned_drivers"][key] = values
            car_details[entry["CAR"]]["assigned_drivers"] = sort_dict_keys_with_numbers(car_details[entry["CAR"]]["assigned_drivers"])
        car_details[entry["CAR"]].update(team=entry["TEAM"],
                                         car_status=entry["CAR_STATUS"],
                                         car_tier=entry["CAR_TIER"],
                                         pitcrew_tier=entry["PITCREW_TIER"],
                                         strategy_tier=entry["STRATEGY_TIER"])
    
    return car_details

def convert_drivers(series: str = "XFINITY"):
    with open(Path.cwd() / "src" / "data" / "ALL_DRIVERS.json", "r") as map_file:
        orig_file = json.loads(map_file.read())

    driver_data = {}

    for driver in orig_file:
        if driver[f"{series}_TIER"] is not None:
            driver_data[driver["NAME"]] = {
                "BIRTHDAY": driver["BIRTHDAY"],
                "DECLARED_POINTS": driver["DECLARED_POINTS"],
                f"{series}_TIER": driver[f"{series}_TIER"],
                f"PAST_{series}_CHAMPION": False if driver[f"PAST_{series}_CHAMPION"] is None else True
            }
    
    return driver_data
