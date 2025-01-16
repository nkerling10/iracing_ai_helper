import json
import logging
import os
import PySimpleGUI as sg
from pathlib import Path
from shutil import copyfile, copytree

logger = logging.getLogger(__name__)

ai_seasons_file_path = Path.cwd() / "ai_seasons"
base_files_roster_path = Path.cwd() / "base_files" / "rosters"


def _update_season_settings(config: object, season_settings: dict) -> None:
    """
    Modifies settings within the season json file to what the user provided  during creation.
    """
    try:
        logger.info("Attempting to open season settings file")
        with open(
            config.iracing_folder / "aiseasons" / season_settings.get("season_file"),
            "r",
        ) as file:
            modified_season_file = json.loads(file.read())
    except Exception as e:
        logger.error(f"Failed to read season settings file: {e}")
        return

    car_index = 0
    while car_index < len(modified_season_file["carSettings"]):
        modified_season_file["carSettings"][car_index]["max_pct_fuel_fill"] = (
            season_settings.get("fuel_capacity")
        )
        modified_season_file["carSettings"][car_index]["max_dry_tire_sets"] = (
            -1
            if season_settings.get("tire_sets") == "UNLIMITED"
            else int(season_settings.get("tire_sets"))
        )
        car_index += 1

    modified_season_file["rosterName"] = season_settings.get("roster_name")

    race_index = 0
    while race_index < len(modified_season_file["events"]):
        full_disance = modified_season_file["events"][race_index]["race_laps"]
        modified_season_file["events"][race_index]["race_laps"] = round(
            full_disance * (season_settings.get("race_distance_percent") / 100)
        )
        race_index += 1

    try:
        logger.info("Attempting to write updates to season_settings file")
        with open(
            config.iracing_folder / "aiseasons" / season_settings.get("season_file"),
            "w",
        ) as file:
            json.dump(modified_season_file, file, ensure_ascii=False, indent=4)
    except Exception as e:
        logger.error(f"Failed to write file: {e}")


def _copy_season_base_file(config: object, season_settings: dict) -> bool:
    """
    Performs a copy of selected series' base season file into the iRacing aiseasons
    folder. It will be named what the user provided.
    """
    if season_settings.get("season_series") == "CUP":
        base_file = "2025_Cup_Series"
    elif season_settings.get("season_series") == "XFINITY":
        base_file = "2025_Xfinity_Series"
    elif season_settings.get("season_series") == "TRUCKS":
        base_file = "2025_Truck_Series"
    elif season_settings.get("season_series") == "ARCA":
        base_file = "2025_ARCA_Series"
    try:
        logger.info(f"Copying official file {base_file}.json")
        copyfile(
            Path(Path.cwd() / "base_files" / "seasons" / f"{base_file}.json"),
            Path(
                config.iracing_folder
                / "aiseasons"
                / f"{season_settings.get('season_name')}.json"
            ),
        )
        logger.info(
            "File copied successfully, updating file path in season_settings file"
        )
        try:
            with open(
                Path.cwd()
                / "ai_seasons"
                / f"{season_settings.get('season_name')}.json",
                "r",
            ) as file:
                season_file = json.loads(file.read())
                logger.debug("File read successful")
        except Exception as e:
            logger.error(
                f"Could not read file {Path.cwd()}"
                / "ai_seasons"
                / f"{season_settings.get('season_name')}.json"
            )
            return False
        season_file["season_file"] = str(
            config.iracing_folder
            / "aiseasons"
            / f"{season_settings.get('season_name')}.json"
        ).replace("\\", "/")
        season_settings["season_file"] = str(
            config.iracing_folder
            / "aiseasons"
            / f"{season_settings.get('season_name')}.json"
        ).replace("\\", "/")
        try:
            with open(
                Path.cwd()
                / "ai_seasons"
                / f"{season_settings.get('season_name')}.json",
                "w",
            ) as file:
                file.write(json.dumps(season_file, indent=4))
            logger.debug("File write successful")
        except Exception as e:
            logger.error(
                f"Could not write to file {Path.cwd()}"
                / "ai_seasons"
                / f"{season_settings.get('season_name')}.json"
            )
            return False
        return True
    except Exception as e:
        logger.critical(e)
        return False


def _create_iracing_season(config: object, season_settings: dict) -> None:
    """
    Exists as a helper to create the season. If the season base file cannot be copied,
    it will return with no further action.
    """
    season_copied_bool = _copy_season_base_file(config, season_settings)
    if not season_copied_bool:
        return
    _update_season_settings(config, season_settings)


def _copy_roster_folder(config: object, season_settings: dict) -> None:
    """
    Performs a copy of selected series' base roster file into the iRacing airosters
    folder. It will exist in a folder titled what the user provided as roster.json.
    """
    roster_path_dest = (
        config.iracing_folder / "airosters" / season_settings.get("roster_name")
    )

    if season_settings.get("season_series") == "CUP":
        folder = base_files_roster_path / "2025_Cup_Series"
    elif season_settings.get("season_series") == "XFINITY":
        folder = base_files_roster_path / "2025_Xfinity_Series"
    elif season_settings.get("season_series") == "TRUCKS":
        folder = base_files_roster_path / "2025_Truck_Series"
    elif season_settings.get("season_series") == "ARCA":
        folder = base_files_roster_path / "2025_ARCA_Series"

    if not os.path.exists(roster_path_dest):
        logger.info(f"Folder {roster_path_dest} does not exist, creating")
        os.makedirs(roster_path_dest)

    try:
        logger.info(f"Copying roster folder {folder}")
        copytree(
            folder,
            config.iracing_folder
            / "airosters"
            / season_settings.get("roster_name"),
            dirs_exist_ok=True
        )
        logger.info("Folder copied successfully")
    except Exception as e:
        logger.error(f"Error copying file: {e}")


