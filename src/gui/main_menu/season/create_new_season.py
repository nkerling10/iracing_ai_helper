import json
import logging
import os
import PySimpleGUI as sg
import sqlite3
from pathlib import Path
from shutil import copyfile, copytree

logger = logging.getLogger(__name__)

ai_seasons_file_path = Path.cwd() / "ai_seasons"
base_files_roster_path = Path.cwd() / "base_files" / "rosters"
season_path_dest = f"C:/Users/Nick/Documents/iRacing/aiseasons/"

__version__ = "1.0"

CUP_SERIES = set([139, 140, 141])
XFINITY_SERIES = set([114, 115, 116])
TRUCK_SERIES = set([111, 123, 155])
ARCA_SERIES = set([24])
INDYCAR_SERIES = set([99])
SRX_SERIES = set([179])
LATEMODEL_SERIES = set([164])

def _load_iracing_season(season_file: str):
    with open(season_file, "r") as file:
        iracing_season = json.loads(file.read())
    cars_selected = set([car.get("car_id") for car in iracing_season.get("carSettings")])
    if cars_selected == CUP_SERIES:
        return "CUP"
    elif cars_selected == XFINITY_SERIES:
        return "XFINITY"
    elif cars_selected == TRUCK_SERIES:
        return "TRUCK"
    elif cars_selected == ARCA_SERIES:
        return "ARCA"
    elif cars_selected == INDYCAR_SERIES:
        return "INDYCAR"
    elif cars_selected == SRX_SERIES:
        return "SRX"
    elif cars_selected == LATEMODEL_SERIES:
        return "LATEMODEL"
    else:
        logger.debug(f"Car IDs for loaded season: {cars_selected}")
        return "CUSTOM"


def _season_type(values: dict) -> str:
    """
    Returns season type when called by _create_local_season_settings_file
    """
    if values["__SEASONTYPERADIOCUP__"]:
        return "CUP"
    elif values["__SEASONTYPERADIOXFINITY__"]:
        return "XFINITY"
    elif values["__SEASONTYPERADIOTRUCKS__"]:
        return "TRUCKS"
    elif values["__SEASONTYPERADIOARCA__"]:
        return "ARCA"
    elif values["__SEASONTYPERADIOINDYCAR__"]:
        return "INDYCAR"
    elif values["__SEASONTYPERADIOSRX__"]:
        return "SRX"


def _block_focus(window) -> None:
    """
    Function to block focus on main_window when the create season dialog appears
    """
    for key in window.key_dict:  # Remove dash box of all Buttons
        element = window[key]
        if isinstance(element, sg.Button):
            element.block_focus()


