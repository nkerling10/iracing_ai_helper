"""
Details to come...
"""

## Standard library imports
import PySimpleGUI as sg
import json
from pathlib import Path
## Third party imports

## Local imports
from randomizer import randomizer


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


def _roster_file_headers() -> list:
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


def build_driver_table(driver_objs: list) -> list:
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


def build_driver_display_info(roster_path: str) -> list:
    with open(roster_path, "r") as roster_file:
        driver_objs = [Driver(driver) for driver in 
                       json.loads(roster_file.read()).get("drivers")]
    driver_data = build_driver_table(driver_objs)

    return driver_data


def build_roster_tab_layout(driver_data: list) -> list:
    return [
        [
            sg.Table(
                values=driver_data,
                headings=_roster_file_headers(),
                justification="center",
                key="-TABLE-",
                num_rows=35,
            )
        ],
        [
            sg.Text(text="Track: "),
            sg.Input(key="-TRACK-", enable_events=True, size=(15, None)),
            sg.Text(key="-TRACKSTATUS-"),
        ],
        [sg.Text(text="File loaded:"), sg.Text(key="-ROSTERFILELOADED-")],
        [sg.Button("Randomize"), sg.Button("Copy")]
    ]

def build_layout(driver_data: list) -> list:
    roster_tab_layout = build_roster_tab_layout(driver_data)

    season_tab_layout = [[]]
    standings_tab_layout = [[]]

    layout = [[sg.TabGroup([[sg.Tab("Roster", roster_tab_layout, key="-rostertab-"),
                                sg.Tab("Season", season_tab_layout, key="-seasontab"),
                                sg.Tab("Standings", standings_tab_layout, key="-standingstab-")]],
                                key="-tabgroup1-", tab_location="topleft"),]]

    return layout


def main_window() -> None:
    driver_data = build_driver_display_info(local_roster_path)
    layout = build_layout(driver_data)
    window = sg.Window(
        "NSK AI Roster Randomizer - Alpha v0.1", layout, finalize=True
    )
    window["-ROSTERFILELOADED-"].update(value=local_roster_path)
    while True:
        event, values = window.read(timeout=1000)
        if event in (sg.WIN_CLOSED, None, "Exit"):
            break
        elif event == "Randomize":
            if values["-TRACK-"] != "":
                randomizer.main(values["-TRACK-"], local_roster_path)
                window["-TRACKSTATUS-"].update("Success!")
                driver_data = build_driver_display_info(local_roster_path)
                window["-TABLE-"].update(values=driver_data)
                window.read(timeout=1500)
                window["-TRACKSTATUS-"].update("")
            else:
                window["-TRACKSTATUS-"].update("ERROR! Track missing")
        elif event == "Copy":
            randomizer.perform_copy(local_roster_path)


if __name__ == "__main__":
    sg.theme("DarkBrown4")
    SETTINGS_PATH = Path.cwd() / "src" / "gui" / "pages" / "roster"
    settings = sg.UserSettings(
        path = SETTINGS_PATH,
        filename="roster_config.ini",
        use_config_file=True,
        convert_bools_and_none=True
    )
    local_roster_path = settings["PATHS"]["LOCAL_ROSTER"]
    iracing_ai_roster_path = settings["PATHS"]["AI_ROSTER_FOLDER"]
    main_window()
