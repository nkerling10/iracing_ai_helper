import json
from gui.helpers.calc_stage_length import _calc_stage_lengths


class RaceData:
    def __init__(self, values):
        self.week = values.get("week")
        self.track = values.get("track_name")
        self.stage_1, self.stage_2 = self._set_stage_lengths(
            values.get("track_short_name"), values.get("race_laps")
        )
        self.race_laps = values.get("race_laps")

    @staticmethod
    def _set_stage_lengths(track_short_name: str, race_length: int) -> tuple[int, int]:
        return _calc_stage_lengths(track_short_name, race_length)


def _convert_race_data(values: dict, db: object) -> dict:
    track_data_raw = db.execute_select_query("TRACK", f"ID is {values.get("track_id")}")
    track_data = track_data_raw[0]
    values["track_name"] = track_data[0]
    values["track_short_name"] = track_data[1]
    del values["track_id"]

    return values


class NextRaceData:
    def _load_next_race_data(
        config: object, season_settings: dict, db: object
    ) -> object:
        with open(
            config.iracing_folder
            / "aiseasons"
            / f"{season_settings.get("season_name")}.json"
        ) as file:
            season_file = json.loads(file.read())
        # loop through events to get first race without results
        try:
            next_race = [
                next(
                    race
                    for race in season_file.get("events")
                    if not race.get("results")
                )
            ][0]
        except IndexError:
            return
        values = {
            "week": season_file["events"].index(next_race) + 1,
            "track_id": next_race.get("trackId"),
            "race_laps": next_race.get("race_laps"),
        }

        values = _convert_race_data(values, db)

        # assign wanted data and return it
        return RaceData(values)
