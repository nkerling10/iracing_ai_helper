import json
import logging
import os
import PySimpleGUI as sg
from pathlib import Path
from shutil import copyfile

logger = logging.getLogger(__name__)

ai_seasons_file_path = Path.cwd() / "ai_seasons"
base_files_roster_path = Path.cwd() / "base_files" / "rosters"


def _copy_roster_file(config: object, season: dict) -> None:
    roster_path_dest = config.iracing_folder / "airosters" / season.get("roster_name")

    if season.get("season_series") == "CUP":
        file = base_files_roster_path / "2025_Cup_Series" / "roster.json"
    elif season.get("season_series") == "XFINITY":
        file = base_files_roster_path / "2025_Xfinity_Series" / "roster.json"
    elif season.get("season_series") == "TRUCKS":
        file = base_files_roster_path / "2025_Truck_Series" / "roster.json"
    elif season.get("season_series") == "ARCA":
        file = base_files_roster_path / "2025_ARCA_Series" / "roster.json"

    if not os.path.exists(roster_path_dest):
        logger.info(f"Folder {roster_path_dest} does not exist, creating")
        os.makedirs(roster_path_dest)

    try:
        logger.info(f"Copying roster file {file}")
        copyfile(file, config.iracing_folder / "airosters" / season.get("roster_name") / "roster.json")
        logger.info("File copied successfully")
    except Exception as e:
        logger.error(f"Error copying file: {e}")


def _create_local_season_file(values: dict, custom_tireset: int = 0) -> dict:
    if not os.path.exists(ai_seasons_file_path):
        logger.info(f"Folder {ai_seasons_file_path} does not exist, creating")
        os.makedirs(ai_seasons_file_path)
    if os.path.exists(ai_seasons_file_path / f"{values['__SEASONNAME__']}.json"):
        sg.Popup("Warning! A season file with that name already exists", no_titlebar=True)
        return False
    season = {
        "season_name": values["__SEASONNAME__"],
        "season_series": _season_type(values),
        "roster_name": values["__ROSTERNAME__"],
        "fuel_capacity": int(values["__FUELCAPACITY__"]),
        "tire_sets": "UNLIMITED" if values["__TIRESETSUNLIMITED__"] is True else custom_tireset,
        "race_distance_percent": int(values["__RACEDISTANCEPERCENT__"]),
        "points_format": _points_format(values),
    }
    try:
        with open(ai_seasons_file_path / f"{values['__SEASONNAME__']}.json", "w") as new_season_file:
            new_season_file.write(json.dumps(season, indent=4))
    except Exception as e:
        logger.error("Unable to write file")
        return {}

    return season


def _points_format(values: dict) -> str:
    if values["__CURRENTPOINTSFORMAT__"]:
        return "CURRENT"
    elif values["__CHASEPOINTSFORMAT__"]:
        return "CHASE"
    elif values["__WINSTONCUPPOINTSFORMAT__"]:
        return "WINSTON"


def _season_type(values: dict) -> str:
    if values["__SEASONTYPECUP__"]:
        return "CUP"
    elif values["__SEASONTYPEXFINITY__"]:
        return "XFINITY"
    elif values["__SEASONTYPETRUCKS__"]:
        return "TRUCKS"
    elif values["__SEASONTYPEARCA__"]:
        return "ARCA"


def _block_focus(window) -> None:
    for key in window.key_dict:  # Remove dash box of all Buttons
        element = window[key]
        if isinstance(element, sg.Button):
            element.block_focus()


