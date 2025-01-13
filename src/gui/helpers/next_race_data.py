import json

class RaceData:
    def __init__(self, values):
        self.week = values.get("week")
        self.track = values.get("track_name")
        self.stage_1 = int(values.get("race_laps") / 4)
        self.stage_2 = int(values.get("race_laps") / 2)
        self.race_laps = values.get("race_laps")


def _convert_race_data(values: dict, db: object) -> dict:
    track_data = db.execute_select_query("TRACK", f"ID = {values.get("track_id")}")[0]
    values["track_name"] = track_data[0]
    del values["track_id"]

    return values

class NextRaceData:
    def _load_next_race_data(config: object, season_settings: dict, db: object) -> object:
        with open(config.iracing_folder / "aiseasons" / f"{season_settings.get("season_name")}.json") as file:
            season_file = json.loads(file.read())
        # loop through events to get first race without results
        try:
            next_race = [next(race for race in season_file.get("events") if not race.get("results"))][0]
        except IndexError:
             return
        values = {
            "week": season_file["events"].index(next_race)+1,
            "track_id": next_race.get("trackId"),
            "race_laps": next_race.get("race_laps")
        }

        values = _convert_race_data(values, db)

        # assign wanted data and return it
        return RaceData(values)