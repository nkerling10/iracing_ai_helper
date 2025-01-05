"""
Details to come...
"""

## Standard library imports
import json
import logging

## Third party imports

## Local imports
from functions.season.track_ids import Track

logger = logging.getLogger(__name__)


class Race:
    index = 1

    def __init__(self, race: dict):
        self.week = Race.index
        self.track = Track(race["trackId"]).name
        self.laps = race["race_laps"]
        self.results = True if race.get("results") else False
        Race.index += 1


def _build_season_table(race_objs: list) -> list:
    race_data = []

    for race in race_objs:
        race_data.append([
            race.week,
            race.track,
            race.laps,
            race.results
        ])

    return race_data

def build_season_display_info(season_path: str) -> list:
    with open(season_path, "r") as season_file:
        race_objs = [
            Race(race) for race in json.loads(season_file.read()).get("events")
        ]
    return _build_season_table(race_objs)
