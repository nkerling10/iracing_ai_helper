import json
import logging
import os
import PySimpleGUI as sg
from pathlib import Path

logger = logging.getLogger(__name__)

ai_seasons_file_path = Path.cwd() / "ai_seasons"

def _create_local_season_file(values: dict) -> bool:
    if not os.path.exists(ai_seasons_file_path):
        logger.info(f"Folder {ai_seasons_file_path} does not exist, creating")
        os.makedirs(ai_seasons_file_path)
    if os.path.exists(ai_seasons_file_path / f"{values['__SEASONNAME__']}.json"):
        sg.Popup("Warning! A season file with that name already exists")
        return False
    with open(ai_seasons_file_path / f"{values['__SEASONNAME__']}.json", "w") as new_season_file:
        new_season_file.write(
            json.dumps(
                {
                    "season_info": {
                        "season_name": values["__SEASONNAME__"],
                        "roster_folder": values["__ROSTERFOLDERINPUT__"],
                        "season_file": "OFFICIAL" if values["__OFFICIALSEASONFILE__"]
                            is True else values["__SEASONFILEINPUT__"],
                        "season_series": _season_type(values),
                        "race_distance_percent": int(values["__RACEDISTANCEPERCENT__"]),
                        "points_format": _points_format(values)
                    },
                    "season_drivers": {},
                    "season_races": {}
                },
                indent=4))
        return True


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
    for key in window.key_dict:    # Remove dash box of all Buttons
        element = window[key]
        if isinstance(element, sg.Button):
            element.block_focus()


def _create_new_season(config) -> dict:
    layout = [
        [sg.Frame(layout=[[sg.InputText(key="__SEASONNAME__")]],
                  title="Enter a name for the season",
                  expand_x=True)],
        [sg.Frame(layout=[[sg.FolderBrowse(key="__ROSTERFOLDER__",
                                           target="__ROSTERFOLDERINPUT__",
                                           initial_folder=config.iracing_folder / "airosters"),
                           sg.Input(key="__ROSTERFOLDERINPUT__",
                                    disabled=True,
                                    text_color="black")]],
                  title="Select desired iRacing roster folder",
                  expand_x=True)],
        [sg.Frame(layout=[[sg.FileBrowse(key="__SEASONFILE__",
                                         target="__SEASONFILEINPUT__",
                                         file_types = (("JSON Files", "*.json"),),
                                         initial_folder=config.iracing_folder / "aiseasons"),
                           sg.Input(key="__SEASONFILEINPUT__",
                                    disabled=True,
                                    text_color="black")],
                            [sg.Text("or")],
                            [sg.Checkbox(text='Use "official" season file', key="__OFFICIALSEASONFILE__")]],
                  title="Select desired season file",
                  expand_x=True)],
        [sg.Frame(layout=[[sg.Radio("Cup", group_id=1, key="__SEASONTYPECUP__"),
                           sg.Radio("Xfinity", group_id=1, key="__SEASONTYPEXFINITY__"),
                           sg.Radio("Truck", group_id=1, key="__SEASONTYPETRUCKS__"),
                           sg.Radio("ARCA", group_id=1, key="__SEASONTYPEARCA__")]],
                  title="Select series type",
                  expand_x=True)],
        [
            sg.Frame(layout=[[sg.Slider(range=(10, 100), default_value=100,
                                        orientation="horizontal", key="__RACEDISTANCEPERCENT__",
                                        expand_x=True)]],
                    title="Select desired race distance",
                    expand_x=True,
                    expand_y=True,),
            sg.Frame(layout=[[sg.Radio("Current", group_id=2, key="__CURRENTPOINTSFORMAT__", default=True)],
                             [sg.Radio("The Chase", group_id=2, key="__CHASEPOINTSFORMAT__")],
                             [sg.Radio("Winston Cup", group_id=2, key="__WINSTONCUPPOINTSFORMAT__")]],
                    title="Points format",
                    expand_x=True,
                    expand_y=True)
        ],
        [sg.Button("Create"), sg.Button("Cancel")]
    ]
    window = sg.Window("Create New Season", layout, use_default_focus=False, finalize=True, modal=True)
    _block_focus(window)
    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, "Exit", "Cancel"):
            window.close()
            return
        if event == "Create":
            if not any([values["__SEASONNAME__"], values["__ROSTERFOLDERINPUT__"]]) and not all([
                            values["__SEASONTYPECUP__"], values["__SEASONTYPEXFINITY__"],
                            values["__SEASONTYPETRUCKS__"], values["__SEASONTYPEARCA__"]]):
                sg.popup("Missing a required entry!", no_titlebar=True)
            if not any([values["__SEASONFILEINPUT__"], values["__OFFICIALSEASONFILE__"]]):
                sg.popup("You must either select an iRacing season file or check the box to use the official season")
            else:
                result = _create_local_season_file(values)
                if result:
                    window.close()
                    return True
        else:
            print(event, values)