def _update_season_settings(season_settings: dict) -> None:
    """
    Modifies settings within the season json file to what the user provided  during creation.
    """
    try:
        logger.info("Attempting to open season settings file")
        with open(season_settings.get("iracing_season_file"), "r") as file:
            modified_season_file = json.loads(file.read())
    except Exception as e:
        logger.error(f"Failed to read season settings file: {e}")
        return False

    car_index = 0
    while car_index < len(modified_season_file["carSettings"]):
        modified_season_file["carSettings"][car_index]["max_pct_fuel_fill"] = (
            season_settings.get("user_settings").get("fuel_capacity")
        )
        modified_season_file["carSettings"][car_index]["max_dry_tire_sets"] = (
            -1
            if season_settings.get("user_settings").get("tire_sets") == "UNLIMITED"
            else int(season_settings.get("user_settings").get("tire_sets"))
        )
        car_index += 1

    modified_season_file["rosterName"] = season_settings.get("season_name")
    modified_season_file["name"] = season_settings.get("season_name")
    modified_season_file["max_drivers"] = 100

    race_index = 0
    while race_index < len(modified_season_file["events"]):
        try:
            full_distance = modified_season_file["events"][race_index]["race_laps"]
        except KeyError:
            modified_season_file["events"][race_index]["race_laps"] = modified_season_file["race_laps"]
            full_distance = modified_season_file["events"][race_index]["race_laps"]
        modified_season_file["events"][race_index]["race_laps"] = round(
            full_distance * (season_settings.get("user_settings").get("race_distance_percent") / 100)
        )
        race_index += 1

    try:
        logger.info("Attempting to write updates to season_settings file")
        with open(season_settings.get("iracing_season_file"), "w") as file:
            json.dump(modified_season_file, file, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        logger.error(f"Failed to write file: {e}")
        return False


def _copy_roster_folder(season_series: str, season_name: str) -> None:
    """
    Performs a copy of selected series' base roster file into the iRacing airosters
    folder. It will exist in a folder titled what the user provided as roster.json.
    """
    base_roster_folder = Path.cwd() / "base_files" / f"2025_{season_series}"
    roster_path_dest = f"C:/Users/Nick/Documents/iRacing/airosters/{season_name}"

    if not os.path.exists(roster_path_dest):
        logger.info(f"Folder {roster_path_dest} does not exist, creating")
        os.makedirs(roster_path_dest)

    try:
        logger.info(f"Copying roster folder {base_roster_folder / f"2025_{season_series}_ROSTER"}")
        copytree(
            base_roster_folder / f"2025_{season_series}_ROSTER",
            f"C:/Users/Nick/Documents/iRacing/airosters/{season_name}",
            dirs_exist_ok=True,
        )
        logger.info("Folder copied successfully")
        return f"C:/Users/Nick/Documents/iRacing/airosters/{season_name}"
    except Exception as e:
        logger.error(f"Error copying folder: {e}")
        return None


def _copy_season_file(season_series: str, season_name: str):
    base_season_folder = Path.cwd() / "base_files" / f"2025_{season_series}"
    try:
        logger.info(f"Copying season file {base_season_folder}/2025_{season_series}.json")
        copyfile(
            Path(f"{base_season_folder}/2025_{season_series}.json"),
            Path(f"{season_path_dest}/{season_name}.json")
        )
        logger.info("File copied successfully")
        return f"{season_path_dest}/{season_name}.json"
    except Exception as e:
        logger.error(f"Error copying file: {e}")
        return None


def _copy_custom_season_file(custom_season_file_path: str, season_name: str):
    try:
        logger.info(f"Copying season file {custom_season_file_path}")
        copyfile(
            Path(f"{custom_season_file_path}"),
            Path(f"{season_path_dest}/{season_name}.json")
        )
        logger.info("File copied successfully")
        return f"{season_path_dest}/{season_name}.json"
    except Exception as e:
        logger.error(f"Error copying file: {e}")
        return None


def _create_local_season_settings_file(values: dict, tire_sets: int, custom_season_file_path: str) -> dict:
    """
    Creates the local "season settings" file that is stored as json. This file contains references to
    user selected settings as well as the iRacing AI Season file & Roster file that will be linked when utilizing
    the app. File is stored in a folder called "ai_seasons" in the same directory that the app exists in.
    """
    if not os.path.exists(ai_seasons_file_path):
        logger.info(f"Folder {ai_seasons_file_path} does not exist, creating")
        os.makedirs(ai_seasons_file_path)
    if os.path.exists(ai_seasons_file_path / f"{values['__SEASONNAME__']}.json"):
        sg.Popup(
            "A season_settings file with that name already exists, use a different name",
            no_titlebar=True,
        )
        return {}

    if custom_season_file_path:
        season_file = _copy_custom_season_file(custom_season_file_path, season_name=values["__SEASONNAME__"])
    else:
        season_file = _copy_season_file(season_series=_season_type(values), season_name=values["__SEASONNAME__"])

    season_settings = {
        "season_name": values["__SEASONNAME__"],
        "player_team_name": values["__PLAYERTEAMNAME__"],
        "season_series": _season_type(values),
        "iracing_roster_file": _copy_roster_folder(season_series=_season_type(values), season_name=values["__SEASONNAME__"]),
        "iracing_season_file": season_file,
        "custom_season": True if custom_season_file_path else False,
        "user_settings": {
            "stages_enabled": True if values["__STAGECAUTIONSCHECKBOX__"] is True else False,
            "field_size": values["__FIELDSIZE__"],
            "race_distance_percent": int(values["__RACEDISTANCEPERCENT__"]),
            "fuel_capacity": int(values["__FUELCAPACITY__"]),
            "tire_sets": "UNLIMITED" if values["__TIRESETSUNLIMITED__"] is True else tire_sets,
            "pre_race_penalties": {
                "enabled": True if values["__PRERACEPENALTIESCHECKBOX__"] is True else False,
                "chance": (
                        int(values["__PRERACEPENALTIESCHANCEVALUE__"])
                        if values["__PRERACEPENALTIESCHECKBOX__"] is True
                        else 0
                    ),
                "inspection_fail_chance_modifier": (
                    int(values["__INSPECTIONFAILCHANCEMODIFIERVALUE__"])
                    if values["__PRERACEPENALTIESCHECKBOX__"] is True
                    else 0
                ),
            },
            "pit_penalties": {
                "enabled": True if values["__PITPENALTIESCHECKBOX__"] is True else False,
                "chance": int(values["__PITPENALTIESCHANCEVALUE__"])
            },
            "post_race_penalties": {
                "enabled": True if values["__POSTRACEPENALTIESCHECKBOX__"] is True else False,
                "chance": (
                    int(values["__POSTRACEPENALTIESCHANCEVALUE__"])
                    if values["__PRERACEPENALTIESCHECKBOX__"] is True
                    else 0
                )
            },
            "debris_cautions": {
                "enabled": True if values["__DEBRISCAUTIONCHECKBOX__"] is True else False,
                "chance": (
                    int(values["__DEBRISCAUTIONCHANCEVALUE__"])
                    if values["__DEBRISCAUTIONCHECKBOX__"] is True
                    else 0
                )
            }
        }
    }

    try:
        with open(ai_seasons_file_path / f"{values['__SEASONNAME__']}.json", "w") as new_season_file:
            new_season_file.write(json.dumps(season_settings, indent=4))
            return season_settings
    except Exception as e:
        logger.error("Unable to write file")
        return {}


def WIP_create_new_season_layout():
    return [
        [
            sg.Button("NASCAR Cup Series"),
            sg.Button("NASCAR Xfinity Series"),
            sg.Button("NASCAR Truck Series"),
            sg.Button("ARCA Menards Series"),
        ],
        [
            sg.Button("SRX Series"),
            sg.Button("Indycar Series"),
            sg.Button("Late Models"),
        ]
    ]


def WIP_create_new_season():
    window = sg.Window(
        "Create New Season", _create_new_season_layout(), use_default_focus=False, finalize=True, modal=True
    )
    _block_focus(window)
    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, "Exit", "Cancel"):
            window.close()
            return


