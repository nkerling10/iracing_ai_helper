"""
Details to come...
"""

## Standard library imports
import json
import logging

## Third party imports

## Local imports


logger = logging.getLogger(__name__)

class Race:
    index = 1

    def __init__(self, race: dict, track_data: dict):
        self.week = Race.index
        self.track = track_data[str(race["trackId"])].get("long_name")
        self.laps = race["race_laps"]
        self.results = True if race.get("results") else False
        Race.index += 1


def _build_season_table(race_objs: list) -> list:
    race_data = []

    for race in race_objs:
        race_data.append([race.week, race.track, race.laps, race.results])

    return race_data


def build_season_display_info(season_path: str) -> list:
    with open("C:/Users/Nick/Documents/iracing_ai_helper/src/assets/references/iracing_tracks.json", "r") as track_file:
        track_data = json.loads(track_file.read())
    with open(season_path, "r") as season_file:
        logger.debug(f"Opening {season_path}")
        race_objs = [
            Race(race, track_data) for race in json.loads(season_file.read()).get("events")
        ]
        logger.debug(f"{len(race_objs)} events loaded")
    return _build_season_table(race_objs)
