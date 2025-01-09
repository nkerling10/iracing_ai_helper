"""
Details to come...
"""

## Standard library imports
import json
import logging
import time
import PySimpleGUI as sg
import sqlite3
import sys
from pathlib import Path

## Third party imports

## Local imports
from config.settings import Settings
from functions.race_manager.race_manager import main as race_manager
from functions.roster import roster_data
from functions.roster.randomizer import randomizer
from functions.season import season_data
from functions.database.db_manager import DatabaseManager
from layouts.tabs.config_tab import ConfigTabLayout
from layouts.tabs.database_tab import DatabaseTabLayout
from layouts.tabs.roster_tab import RosterTabLayout
from layouts.tabs.season_tab import SeasonTabLayout
from layouts.tabs.logging_tab import LoggingTabLayout


logging.basicConfig()


def _load_roster_file() -> None:
    active_driver_data, inactive_driver_data = (
        roster_data.build_driver_display_info(config.local_roster_file)
    )
    window["-ROSTERFILELOADED-"].update(f"File loaded: {config.local_roster_file}")
    window["-ACTIVEDRIVERS-"].update(values=active_driver_data)
    window["-INACTIVEDRIVERS-"].update(values=inactive_driver_data)


def _load_season_file() -> None:
    colored_rows = []
    season_rows = season_data.build_season_display_info(config.local_season_file)
    next_race = [next(x[0]-1 for x in season_rows if x[3] is False)]
    done_races = [([x[0]-1], "white", "green") for x in season_rows if x[3] is True]
    not_done_races = [([x[0]-1], "white", "red") for x in season_rows if x[3] is False and x[0]-1 != next_race]
    for each in not_done_races:
        colored_rows.append(each)
    for each in done_races:
        colored_rows.append(each)
    colored_rows.append((next_race, "white", "orange"))
    window["-SEASONTABLE-"].update(values=season_rows, row_colors=colored_rows)
    window["-SEASONFILELOADED-"].update(f"File loaded: {config.local_season_file}")
    window["-TRACKBOXLABEL-"].update(visible=True)
    window["-TRACKBOX-"].update(values=RosterTabLayout._roster_file_track_choices(len(season_rows)),
                                visible=True)


def _set_tab_visibility(tab_status) -> None:
    window["-maintab-"].update(visible=tab_status)
    window["-databasetab-"].update(visible=tab_status)
    window["-rostertab-"].update(visible=tab_status)
    window["-seasontab"].update(visible=tab_status)
    window["-standingstab-"].update(visible=tab_status)


def _build_layout() -> list[list]:
    main_tab_layout = [[sg.Button(button_text="Start", key="-RACEMANAGER-"),
                        sg.Button(button_text="Stop", key="-BUTTONEXCEPTION-")]]
    db_tab_layout = DatabaseTabLayout.build_db_tab_layout()
    roster_tab_layout = RosterTabLayout.build_roster_tab_layout()
    season_tab_layout = SeasonTabLayout.build_season_tab_layout()
    standings_tab_layout = [[]]
    config_tab_layout = ConfigTabLayout.build_config_tab_layout(config.database_path,
                                                                config.local_roster_file,
                                                                config.local_season_file,
                                                                config.iracing_ai_roster_folder,
                                                                config.iracing_ai_season_folder)
    logging_tab_layout = LoggingTabLayout._build_logging_tab_layout()

    return [
        [
            sg.TabGroup(
                [
                    [
                        #TODO: create/load season button
                        sg.Tab("Main", main_tab_layout, key="-maintab-"),
                        sg.Tab("Database", db_tab_layout, key="-databasetab-"),
                        sg.Tab("Roster", roster_tab_layout, key="-rostertab-"),
                        sg.Tab("Season", season_tab_layout, key="-seasontab"),
                        sg.Tab("Standings", standings_tab_layout, key="-standingstab-"),
                        sg.Tab("Config", config_tab_layout, key="-configtab-", visible=True),
                        sg.Tab("Logging", logging_tab_layout, key="-loggingtab-", visible=True)
                    ]
                ],
                key="-tabgroup1-",
                tab_location="topleft"
            )
        ],
        [sg.Exit()]
    ]