def _create_new_season(config) -> dict:
    layout = [
        [sg.Frame(layout=[[sg.InputText(key="__SEASONNAME__")]], title="Enter a name for the season", expand_x=True)],
        [
            sg.Frame(
                layout=[
                    [
                        sg.Radio("Cup", group_id=1, key="__SEASONTYPECUP__", enable_events=True),
                        sg.Radio("Xfinity", group_id=1, key="__SEASONTYPEXFINITY__", enable_events=True),
                        sg.Radio("Truck", group_id=1, key="__SEASONTYPETRUCKS__", enable_events=True),
                        sg.Radio("ARCA", group_id=1, key="__SEASONTYPEARCA__", enable_events=True),
                    ]
                ],
                title="Select series type",
                expand_x=True,
            )
        ],
        [sg.Frame(layout=[[sg.InputText(key="__ROSTERNAME__")]], title="Enter a name for the roster", expand_x=True)],
        [
            sg.Frame(
                layout=[
                    [
                        sg.Slider(
                            range=(10, 100),
                            default_value=100,
                            orientation="horizontal",
                            key="__RACEDISTANCEPERCENT__",
                            expand_x=True,
                        )
                    ]
                ],
                title="Select desired race distance",
                expand_x=True,
                expand_y=True,
            ),
            sg.Frame(
                layout=[
                    [sg.Radio("Current", group_id=2, key="__CURRENTPOINTSFORMAT__", default=True)],
                    [sg.Radio("The Chase", group_id=2, key="__CHASEPOINTSFORMAT__", disabled=True)],
                    [sg.Radio("Winston Cup", group_id=2, key="__WINSTONCUPPOINTSFORMAT__", disabled=True)],
                ],
                title="Points format",
                expand_x=True,
                expand_y=True,
            ),
        ],
        [
            sg.Frame(
                layout=[
                    [
                        sg.Slider(
                            range=(1, 100),
                            default_value=100,
                            orientation="horizontal",
                            key="__FUELCAPACITY__",
                            expand_x=True,
                        )
                    ]
                ],
                title="Select desired fuel capacity",
                expand_x=True,
                expand_y=True,
            ),
            sg.Frame(
                layout=[
                    [
                        sg.Checkbox("Custom", key="__TIRESETSCUSTOM__", expand_x=True, enable_events=True),
                        sg.Checkbox(
                            "Unlimited", key="__TIRESETSUNLIMITED__", expand_x=True, default=True, enable_events=True
                        ),
                    ],
                    [sg.Text("Sets:"), sg.Text("0", key="__TIRESETS__", enable_events=True)],
                    [sg.Button("-set"), sg.Button("+set")],
                ],
                title="Enter desired number of tire sets",
                expand_x=True,
                expand_y=True,
            ),
        ],
        [sg.Button("Create"), sg.Button("Cancel")],
    ]
    window = sg.Window("Create New Season", layout, use_default_focus=False, finalize=True, modal=True)
    _block_focus(window)
    tire_sets = 0
    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, "Exit", "Cancel"):
            window.close()
            return
        if event == "Create":
            if not any([values["__SEASONNAME__"], values["__ROSTERNAME__"]]) and not all(
                [
                    values["__SEASONTYPECUP__"],
                    values["__SEASONTYPEXFINITY__"],
                    values["__SEASONTYPETRUCKS__"],
                    values["__SEASONTYPEARCA__"],
                ]
            ):
                sg.popup("Missing a required entry!", no_titlebar=True)
            else:
                season = _create_local_season_file(values, window["__TIRESETS__"].get())
                _copy_roster_file(config, season)
                if season:
                    window.close()
                    return season
        if event == "__TIRESETSCUSTOM__":
            window["__TIRESETSUNLIMITED__"].update(value=False)
        if event == "__TIRESETSUNLIMITED__":
            window["__TIRESETSCUSTOM__"].update(value=False)
        if event == "+set":
            tire_sets += 1
            window["__TIRESETSCUSTOM__"].update(value=True)
            window["__TIRESETSUNLIMITED__"].update(value=False)
            window["__TIRESETS__"].update(tire_sets)
        if event == "-set":
            if tire_sets != 0:
                tire_sets -= 1
                window["__TIRESETSCUSTOM__"].update(value=True)
                window["__TIRESETSUNLIMITED__"].update(value=False)
                window["__TIRESETS__"].update(tire_sets)
        else:
            logger.debug(f"{event}: {values}")
