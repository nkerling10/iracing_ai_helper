"""
Details to come...
"""

## Standard library imports
import json
import logging
import threading
import time
import PySimpleGUI as sg
import sqlite3
from pathlib import Path

## Third party imports

## Local imports
from functions.race_manager.race_manager import main as race_manager
from functions.race_manager.race_manager import ButtonException
from functions.roster import roster_data
from functions.roster.randomizer import randomizer
from functions.season import season_data
from functions.database.db_manager import DatabaseManager
from layouts.tabs.database_tab import DatabaseTabLayout
from layouts.tabs.roster_tab import RosterTabLayout
from layouts.tabs.season_tab import SeasonTabLayout
from layouts.tabs.logging_tab import LoggingTabLayout


logging.basicConfig()


def build_layout() -> list[list]:
    main_tab_layout = [[sg.Button(button_text="Start", key="-RACEMANAGER-"),
                        sg.Button(button_text="Stop", key="-BUTTONEXCEPTION-")]]
    db_tab_layout = DatabaseTabLayout.build_db_tab_layout()
    roster_tab_layout = RosterTabLayout.build_roster_tab_layout()
    season_tab_layout = SeasonTabLayout.build_season_tab_layout()
    standings_tab_layout = [[]]
    logging_tab_layout = LoggingTabLayout._build_logging_tab_layout()

    layout = [
        [
            sg.TabGroup(
                [
                    [
                        sg.Tab("Main", main_tab_layout, key="-maintab-"),
                        sg.Tab("Database", db_tab_layout, key="-databasetab-"),
                        sg.Tab("Roster", roster_tab_layout, key="-rostertab-"),
                        sg.Tab("Season", season_tab_layout, key="-seasontab"),
                        sg.Tab("Standings", standings_tab_layout, key="-standingstab-"),
                        sg.Tab("Logging", logging_tab_layout, key="-loggingtab-"),
                    ]
                ],
                key="-tabgroup1-",
                tab_location="topleft",
            ),
        ],
        [sg.Exit()],
    ]

    return layout


def main_window():
    db_table_options = []
    window = sg.Window(
        "NSK AI Roster Randomizer - Alpha v0.1",
        build_layout(),
        no_titlebar=False,
        finalize=True,
    )
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(module)s [%(levelname)s] %(message)s",
        force=True,
    )
    logger = logging.getLogger()
    prev_table = ""
    while True:
        event, values = window.read(timeout=1000)
        if event in (sg.WIN_CLOSED, None, "Exit"):
            try:
                db.conn.close()
            except:
                pass
            break
        if event == "-RACEMANAGER-":
            pass
            #race_manager()
        if event == "-DBTABCONNECTBUTTON-":
            db = DatabaseManager(database_path)
            window["-DBTABCONNECTTEXT-"].update(database_path)
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
                roster_data.build_driver_display_info(local_roster_path)
            )
            window["-ROSTERFILELOADED-"].update(f"File loaded: {local_roster_path}")
            window["-ACTIVEDRIVERS-"].update(values=active_driver_data)
            window["-INACTIVEDRIVERS-"].update(values=inactive_driver_data)
        if event == "-LOADSEASONBUTTON-":
            colored_rows = []
            season_rows = season_data.build_season_display_info(local_season_path)
            next_race = [next(x[0]-1 for x in season_rows if x[3] is False)]
            done_races = [([x[0]-1], "white", "green") for x in season_rows if x[3] is True]
            not_done_races = [([x[0]-1], "white", "red") for x in season_rows if x[3] is False and x[0]-1 != next_race]
            for each in not_done_races:
                colored_rows.append(each)
            for each in done_races:
                colored_rows.append(each)
            colored_rows.append((next_race, "white", "orange"))
            window["-SEASONTABLE-"].update(values=season_rows, row_colors=colored_rows)
            window["-SEASONFILELOADED-"].update(f"File loaded: {local_season_path}")
            window["-TRACKBOXLABEL-"].update(visible=True)
            window["-TRACKBOX-"].update(values=RosterTabLayout._roster_file_track_choices(len(season_rows)),
                                        visible=True)
        if event == "Randomize":
            randomizer.main(str(values["-TRACKBOX-"]), local_roster_path)
            window["-TRACKSTATUS-"].update("Success!")
            active_driver_data, inactive_driver_data = (
                roster_data.build_driver_display_info(local_roster_path)
            )
            window["-ACTIVEDRIVERS-"].update(values=active_driver_data)
            window["-INACTIVEDRIVERS-"].update(values=inactive_driver_data)
            window.read(timeout=1500)
            window["-TRACKSTATUS-"].update("")
        if event == "Copy":
            randomizer.perform_copy(local_roster_path)
        if event == "-CLEARLOGBOX-":
            window["-LOGGINGBOX-"].update("")
        if event == "-SEASONTABLE-":
            window["-TRACKBOX-"].update(value=values['-SEASONTABLE-'][0]+1)


if __name__ == "__main__":
    sg.theme("Python")
    settings = sg.UserSettings(
        path=Path.cwd() / "src" / "gui" / "assets" / "config",
        filename="config.ini",
        use_config_file=True,
        convert_bools_and_none=True,
    )
    database_path = settings["SYSTEM"]["DATABASE_PATH"]
    local_roster_path = settings["PATHS"]["LOCAL_ROSTER"]
    iracing_ai_roster_path = settings["PATHS"]["AI_ROSTER_FOLDER"]
    local_season_path = settings["PATHS"]["LOCAL_SEASON"]

    main_window()
