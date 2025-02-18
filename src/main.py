## Standard library imports
import coloredlogs
import json
import logging
from pathlib import Path

## Third party imports
import PySimpleGUI as sg

## Local imports
from config.app_settings.settings import Settings
from gui.main_menu.season import season_menu_window
from gui.main_menu.single_race import singlerace_window
from gui.main_menu.settings import settings_window


logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(module)s [%(levelname)s] %(message)s",
    force=True
)


class IracingData:
    def __init__(self):
        self.cars = self._load_data("iracing_cars.json")
        self.tracks = self._load_data("iracing_tracks.json")

    def _load_data(self, file: str):
        with open(Path.cwd() / "src" / "assets" / "references" / file) as data_file:
            return json.loads(data_file.read())


def _menu_column_layout() -> list[list]:
    return [
        [
            sg.pin(sg.Button("Season",
                    key="--SEASONRACEMENUBUTTON--",
                    size=(None, 15),
                    enable_events=True)),
            sg.pin(sg.Button("Single Race",
                    key="--SINGLERACEMENUBUTTON--",
                    size=(None, 15),
                    enable_events=True)),
            sg.pin(sg.Button("Settings",
                    key="--SETTINGSMENUBUTTON--",
                    size=(None, 15),
                    enable_events=True)),
            sg.Push(),
            sg.pin(sg.Button("About",
                    key="--ABOUTMENUBUTTON--",
                    size=(None, 15),
                    enable_events=True)),
            sg.pin(sg.Exit())
        ]
    ]


def _splash_area_layout() -> list[list]:
    return [
        [
            sg.Image(
                source="C:/Users/Nick/Documents/iracing_ai_helper/src/assets/images/chase_splash_500x300.png",
                expand_x=True,
                expand_y=True
            )
        ]
    ]


def _main_menu_layout() -> list[list]:
    return [
        [
            sg.pin(sg.Text("iRacing AI Integrator", expand_x=True))
        ],
        [
            sg.pin(sg.Column(layout=_menu_column_layout(), expand_x=True, expand_y=True))
        ],
        [
            sg.HorizontalSeparator()
        ],
        [
            sg.Column(layout=_splash_area_layout(), expand_x=True, expand_y=True, key="__SPLASHLAYOUT__")
        ]
    ]


def main():
    iracing_data = IracingData()
    window = sg.Window(
        "Race Type Selection",
        _main_menu_layout(),
        no_titlebar=False,
        finalize=True,
        size=(650,350)
    )
    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, "Exit"):
            return
        if event == "--SEASONRACEMENUBUTTON--":
            season_menu_window.main()
        if event == "--SINGLERACEMENUBUTTON--":
            singlerace_window.main()
        if event == "--SETTINGSMENUBUTTON--":
            settings_window.main()
        if event == "--ABOUTMENUBUTTON--":
            pass

if __name__ == "__main__":
    logger = logging.getLogger()
    coloredlogs.install(level='DEBUG', logger=logger)
    config = Settings()
    main()
