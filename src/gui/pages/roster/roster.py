"""
Details to come...
"""

## Standard library imports
import PySimpleGUI as sg
import json

## Third party imports

## Local imports
from randomizer import randomizer

roster_path = "C:\\Users\\Nick\\Documents\\iracing_ai_helper\\rosters\\2025_Xfinity_Series_NSK_AI\\roster.json"


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


class Roster:
    @staticmethod
    def _build_headers() -> list:
        return [
            "Car",
            "Name",
            "Age",
            "Skill",
            "Aggr.",
            "Opt.",
            "Smth.",
            "Pitcrew",
            "Strat.",
        ]

    @staticmethod
    def _build_driver_table(driver_objs: list) -> list:
        driver_data = []

        for obj in driver_objs:
            if "NODRIVER" not in obj.name:
                driver_data.append(
                    [
                        obj.car,
                        obj.name,
                        obj.age,
                        obj.skill,
                        obj.aggression,
                        obj.optimism,
                        obj.smoothness,
                        obj.pitcrew,
                        obj.strategy,
                    ]
                )

        return driver_data

    @staticmethod
    def _format_drivers(drivers: list) -> list:
        driver_objs = []
        for driver in drivers:
            driver_objs.append(Driver(driver))

        return driver_objs

    @classmethod
    def build_driver_display_info(cls, roster_path: str) -> list:
        with open(roster_path, "r") as file:
            drivers = json.loads(file.read()).get("drivers")
        driver_objs = cls._format_drivers(drivers)
        driver_data = cls._build_driver_table(driver_objs)

        return driver_data

    @classmethod
    def build_layout(cls, driver_data: list) -> list:
        headers = cls._build_headers()
        layout = [
            [
                sg.Table(
                    values=driver_data,
                    headings=headers,
                    justification="center",
                    key="-TABLE-",
                    num_rows=35,
                )
            ],
            [
                sg.Text(text="Track: "),
                sg.Input(key="-TRACK-", enable_events=True, size=(15, None)),
            ],
            [sg.Button("Randomize"), sg.Button("Copy")],
        ]

        return layout

    @classmethod
    def main(cls, roster_path: str) -> None:
        driver_data = cls.build_driver_display_info(roster_path)
        layout = cls.build_layout(driver_data)

        window = sg.Window(
            "NSK AI Roster Randomizer - Alpha v0.1", layout, finalize=True
        )
        while True:
            event, values = window.read(timeout=1000)
            if event in (sg.WIN_CLOSED, None, "Exit"):
                break
            elif event == "Randomize":
                randomizer.main(values["-TRACK-"], roster_path)
                driver_data = cls.build_driver_display_info(roster_path)
                window["-TABLE-"].update(values=driver_data)
            elif event == "Copy":
                randomizer.perform_copy(roster_path)
            else:
                print(event, values)


if __name__ == "__main__":
    Roster.main(roster_path)
