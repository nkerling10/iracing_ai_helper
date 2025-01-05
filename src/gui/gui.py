"""
Details to come...
"""

## Standard library imports
import json
import logging
import PySimpleGUI as sg
from pathlib import Path
## Third party imports

## Local imports
from functions.roster import roster_data
from functions.roster.randomizer import randomizer
from layouts.tab_layouts import RosterTabLayout
from layouts.tab_layouts import SeasonTabLayout
from layouts.tab_layouts import LoggingTabLayout


logging.basicConfig()

def build_layout() -> list[list]:
    main_tab_layout = [[sg.Ok()]]
    roster_tab_layout = RosterTabLayout.build_roster_tab_layout()
    season_tab_layout = SeasonTabLayout.build_season_tab_layout({})
    standings_tab_layout = [[]]
    logging_tab_layout = LoggingTabLayout._build_logging_tab_layout()
    #logging_tab_layout = [[]]

    layout = [[sg.TabGroup([[sg.Tab("Main", main_tab_layout, key="-maintab-"),
                            sg.Tab("Roster", roster_tab_layout, key="-rostertab-"),
                            sg.Tab("Season", season_tab_layout, key="-seasontab"),
                            sg.Tab("Standings", standings_tab_layout, key="-standingstab-"),
                            sg.Tab("Logging", logging_tab_layout, key="-loggingtab-")]],
                            key="-tabgroup1-", tab_location="topleft"),],
                [sg.Exit()]]

    return layout

def main_window():
    window = sg.Window(
        "NSK AI Roster Randomizer - Alpha v0.1",
        build_layout(),
        #no_titlebar=True,
        finalize=True
    )
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(module)s [%(levelname)s] %(message)s",
        force=True
    )
    logger = logging.getLogger()
    while True:
        event, values = window.read(timeout=1000)
        if event in (sg.WIN_CLOSED, None, "Exit"):
            break
        if event == "-LOADROSTERBUTTON-":
            active_driver_data, inactive_driver_data = roster_data.build_driver_display_info(local_roster_path)
            window["-ROSTERFILELOADED-"].update(f"File loaded: {local_roster_path}")
            window["-ACTIVEDRIVERS-"].update(values=active_driver_data)
            window["-INACTIVEDRIVERS-"].update(values=inactive_driver_data)
        if event == "Randomize":
            randomizer.main(values["-TRACKBOX-"], local_roster_path)
            window["-TRACKSTATUS-"].update("Success!")
            active_driver_data, inactive_driver_data = roster_data.build_driver_display_info(local_roster_path)
            window["-ACTIVEDRIVERS-"].update(values=active_driver_data)
            window["-INACTIVEDRIVERS-"].update(values=inactive_driver_data)
            window.read(timeout=1500)
            window["-TRACKSTATUS-"].update("")
        if event == "Copy":
            randomizer.perform_copy(local_roster_path)
        if event == "-CLEARLOGBOX-":
            window["-LOGGINGBOX-"].update("")


if __name__ == "__main__":
    sg.theme("Python")
    settings = sg.UserSettings(
        path = Path.cwd() / "src" / "gui" / "assets" / "config",
        filename="roster_tab_config.ini",
        use_config_file=True,
        convert_bools_and_none=True
    )
    local_roster_path = settings["PATHS"]["LOCAL_ROSTER"]
    iracing_ai_roster_path = settings["PATHS"]["AI_ROSTER_FOLDER"]
    
    main_window()