def create_new_season(custom_season_file_path: str = "") -> dict:
    """
    Handles the popup window for creating a new season
    """
    if custom_season_file_path:
        season_series = _load_iracing_season(custom_season_file_path)
    
    layout = [
        [
            sg.Frame(
                layout=[[sg.InputText(key="__SEASONNAME__")]],
                title="Enter a name for the season",
                expand_x=True,
            )
        ],
        [
            sg.Frame(
                layout=[
                    [
                        sg.Radio(
                            "Cup",
                            group_id=1,
                            key="__SEASONTYPERADIOCUP__",
                            enable_events=True,
                            disabled=True,
                        ),
                        sg.Radio(
                            "Xfinity",
                            group_id=1,
                            key="__SEASONTYPERADIOXFINITY__",
                            enable_events=True,
                            default=True
                        ),
                        sg.Radio(
                            "Truck",
                            group_id=1,
                            key="__SEASONTYPERADIOTRUCKS__",
                            enable_events=True,
                            disabled=True,
                        ),
                        sg.Radio(
                            "ARCA",
                            group_id=1,
                            key="__SEASONTYPERADIOARCA__",
                            enable_events=True,
                            disabled=True,
                        ),
                        sg.Radio(
                            "Indycar",
                            group_id=1,
                            key="__SEASONTYPERADIOINDYCAR__",
                            enable_events=True,
                            disabled=True,
                        ),
                        sg.Radio(
                            "Indycar",
                            group_id=1,
                            key="__SEASONTYPERADIOSRX__",
                            enable_events=True,
                            disabled=True,
                        )
                    ]
                ],
                title="Series Type",
                expand_x=True,
            ),
            sg.Frame(
                layout=[
                    [
                        sg.Spin(
                            values=[i for i in range(1, 50)],
                            initial_value=38,
                            expand_x=True,
                            key="__FIELDSIZE__",
                        )
                    ]
                ],
                title="Field size",
                expand_y=True,
            ),
            sg.Frame(
                layout=[[sg.InputText(key="__PLAYERTEAMNAME__")]],
                title="Team name",
                expand_y=True,
            ),
        ],
        [
            sg.Frame(
                layout=[
                    [
                        sg.Slider(
                            range=(5, 100),
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
                    [
                        sg.Radio(
                            "Current",
                            group_id=2,
                            key="__CURRENTPOINTSFORMAT__",
                            default=True,
                        )
                    ],
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
                        sg.Checkbox(
                            "Custom",
                            key="__TIRESETSCUSTOM__",
                            expand_x=True,
                            enable_events=True,
                        ),
                        sg.Checkbox(
                            "Unlimited",
                            key="__TIRESETSUNLIMITED__",
                            expand_x=True,
                            default=True,
                            enable_events=True,
                        ),
                    ],
                    [
                        sg.Text("Sets:"),
                        sg.Text("0", key="__TIRESETS__", enable_events=True),
                    ],
                    [sg.Button("-set"), sg.Button("+set")],
                ],
                title="Enter desired number of tire sets",
                expand_x=True,
                expand_y=True,
            ),
        ],
        [
            sg.Frame(
                layout=[
                    [
                        sg.Column(
                            layout=[
                                [
                                    sg.Frame(
                                        layout=[
                                            [
                                                sg.Column(
                                                    layout=[
                                                        [
                                                            sg.Checkbox(
                                                                "Pre-race penalties",
                                                                key="__PRERACEPENALTIESCHECKBOX__",
                                                                expand_x=True,
                                                                expand_y=True,
                                                                default=True,
                                                                tooltip="Enables/Disables the generation and assignment of pre-race penalties",
                                                            ),
                                                        ],
                                                        [
                                                            sg.Text(
                                                                "% Likelihood",
                                                                justification="c",
                                                                tooltip="Percentage chance that each car will have a pre-race penalty",
                                                            ),
                                                            sg.Text(
                                                                "Inspection\nmodifier",
                                                                justification="c",
                                                                tooltip="Multiplicative percentage chance that each additional inspection attempt will fail\n\nIf value of pre-race penalities and Inspection modifier are 2%:\n2% fail chance of first inspection -> 4% fail chance of second inspection -> 8% fail chance of third inspection",
                                                            ),
                                                        ],
                                                        [
                                                            sg.Spin(
                                                                values=[
                                                                    i
                                                                    for i in range(
                                                                        1, 100
                                                                    )
                                                                ],
                                                                key="__PRERACEPENALTIESCHANCEVALUE__",
                                                                initial_value=2,
                                                                expand_x=True,
                                                                tooltip="Percentage chance that each car will have a pre-race penalty",
                                                            ),
                                                            sg.Spin(
                                                                values=[
                                                                    i
                                                                    for i in range(
                                                                        1, 100
                                                                    )
                                                                ],
                                                                key="__INSPECTIONFAILCHANCEMODIFIERVALUE__",
                                                                initial_value=2,
                                                                expand_x=True,
                                                                tooltip="Multiplicative percentage chance that each additional inspection attempt will fail",
                                                            ),
                                                        ],
                                                    ]
                                                ),
                                                sg.Column(
                                                    layout=[
                                                        [
                                                            sg.Checkbox(
                                                                "Pit penalties",
                                                                key="__PITPENALTIESCHECKBOX__",
                                                                expand_x=True,
                                                                expand_y=True,
                                                                default=True,
                                                                tooltip="Enables/Disables the generation and assignment of pit-penalties for all drivers",
                                                            ),
                                                        ],
                                                        [
                                                            sg.Text(
                                                                "% Likelihood",
                                                                justification="c",
                                                            )
                                                        ],
                                                        [
                                                            sg.Spin(
                                                                values=[
                                                                    i
                                                                    for i in range(
                                                                        1, 100
                                                                    )
                                                                ],
                                                                key="__PITPENALTIESCHANCEVALUE__",
                                                                initial_value=8,
                                                                expand_x=True,
                                                                tooltip="Percentage chance for a car to have a pit-penalty assigned",
                                                            )
                                                        ],
                                                    ]
                                                ),
                                                sg.Column(
                                                    layout=[
                                                        [
                                                            sg.Checkbox(
                                                                "Post-race penalties",
                                                                key="__POSTRACEPENALTIESCHECKBOX__",
                                                                expand_x=True,
                                                                expand_y=True,
                                                                default=True,
                                                                tooltip="Enables/Disables the generation and assignment of post-race penalties for all drivers",
                                                            )
                                                        ],
                                                        [
                                                            sg.Text(
                                                                "% Likelihood",
                                                                justification="c",
                                                            )
                                                        ],
                                                        [
                                                            sg.Spin(
                                                                values=[
                                                                    i
                                                                    for i in range(
                                                                        1, 100
                                                                    )
                                                                ],
                                                                key="__POSTRACEPENALTIESCHANCEVALUE__",
                                                                initial_value=2,
                                                                expand_x=True,
                                                                tooltip="Percentage chance for a car to have a post-race penalty assigned",
                                                            )
                                                        ],
                                                    ]
                                                ),
                                            ]
                                        ],
                                        title="Penalties",
                                    ),
                                    sg.Frame(
                                        layout=[
                                            [
                                                sg.Column(
                                                    layout=[
                                                        [
                                                            sg.Checkbox(
                                                                "Debris Cautions",
                                                                key="__DEBRISCAUTIONCHECKBOX__",
                                                                expand_x=True,
                                                                expand_y=True,
                                                                default=True,
                                                                tooltip="Enables/Disables the generation of debris caution events",
                                                            )
                                                        ],
                                                        [
                                                            sg.Text(
                                                                "% Likelihood",
                                                                justification="c",
                                                            )
                                                        ],
                                                        [
                                                            sg.Spin(
                                                                values=[
                                                                    i
                                                                    for i in range(1, 5)
                                                                ],
                                                                key="__DEBRISCAUTIONCHANCEVALUE__",
                                                                initial_value=1,
                                                                expand_x=True,
                                                                tooltip="Percentage chance a debris caution will be thrown during each tick",
                                                            )
                                                        ],
                                                    ]
                                                ),
                                                sg.Column(
                                                    layout=[
                                                        [
                                                            sg.Checkbox(
                                                                "Stage Cautions",
                                                                key="__STAGECAUTIONSCHECKBOX__",
                                                                expand_x=True,
                                                                expand_y=False,
                                                                default=True,
                                                                tooltip="Enables/Disables stage caution flags",
                                                            )
                                                        ]
                                                    ]
                                                ),
                                            ]
                                        ],
                                        title="Cautions",
                                        expand_x=True,
                                        expand_y=True,
                                    ),
                                ]
                            ]
                        )
                    ]
                ],
                title="Race Settings",
                expand_x=True,
                expand_y=True,
            )
        ],
        [sg.Button("Create"), sg.Button("Cancel")],
    ]

    window = sg.Window(
        "Create New Season", layout, use_default_focus=False, finalize=True, modal=True
    )
    _block_focus(window)
    if season_series:
        window[f"__SEASONTYPERADIO{season_series}__"].update(value=True)
        for key, _element in window.AllKeysDict.items():
            if "SEASONTYPERADIO" in key and season_series not in key:
                window[key].update(disabled=True)
    tire_sets = 0
    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, "Exit", "Cancel"):
            window.close()
            return
        if event == "Create":
            if not all(
                [values["__SEASONNAME__"], values["__PLAYERTEAMNAME__"]]
            ) or not any(
                [
                    values["__SEASONTYPERADIOCUP__"],
                    values["__SEASONTYPERADIOXFINITY__"],
                    values["__SEASONTYPERADIOTRUCKS__"],
                    values["__SEASONTYPERADIOARCA__"],
                    values["__SEASONTYPERADIOINDYCAR__"],
                    values["__SEASONTYPERADIOSRX__"]
                ]
            ):
                sg.popup("ERROR: Missing a required entry!", no_titlebar=True)
            else:
                season_settings = _create_local_season_settings_file(values, window["__TIRESETS__"].get(), custom_season_file_path)
                if season_settings:
                    success = _update_season_settings(season_settings)
                    if success:
                        window.close()
                        return season_settings
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


if __name__ == "__main__":
    create_new_season()
