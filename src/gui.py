"""
Details to come...
"""

## Standard library imports
import json
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
from gui.layouts.tabs.season_tab import SeasonTab
from gui.layouts.tabs.season_subtabs.roster_tab import RosterTabLayout
from gui.layouts.tabs.season_subtabs.schedule_tab import ScheduleTabLayout
from gui.layouts.tabs.config_tab import ConfigTabLayout
from gui.layouts.tabs.logging_tab import LoggingTabLayout


logging.basicConfig()


def _connect_to_local_db() -> object:
    logger.info(f"Attempting connection to local database: {config.database_path}")
    try:
        db = DatabaseManager(config.database_path)
        logger.info("Database connection successful")
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
    window["-DBTABCONNECTTEXT-"].update(config.database_path)
    window["-DBTABCONNECTCOMBO-"].update(values=db.tables, size=(30, 50))
    window["-DBTABCONNECTBUTTON-"].update(disabled=True)
    for table in db.tables:
        db_table_options.append(table)

    return db


def _open_saved_season(loaded_season: str) -> dict:
    try:
        with open(loaded_season, "r") as file:
            return json.loads(file.read())
    except Exception as e:
        logger.warning(f"ERROR: Unable to open {loaded_season}")


def _load_roster_file(season: dict) -> None:
    logger.info("Loading roster file")
    active_driver_data, inactive_driver_data = roster_data.build_driver_display_info(
        config.iracing_folder / "airosters" / season.get("roster_name")
    )
    logger.info("Updating roster table values")
    window["-ACTIVEDRIVERS-"].update(values=active_driver_data)
    window["-INACTIVEDRIVERS-"].update(values=inactive_driver_data)


def _load_iracing_season_file(season: dict) -> None:
    logger.info("Loading season file")
    season_rows, colored_rows = LoadSeasonFile._load_season_file(config, season)
    logger.info("Updating season table values")
    window["-SCHEDULETABLE-"].update(values=season_rows, row_colors=colored_rows)
    window["-TRACKBOXLABEL-"].update(visible=True)
    window["-TRACKBOX-"].update(values=RosterTabLayout._roster_file_track_choices(len(season_rows)), visible=True)


def _set_tab_visibility(tab_status: bool) -> None:
    window["-hometab-"].update(visible=tab_status)
    window["-databasetab-"].update(visible=tab_status)
    window["-seasontab-"].update(visible=tab_status)


def _build_main_layout() -> list[list]:
    splash_tab_layout = SplashTabLayout.build_splash_tab_layout()
    season_tab_layout = SeasonTab._build_season_tab()
    db_tab_layout = DatabaseTabLayout.build_db_tab_layout()
    config_tab_layout = ConfigTabLayout.build_config_tab_layout(config.database_path, config.iracing_folder)
    logging_tab_layout = LoggingTabLayout._build_logging_tab_layout()

    return [
        [
            sg.TabGroup(
                [
                    [
                        sg.Tab("Home", splash_tab_layout, key="-hometab-"),
                        sg.Tab("Season", season_tab_layout, key="-seasontab-"),
                        sg.Tab("Database", db_tab_layout, key="-databasetab-"),
                        sg.Tab("Config", config_tab_layout, key="-configtab-", visible=True),
                        sg.Tab("Logging", [[]], key="-loggingtab-", visible=True),
                    ]
                ],
                key="-tabgroup1-",
                tab_location="topleft",
            )
        ],
        [sg.Exit()],
    ]


