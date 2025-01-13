import math

def _calc_stage_lengths(track_short_name: str, race_length: int) -> tuple[int, int]:
    if track_short_name in ["Daytona", "Atlanta", "Watkins Glen"]:
        stage_1_mod = 0.25
    elif track_short_name == "COTA":
        stage_1_mod = 0.31
    elif track_short_name in [
        "Phoenix",
        "Las Vegas",
        "Homestead",
        "Texas",
        "Charlotte",
        "Dover",
        "Kansas",
    ]:
        stage_1_mod = 0.225
    elif track_short_name in [
        "Martinsville",
        "Nashville",
        "Sebring",
        "Rockingham",
    ]:
        stage_1_mod = 0.24
    elif track_short_name == "Darlington":
        stage_1_mod = 0.307
    elif track_short_name == "Bristol":
        stage_1_mod = 0.285
    elif track_short_name in ["Talladega", "Pocono"]:
        stage_1_mod = 0.23
    elif track_short_name == "Sonoma":
        stage_1_mod = 0.26
    elif track_short_name in [
        "Indianapolis",
        "Iowa",
        "Charlotte Roval",
        "Chicago",
    ]:
        stage_1_mod = 0.30
    elif track_short_name == "Laguna Seca":
        stage_1_mod = 0.34
    elif track_short_name == "WWT":
        stage_1_mod = 0.22
    
    stage_1_end_lap = math.floor(race_length * stage_1_mod)

    return stage_1_end_lap, math.floor(
        stage_1_end_lap * 2.15 if track_short_name == "COTA" else stage_1_end_lap * 2
    )