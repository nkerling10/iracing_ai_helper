import json
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
from functions.race_manager.race_manager import start_race_manager
from assets.misc.data_converter import convert_car_driver_mapping, convert_drivers


example_season_data = {'season_name': 'xfinity4', 'player_team_name': 'cac', 'season_series': 'XFINITY', 'iracing_roster_file': 'C:/Users/Nick/Documents/iRacing/airosters/xfinity4', 'iracing_season_file': 'C:/Users/Nick/Documents/iRacing/aiseasons/xfinity4.json', 'user_settings': {'stages_enabled': True, 'field_size': 38, 'race_distance_percent': 100, 'fuel_capacity': 100, 'tire_sets': 'UNLIMITED', 'pre_race_penalties': {'enabled': True, 'chance': 2, 'inspection_fail_chance_modifier': 2}, 'pit_penalties': {'enabled': True, 'chance': 8}, 'post_race_penalties': {'enabled': True, 'chance': 2}, 'debris_cautions': {'enabled': True, 'chance': 1}}}

logger = logging.getLogger(__name__)

def _block_focus(window) -> None:
    """
    Function to block focus on main_window when the create season dialog appears
    """
    for key in window.key_dict:  # Remove dash box of all Buttons
        element = window[key]
        if isinstance(element, sg.Button):
            element.block_focus()

def _get_real_schedule_stages(week, season_data):
    with open(Path.cwd() / "src" / "data" / f"2025_{season_data.get("season_series").lower()}_schedule.json", "r") as stage_file:
        all_race_stages = json.loads(stage_file.read())
    race_stage_lengths = all_race_stages[str(week)].get("stages")
    if season_data.get("user_settings").get("race_distance_percent") != 100:
        for stage in race_stage_lengths:
            stage = round(stage * season_data.get("user_settings").get("race_distance_percent") / 100)

    return race_stage_lengths

def _get_custom_schedule_stages(season_data, week, track):
    with open(season_data.get("iracing_season_file"), "r") as season_file:
        iracing_season = json.loads(season_file.read())

    race_week_entry = iracing_season.get("events")[week]
    track_id = race_week_entry.get("trackId")
    race_laps = race_week_entry.get("race_laps", iracing_season.get("race_laps"))

    # Homestead, Vegas, Nashville, Texas, Dover, Charlotte, Kansas, Phoenix
    if track_id in [20, 103, 400, 357, 162, 339, 214, 419]:
        stage_1 = round(race_laps * .225)
    # Iowa, Rockingham, Martinsville
    elif track_id in [169, 203, 33]:
        stage_1 = round(race_laps * .24)
    # Daytona
    elif track_id in [191]:
        stage_1 = round(race_laps * .275)
    else:
        stage_1 = round(race_laps * .235)

    race_stage_lengths = [stage_1, stage_1 * 2, race_laps]

    return race_stage_lengths

def _get_season_length(season_data):
    return build_season_display_info(season_data.get("iracing_season_file"))


def _season_info_layout(season_data: dict, schedule_data: list) -> list[list]:
    active_driver_data, inactive_driver_data = build_driver_display_info(season_data.get("iracing_roster_file"))

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
                            layout=ScheduleTabLayout.build_schedule_tab_layout(schedule_data),
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
    schedule_data = _get_season_length(season_data)
    car_driver_map = convert_car_driver_mapping(season_data.get("season_series"))
    driver_data = convert_drivers(season_data.get("season_series"))
    window = sg.Window(
        f"Loaded season: {season_data.get("season_name")}",
        _season_info_layout(season_data, schedule_data),
        no_titlebar=False,
        finalize=True,
        #size=(1000,600),
        keep_on_top=True
    )
    next_race = next((x for x in schedule_data if x[3] is False), None)
    race_week = schedule_data.index(next_race)+1
    if season_data.get("season_custom"):
        race_stage_lengths = _get_custom_schedule_stages(season_data, schedule_data.index(next_race), next_race[1])
    else:
        race_stage_lengths = _get_real_schedule_stages(race_week, season_data)
    window["-TRACKBOX-"].update(value=race_week,
        values=RosterTabLayout._roster_file_track_choices(len(schedule_data))
    )
    window["_-WEEK-_"].update(value=race_week)
    window["_-TRACK-_"].update(value=next_race[1])
    if season_data.get("user_settings").get("stages_enabled"):
        window["_-STAGE1-_"].update(value=race_stage_lengths[0])
        window["_-STAGE2-_"].update(value=race_stage_lengths[1])
    window["_-STAGE3-_"].update(value=race_stage_lengths[2])
    _block_focus(window)
    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, "Cancel"):
            window.close()
            return
        if event == "Randomize":
            Randomizer(season_data, week=window["-TRACKBOX-"].get())
            active_driver_data, inactive_driver_data = build_driver_display_info(
                season_data.get("iracing_roster_file")
            )
            window["-ACTIVEDRIVERS-"].update(values=active_driver_data)
            window["-INACTIVEDRIVERS-"].update(values=inactive_driver_data)
        if event == "-SCHEDULETABLE-":
            window["-TRACKBOX-"].update(value=values["-SCHEDULETABLE-"][0] + 1)
        if event == "-STARTRACEBUTTON-":
            randomize_check = sg.PopupYesNo("Randomize?", keep_on_top=True)
            if randomize_check == "Yes":
                Randomizer(season_data, week=window["-TRACKBOX-"].get())
                active_driver_data, inactive_driver_data = build_driver_display_info(
                    season_data.get("iracing_roster_file")
                )
                window["-ACTIVEDRIVERS-"].update(values=active_driver_data)
                window["-INACTIVEDRIVERS-"].update(values=inactive_driver_data)
            start_race_manager(car_driver_map, driver_data, season_data, race_stage_lengths, True)


if __name__ == "__main__":
    season_window(example_season_data)
