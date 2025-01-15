import logging

from gui.layouts.tables import season_data

logger = logging.getLogger()


class LoadSeasonFile:
    def _load_season_file(config, season_settings) -> tuple[list, list]:
        """
        Loads data from a season json file, assembles it into displayable format with custom
        row colors for the next race, completed races, and non-completed races.
        """
        colored_rows = []
        season_rows = season_data.build_season_display_info(
            config.iracing_folder
            / "aiseasons"
            / f"{season_settings.get("season_name")}.json"
        )
        next_race = [next(x[0] - 1 for x in season_rows if x[3] is False)]
        logger.debug(f"Next race is week {next_race[0]+1}")
        done_races = [
            ([x[0] - 1], "white", "green") for x in season_rows if x[3] is True
        ]
        not_done_races = [
            ([x[0] - 1], "white", "red")
            for x in season_rows
            if x[3] is False and x[0] - 1 != next_race
        ]
        for each in not_done_races:
            colored_rows.append(each)
        for each in done_races:
            colored_rows.append(each)
        colored_rows.append((next_race, "white", "orange"))

        return season_rows, colored_rows