def main_window():
    db_table_options = []
    '''
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(module)s [%(levelname)s] %(message)s",
        force=True,
    )
    '''
    logger = logging.getLogger()

    if config.first_time_setup is True:
        logger.debug("config.first_time_setup is True, hiding tabs")
        _set_tab_visibility(False)
    else:
        logger.debug("config.first_time_setup is False, displaying tabs")
        _set_tab_visibility(True)
        _load_roster_file()
        _load_season_file()

    prev_table = ""
    while True:
        event, values = window.read()#timeout=1000)
        if event in (sg.WIN_CLOSED, "Exit"):
            try:
                db.conn.close()
            except:
                pass
            break
        if event == "-SAVECONFIGBUTTON-":
            result = ""
            if not any([values["-LOCALDATABASEFILE-"],
                       values["-LOCALROSTERFOLDER-"],
                       values["-LOCALSEASONFILE-"],
                       values["-IRACINGAIROSTERFOLDER-"],
                       values["-IRACINGAISEASONFOLDER-"]]):
                result = sg.popup("Please select a file for each required item",
                         no_titlebar=True,
                         background_color="gray")
            if not result:
                config._write_settings(
                    values["-LOCALDATABASEFILE-"],
                    values["-LOCALROSTERFOLDER-"],
                    values["-LOCALSEASONFILE-"],
                    values["-IRACINGAIROSTERFOLDER-"],
                    values["-IRACINGAISEASONFOLDER-"]
                )
                _set_tab_visibility(True)
        if event == "-RACEMANAGER-":
            pass
            #race_manager()
        if event == "-DBTABCONNECTBUTTON-":
            db = DatabaseManager(config.database_path)
            window["-DBTABCONNECTTEXT-"].update(config.database_path)
            window["-DBTABCONNECTCOMBO-"].update(values=db.tables, size=(30, 50))
            for table in db.tables:
                db_table_options.append(table)
        if event == "-DBTABCONNECTCOMBO-":
            try:
                if prev_table != "":
                    window["-DBTABTABLE-", prev_table].table_frame.master.destroy()
                    del window.AllKeysDict["-DBTABTABLE-", prev_table]
                results, headers = db.execute_query(values["-DBTABCONNECTCOMBO-"])
                window.extend_layout(window["-DBTABLECOLUMN-"], [[sg.Table(
                        values=results,
                        headings=headers,
                        justification="center",
                        key=("-DBTABTABLE-", values["-DBTABCONNECTCOMBO-"]),
                        num_rows=30,
                        auto_size_columns=True,
                        expand_x=True,
                        expand_y=True
                    )]])
                prev_table = values["-DBTABCONNECTCOMBO-"]
                window.refresh()
            except Exception as e:
                print(e)
        if event == "-LOADROSTERBUTTON-":
            active_driver_data, inactive_driver_data = (
                roster_data.build_driver_display_info(config.local_roster_file)
            )
            window["-ROSTERFILELOADED-"].update(f"File loaded: {config.local_roster_file}")
            window["-ACTIVEDRIVERS-"].update(values=active_driver_data)
            window["-INACTIVEDRIVERS-"].update(values=inactive_driver_data)
        if event == "-LOADSEASONBUTTON-":
            colored_rows = []
            season_rows = season_data.build_season_display_info(config.local_season_path)
            next_race = [next(x[0]-1 for x in season_rows if x[3] is False)]
            done_races = [([x[0]-1], "white", "green") for x in season_rows if x[3] is True]
            not_done_races = [([x[0]-1], "white", "red") for x in season_rows if x[3] is False and x[0]-1 != next_race]
            for each in not_done_races:
                colored_rows.append(each)
            for each in done_races:
                colored_rows.append(each)
            colored_rows.append((next_race, "white", "orange"))
            window["-SEASONTABLE-"].update(values=season_rows, row_colors=colored_rows)
            window["-SEASONFILELOADED-"].update(f"File loaded: {config.local_season_path}")
            window["-TRACKBOXLABEL-"].update(visible=True)
            window["-TRACKBOX-"].update(values=RosterTabLayout._roster_file_track_choices(len(season_rows)),
                                        visible=True)
        if event == "Randomize":
            randomizer.main(str(values["-TRACKBOX-"]), config.local_roster_file)
            window["-TRACKSTATUS-"].update("Success!")
            active_driver_data, inactive_driver_data = (
                roster_data.build_driver_display_info(config.local_roster_file)
            )
            window["-ACTIVEDRIVERS-"].update(values=active_driver_data)
            window["-INACTIVEDRIVERS-"].update(values=inactive_driver_data)
            window.read(timeout=1500)
            window["-TRACKSTATUS-"].update("")
        if event == "Copy":
            randomizer.perform_copy(config.local_roster_file)
        if event == "-CLEARLOGBOX-":
            window["-LOGGINGBOX-"].update("")
        if event == "-SEASONTABLE-":
            window["-TRACKBOX-"].update(value=values['-SEASONTABLE-'][0]+1)


if __name__ == "__main__":
    sg.theme("Python")
    config = Settings()
    #config.first_time_setup = True

    #TODO: create functionality for first time setup window to set system paths
    #TODO: build copy or download feature to take base provided files with the tool

    window = sg.Window(
        "NSK AI Roster Randomizer - Alpha v0.1",
        _build_layout(),
        no_titlebar=False,
        finalize=True,
    )

    main_window()
