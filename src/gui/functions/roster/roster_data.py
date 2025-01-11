"""
Details to come...
"""

## Standard library imports
import json
import logging
from pathlib import Path

## Third party imports

## Local imports

logger = logging.getLogger(__name__)


class Driver:
    def __init__(self, driver: dict) -> None:
        self.car = driver["carNumber"]
        self.name = driver["driverName"]
        self.age = driver["driverAge"]
        self.skill = driver["driverSkill"]
        self.aggression = driver["driverAggression"]
        self.optimism = driver["driverOptimism"]
        self.smoothness = driver["driverSmoothness"]
        self.pitcrew = driver["pitCrewSkill"]
        self.strategy = driver["strategyRiskiness"]


def _build_driver_table(driver_objs: list) -> list:
    active_driver_data = []
    inactive_driver_data = []

    for obj in driver_objs:
        if "NODRIVER" not in obj.name:
            list = active_driver_data
        else:
            list = inactive_driver_data
        list.append(
            [obj.car, obj.name, obj.age, obj.skill,
             obj.aggression, obj.optimism, obj.smoothness,
             obj.pitcrew, obj.strategy]
        )

    return active_driver_data, inactive_driver_data


def build_driver_display_info(roster_path: str) -> list:
    with open(Path(roster_path) / "roster.json", "r") as roster_file:
        driver_objs = [
            Driver(driver) for driver in json.loads(roster_file.read()).get("drivers")
        ]
    active_driver_data, inactive_driver_data = _build_driver_table(driver_objs)

    return active_driver_data, inactive_driver_data