def main_window(prev_table: str) -> None:
    if config.first_time_setup is True:
        logger.debug("config.first_time_setup is True, hiding tabs")
        _set_tab_visibility(False)
    else:
        logger.debug("config.first_time_setup is False, displaying tabs")
        _set_tab_visibility(True)
    db = _connect_to_local_db()
    logger.debug("Starting infinite gui loop, happy racing :)")
    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, "Exit"):
            try:
                logger.debug("Attempting to close database connection")
                db.conn.close()
            except:
                logger.debug("Database disconnect unnecessary, skipping operation")
                pass
            break
        if event == "-SAVECONFIGBUTTON-":
            if not any(
                [
                    values["-LOCALDATABASEFILE-"],
                    values["-LOCALROSTERFOLDER-"],
                    values["-LOCALSEASONFILE-"],
                    values["-IRACINGAIROSTERFOLDER-"],
                    values["-IRACINGAISEASONFOLDER-"],
                ]
            ):
                config_fail = sg.popup(
                    "Please select a file for each required item", no_titlebar=True, background_color="gray"
                )
            if not config_fail:
                config._write_settings(
                    values["-LOCALDATABASEFILE-"],
                    values["-LOCALROSTERFOLDER-"],
                    values["-LOCALSEASONFILE-"],
                    values["-IRACINGAIROSTERFOLDER-"],
                    values["-IRACINGAISEASONFOLDER-"],
                )
                _set_tab_visibility(True)
        if event in ["-LOADSAVEDSEASONBUTTON-", "-CREATESEASONBUTTON-"]:
            if event == "-LOADSAVEDSEASONBUTTON-":
                select_season_file = sg.popup_get_file(
                    "Load a Season", initial_folder=Path.cwd() / "ai_seasons", no_window=True
                )
                if select_season_file:
                    season = _open_saved_season(select_season_file)
            if event == "-CREATESEASONBUTTON-":
                season = _create_new_season(config)
                if season:
                    window["-LOADSAVEDSEASONBUTTON-"].update(disabled=False)
            try:
                if season:
                    _load_iracing_season_file(season)
                    _load_roster_file(season)
                    window["-seasontab-"].select()
            except UnboundLocalError:
                continue
        if event == "-DBTABCONNECTBUTTON-":
            _connect_to_local_db()
        if event == "-DBTABCONNECTCOMBO-":
            try:
                if prev_table != None:
                    window["-DBTABTABLE-", prev_table].table_frame.master.destroy()
                    del window.AllKeysDict["-DBTABTABLE-", prev_table]
                results, headers = db.execute_query(values["-DBTABCONNECTCOMBO-"])
                window.extend_layout(
                    window["-DBTABLECOLUMN-"],
                    [
                        [
                            sg.Table(
                                values=results,
                                headings=headers,
                                justification="center",
                                key=("-DBTABTABLE-", values["-DBTABCONNECTCOMBO-"]),
                                num_rows=30,
                                auto_size_columns=True,
                                expand_x=True,
                                expand_y=True,
                            )
                        ]
                    ],
                )
                prev_table = values["-DBTABCONNECTCOMBO-"]
                window.refresh()
            except Exception as e:
                logger.error(e)
        if event == "Randomize":
            randomizer.main(str(values["-TRACKBOX-"]), Path(season.get("roster_folder")) / "roster.json")
            window["-TRACKSTATUS-"].update("Success!")
            active_driver_data, inactive_driver_data = roster_data.build_driver_display_info(
                season.get("roster_folder")
            )
            window["-ACTIVEDRIVERS-"].update(values=active_driver_data)
            window["-INACTIVEDRIVERS-"].update(values=inactive_driver_data)
            window["-TRACKSTATUS-"].update("")
        if event == "Copy":
            randomizer.perform_copy(config.local_roster_file)
        if event == "-CLEARLOGBOX-":
            window["-LOGGINGBOX-"].update("")
        if event == "-SCHEDULETABLE-":
            window["-TRACKBOX-"].update(value=values["-SCHEDULETABLE-"][0] + 1)


if __name__ == "__main__":
    sg.theme("Python")
    config = Settings()
    # TODO: build copy or download feature to take base provided files with the tool
    window = sg.Window(
        "NSK AI Roster Randomizer - Alpha v0.1",
        _build_main_layout(),
        no_titlebar=False,
        finalize=True,
    )

    db_table_options = []
    config_fail = ""

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(module)s [%(levelname)s] %(message)s",
        force=True,
    )
    logger = logging.getLogger()
    logger.info("Main window has been loaded, logger has been instantiated")

    main_window(prev_table=None)
