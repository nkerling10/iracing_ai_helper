import logging
import PySimpleGUI as sg
import sys
from pathlib import Path

sys.path.append(f"{str(Path.cwd())}\\src")

from gui.main_menu.season.season_info.next_race_tab import NextRaceTabLayout
from gui.main_menu.season.season_info.standings_tab import StandingsTabLayout
from gui.main_menu.season.season_info.roster_tab import RosterTabLayout
from gui.main_menu.season.season_info.roster_data_table import build_driver_display_info
from gui.main_menu.season.season_info.schedule_tab import ScheduleTabLayout
from gui.main_menu.season.season_info.schedule_data_table import build_season_display_info
from functions.randomizer import Randomizer


example_season_data = {'season_name': 'xfinity4', 'player_team_name': 'cac', 'season_series': 'XFINITY', 'iracing_roster_file': 'C:/Users/Nick/Documents/iRacing/airosters/xfinity4', 'iracing_season_file': 'C:/Users/Nick/Documents/iRacing/aiseasons//xfinity4.json', 'user_settings': {'stages_enabled': True, 'field_size': 38, 'race_distance_percent': 100, 'fuel_capacity': 100, 'tire_sets': 'UNLIMITED', 'pre_race_penalties': {'enabled': True, 'chance': 2, 'inspection_fail_chance_modifier': 2}, 'pit_penalties': {'enabled': True, 'chance': 8}, 'post_race_penalties': {'enabled': True, 'chance': 2}, 'debris_cautions': {'enabled': True, 'chance': 1}}}

logger = logging.getLogger(__name__)

def _block_focus(window) -> None:
    """
    Function to block focus on main_window when the create season dialog appears
    """
    for key in window.key_dict:  # Remove dash box of all Buttons
        element = window[key]
        if isinstance(element, sg.Button):
            element.block_focus()


def _get_season_length(season_data):
    return build_season_display_info(season_data.get("iracing_season_file"))


def _season_info_layout(season_data: dict) -> list[list]:
    active_driver_data, inactive_driver_data = build_driver_display_info(season_data.get("iracing_roster_file"))
    race_data = _get_season_length(season_data)

    return [
        [
            sg.TabGroup(
                [
                    [
                        sg.Tab(
                            "Next Race",
                            layout=NextRaceTabLayout.build_next_race_tab_layout(),
                            expand_x=True,
                            expand_y=True,
                        ),
                        sg.Tab(
                            "Standings",
                            layout=StandingsTabLayout.build_standings_tab_layout(),
                            expand_x=True,
                            expand_y=True,
                        ),
                        sg.Tab(
                            "Roster",
                            layout=RosterTabLayout.build_roster_tab_layout(active_driver_data, inactive_driver_data),
                            expand_x=True,
                            expand_y=True,
                        ),
                        sg.Tab(
                            "Schedule",
                            layout=ScheduleTabLayout.build_schedule_tab_layout(race_data),
                            expand_x=True,
                            expand_y=True,
                        ),
                    ]
                ],
                key="-SEASONTABS-",
                tab_location="topleft",
                expand_x=True,
                expand_y=True,
            )
        ]
    ]


def season_window(season_data: dict):
    window = sg.Window(
        f"Loaded season: {season_data.get("season_name")}",
        _season_info_layout(season_data),
        no_titlebar=False,
        finalize=True,
        size=(1000,650),
        keep_on_top=True
    )
    window["-TRACKBOX-"].update(
        values=RosterTabLayout._roster_file_track_choices(len(_get_season_length(season_data)))
    )
    
    _block_focus(window)
    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, "Cancel"):
            window.close()
            return
        if event == "Randomize":
            Randomizer(season_data, week=1)
            active_driver_data, inactive_driver_data = build_driver_display_info(
                season_data.get("iracing_roster_file")
            )
            window["-ACTIVEDRIVERS-"].update(values=active_driver_data)
            window["-INACTIVEDRIVERS-"].update(values=inactive_driver_data)
        if event == "-SCHEDULETABLE-":
            window["-TRACKBOX-"].update(value=values["-SCHEDULETABLE-"][0] + 1)


if __name__ == "__main__":
    season_window(example_season_data)