def _create_local_season_settings_file(values: dict, custom_tireset: int = 0) -> dict:
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
            "Warning! A season_settings file with that name already exists",
            no_titlebar=True,
        )
        return False
    season_settings = {
        "settings_version": "1.0",
        "season_name": values["__SEASONNAME__"],
        "season_series": _season_type(values),
        "roster_name": values["__ROSTERNAME__"],
        "fuel_capacity": int(values["__FUELCAPACITY__"]),
        "tire_sets": (
            "UNLIMITED" if values["__TIRESETSUNLIMITED__"] is True else custom_tireset
        ),
        "race_distance_percent": int(values["__RACEDISTANCEPERCENT__"]),
        "points_format": _points_format(values),
    }
    try:
        with open(
            ai_seasons_file_path / f"{values['__SEASONNAME__']}.json", "w"
        ) as new_season_file:
            new_season_file.write(json.dumps(season_settings, indent=4))
    except Exception as e:
        logger.error("Unable to write file")
        return {}

    return season_settings


def _points_format(values: dict) -> str:
    """
    Returns points format when called by _create_local_season_settings_file
    """
    if values["__CURRENTPOINTSFORMAT__"]:
        return "CURRENT"
    elif values["__CHASEPOINTSFORMAT__"]:
        return "CHASE"
    elif values["__WINSTONCUPPOINTSFORMAT__"]:
        return "WINSTON"


def _season_type(values: dict) -> str:
    """
    Returns season type when called by _create_local_season_settings_file
    """
    if values["__SEASONTYPECUP__"]:
        return "CUP"
    elif values["__SEASONTYPEXFINITY__"]:
        return "XFINITY"
    elif values["__SEASONTYPETRUCKS__"]:
        return "TRUCKS"
    elif values["__SEASONTYPEARCA__"]:
        return "ARCA"


def _block_focus(window) -> None:
    """
    Function to block focus on main_window when the create season dialog appears
    """
    for key in window.key_dict:  # Remove dash box of all Buttons
        element = window[key]
        if isinstance(element, sg.Button):
            element.block_focus()


def _create_new_season(config) -> dict:
    """
    Handles the popup window for creating a new season
    """
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
                            key="__SEASONTYPECUP__",
                            enable_events=True,
                        ),
                        sg.Radio(
                            "Xfinity",
                            group_id=1,
                            key="__SEASONTYPEXFINITY__",
                            enable_events=True,
                        ),
                        sg.Radio(
                            "Truck",
                            group_id=1,
                            key="__SEASONTYPETRUCKS__",
                            enable_events=True,
                        ),
                        sg.Radio(
                            "ARCA",
                            group_id=1,
                            key="__SEASONTYPEARCA__",
                            enable_events=True,
                        ),
                    ]
                ],
                title="Select series type",
                expand_x=True,
            )
        ],
        [
            sg.Frame(
                layout=[[sg.InputText(key="__ROSTERNAME__")]],
                title="Enter a name for the roster",
                expand_x=True,
            )
        ],
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
                    [
                        sg.Radio(
                            "Current",
                            group_id=2,
                            key="__CURRENTPOINTSFORMAT__",
                            default=True,
                        )
                    ],
                    [
                        sg.Radio(
                            "The Chase",
                            group_id=2,
                            key="__CHASEPOINTSFORMAT__",
                            disabled=True,
                        )
                    ],
                    [
                        sg.Radio(
                            "Winston Cup",
                            group_id=2,
                            key="__WINSTONCUPPOINTSFORMAT__",
                            disabled=True,
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
        [sg.Button("Create"), sg.Button("Cancel")],
    ]
    window = sg.Window(
        "Create New Season", layout, use_default_focus=False, finalize=True, modal=True
    )
    _block_focus(window)
    tire_sets = 0
    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, "Exit", "Cancel"):
            window.close()
            return
        if event == "Create":
            if not any(
                [values["__SEASONNAME__"], values["__ROSTERNAME__"]]
            ) and not all(
                [
                    values["__SEASONTYPECUP__"],
                    values["__SEASONTYPEXFINITY__"],
                    values["__SEASONTYPETRUCKS__"],
                    values["__SEASONTYPEARCA__"],
                ]
            ):
                sg.popup("Missing a required entry!", no_titlebar=True)
            else:
                season_settings = _create_local_season_settings_file(
                    values, window["__TIRESETS__"].get()
                )
                if season_settings:
                    _copy_roster_folder(config, season_settings)
                    _create_iracing_season(config, season_settings)
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
        else:
            logger.debug(f"{event}: {values}")
