"""
Details to come...
"""

## Standard library imports
import json
import logging
import re
from enum import Enum

## Third party imports

## Local imports


logger = logging.getLogger(__name__)


class Track(Enum):
    Daytona = 191
    Atlanta = 447
    COTA = 231
    Phoenix = 419
    LasVegas = 103
    Homestead = 20
    Martinsville = 33
    Darlington = 115
    Bristol = 101
    Rockingham = 203
    Talladega = 116
    Texas = 357
    Charlotte = 339
    Nashville = 400
    Sebring = 95
    Pocono = 277
    ChicagoStreet = 483
    Sonoma = 48
    Dover = 162
    Indianapolis = 522
    Iowa = 169
    WatkinsGlen = 433
    LagunaSeca = 47
    WWTRaceway = 237
    Kansas = 214
    CharlotteRoval = 350
    NorthWilkesboro = 366


def _convert_track(track_enum: str):
    return re.sub(
        "([A-Z][a-z]+)", r" \1", re.sub("([A-Z]+)", r" \1", track_enum)
    ).split()


def track_name(track_id: int):
    return _convert_track(Track(track_id).name)


class Race:
    index = 1

    def __init__(self, race: dict):
        self.week = Race.index
        self.track = track_name(race["trackId"])
        self.laps = race["race_laps"]
        self.results = True if race.get("results") else False
        Race.index += 1


def _build_season_table(race_objs: list) -> list:
    race_data = []

    for race in race_objs:
        race_data.append([race.week, race.track, race.laps, race.results])

    return race_data


def build_season_display_info(season_path: str) -> list:
    with open(season_path, "r") as season_file:
        logger.debug(f"Opening {season_path}")
        race_objs = [
            Race(race) for race in json.loads(season_file.read()).get("events")
        ]
        logger.debug(f"{len(race_objs)} events loaded")
    return _build_season_table(race_objs)
