"""
Details to come...
"""

## Standard library imports
import logging
import os
import PySimpleGUI as sg
from pathlib import Path

## Third party imports

## Local imports
from gui.config.settings import Settings
from gui.functions.race_manager.race_manager import main as race_manager
from gui.functions.roster import roster_data
from gui.functions.roster.randomizer import randomizer
from gui.functions.database.db_manager import DatabaseManager
from gui.helpers.create_new_season import _create_new_season
from gui.helpers.load_season_file import LoadSeasonFile
from gui.layouts.tabs.splash_tab import SplashTabLayout
from gui.layouts.tabs.database_tab import DatabaseTabLayout
from gui.layouts.tabs.local_files_tabs import LocalFileTab
from gui.layouts.tabs.local_files.roster_tab import RosterTabLayout
from gui.layouts.tabs.local_files.season_tab import SeasonTabLayout
from gui.layouts.tabs.config_tab import ConfigTabLayout
from gui.layouts.tabs.logging_tab import LoggingTabLayout


logging.basicConfig()


def _load_roster_file(logger: object) -> None:
    logger.info("Loading roster file")
    active_driver_data, inactive_driver_data = (
        roster_data.build_driver_display_info(config.iracing_folder / "airosters" / "2025_Xfinity_Series_NSK_AI")
    )
    logger.info("Updating roster table values")
    window["-ACTIVEDRIVERS-"].update(values=active_driver_data)
    window["-INACTIVEDRIVERS-"].update(values=inactive_driver_data)


def _load_season_file(logger: object) -> None:
    logger.info("Loading season file")
    season_rows, colored_rows = LoadSeasonFile._load_season_file(config)
    logger.info("Updating season table values")
    window["-SEASONTABLE-"].update(values=season_rows, row_colors=colored_rows)
    window["-TRACKBOXLABEL-"].update(visible=True)
    window["-TRACKBOX-"].update(values=RosterTabLayout._roster_file_track_choices(len(season_rows)),
                                visible=True)


def _set_tab_visibility(tab_status: bool) -> None:
    window["-maintab-"].update(visible=tab_status)
    window["-databasetab-"].update(visible=tab_status)
    window["-localfiletab-"].update(visible=tab_status)


def _build_main_layout() -> list[list]:
    splash_tab_layout = SplashTabLayout.build_splash_tab_layout()
    db_tab_layout = DatabaseTabLayout.build_db_tab_layout()
    local_files_tab_layout = LocalFileTab._build_local_file_tab()
    config_tab_layout = ConfigTabLayout.build_config_tab_layout(config.database_path,
                                                                config.iracing_folder)
    logging_tab_layout = LoggingTabLayout._build_logging_tab_layout()

    return [
        [
            sg.TabGroup(
                [
                    [
                        sg.Tab("Home", splash_tab_layout, key="-maintab-"),
                        sg.Tab("Database", db_tab_layout, key="-databasetab-"),
                        sg.Tab("Local Files", local_files_tab_layout, key="-localfiletab-"),
                        sg.Tab("Config", config_tab_layout, key="-configtab-", visible=True),
                        sg.Tab("Logging", [[]], key="-loggingtab-", visible=True)
                    ]
                ],
                key="-tabgroup1-",
                tab_location="topleft"
            )
        ],
        [sg.Exit()]
    ]


def main_window() -> None:
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(module)s [%(levelname)s] %(message)s",
        force=True,
    )
    logger = logging.getLogger()
    logger.info("Main window has been loaded, logger has been instantiated")
    if config.first_time_setup is True:
        logger.debug("config.first_time_setup is True, hiding tabs")
        _set_tab_visibility(False)
    else:
        logger.debug("config.first_time_setup is False, displaying tabs")
        _set_tab_visibility(True)
        _load_roster_file(logger)
        _load_season_file(logger)
    logger.debug("Starting infinite gui loop, happy racing :)")
    while True:
        event, values = window.read()#timeout=1000)
        if event in (sg.WIN_CLOSED, "Exit"):
            try:
                logger.debug("Attempting to close database connection")
                db.conn.close()
            except:
                logger.debug("Database disconnect unnecessary, skipping operation")
                pass
            break
        if event == "-SAVECONFIGBUTTON-":
            if not any([values["-LOCALDATABASEFILE-"],
                       values["-LOCALROSTERFOLDER-"],
                       values["-LOCALSEASONFILE-"],
                       values["-IRACINGAIROSTERFOLDER-"],
                       values["-IRACINGAISEASONFOLDER-"]]):
                config_fail = sg.popup("Please select a file for each required item",
                                        no_titlebar=True,
                                        background_color="gray")
            if not config_fail:
                config._write_settings(
                    values["-LOCALDATABASEFILE-"],
                    values["-LOCALROSTERFOLDER-"],
                    values["-LOCALSEASONFILE-"],
                    values["-IRACINGAIROSTERFOLDER-"],
                    values["-IRACINGAISEASONFOLDER-"]
                )
                _set_tab_visibility(True)
        if event == "-LOADSAVEDSEASONBUTTON-":
            loaded_season = sg.popup_get_file("Load a Season", initial_folder=Path.cwd() / "ai_seasons")
        if event == "-CREATESEASONBUTTON-":
            new_season = _create_new_season(config)
            window["-LOADSAVEDSEASONBUTTON-"].update(disabled=False)
            ##TODO: Proceed to load newly created season
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
        if event == "-LOADSEASONFILEBUTTON-":
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
    #TODO: build copy or download feature to take base provided files with the tool
    window = sg.Window(
        "NSK AI Roster Randomizer - Alpha v0.1",
        _build_main_layout(),
        no_titlebar=False,
        finalize=True,
    )

    db_table_options = []
    prev_table = ""
    config_fail = ""

    main_window()
