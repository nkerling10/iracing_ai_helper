import re
from enum import Enum
import logging

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


def _convert_track(track_enum: str):
    return re.sub(
        "([A-Z][a-z]+)", r" \1", re.sub("([A-Z]+)", r" \1", track_enum)
    ).split()


def track_name(track_id: int):
    return _convert_track(Track(track_id).name)
