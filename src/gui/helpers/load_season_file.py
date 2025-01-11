import json
import logging
from pathlib import Path
from shutil import copyfile

from gui.functions.season import season_data

logger = logging.getLogger()

def _configure_season_file(config: object, season: dict):
    with open(season.get("season_file"), "r") as file:
        modified_season_file = json.loads(file.read())
    
    # set tires and fuel
    if season.get("series") == "ARCA":
        modified_season_file["carSettings"][0]["max_pct_fuel_fill"] = season.get("fuel_capacity")
        modified_season_file["carSettings"][0]["max_dry_tire_sets"] = -1 if season.get("tire_sets") == "UNLIMITED" else season.get("tire_sets")
    else:
        modified_season_file["carSettings"][0]["max_pct_fuel_fill"] = season.get("fuel_capacity")
        modified_season_file["carSettings"][0]["max_dry_tire_sets"] = -1 if season.get("tire_sets") == "UNLIMITED" else season.get("tire_sets")
        modified_season_file["carSettings"][1]["max_pct_fuel_fill"] = season.get("fuel_capacity")
        modified_season_file["carSettings"][1]["max_dry_tire_sets"] = -1 if season.get("tire_sets") == "UNLIMITED" else season.get("tire_sets")
        modified_season_file["carSettings"][2]["max_pct_fuel_fill"] = season.get("fuel_capacity")
        modified_season_file["carSettings"][2]["max_dry_tire_sets"] = -1 if season.get("tire_sets") == "UNLIMITED" else season.get("tire_sets")

    # set ai roster
    modified_season_file["rosterName"] = season.get("roster_name")
    

def _get_base_season_file(series: str) -> str:
    if series == "CUP":
        return "2025_Cup_Series"
    elif series == "XFINITY":
        return "2025_Xfinity_Series"
    elif series == "TRUCKS":
        return "2025_Truck_Series"
    elif series == "ARCA":
        return "2025_ARCA_Series"

def _season_file_check(config: object, season: dict) -> dict | bool:
    if season.get("season_file") != "OFFICIAL":
        base_file = _get_base_season_file(season.get("season_series"))
        try:
            logger.info(f"Copying official file {base_file}.json")
            copyfile(
                Path(Path.cwd() / "base_files" / "seasons" / f"{base_file}.json"),
                Path(config.iracing_folder / "aiseasons" / f"{season.get("season_name")}.json")
            )
            logger.info("File copied successfully, updating file path in season file")
            try:
                with open(Path.cwd() / "ai_seasons" / f"{season.get("season_name")}.json", "r") as file:
                    season_file = json.loads(file.read())
                    logger.debug("File read successful")
            except Exception as e:
                logger.error(f"Could not read file {Path.cwd() / "ai_seasons" / {season.get("season_name")}}.json")
                return False
            season_file["season_file"] = str(config.iracing_folder / "aiseasons" / f"{season.get("season_name")}.json").replace("\\", "/")
            season["season_file"] = str(config.iracing_folder / "aiseasons" / f"{season.get("season_name")}.json").replace("\\", "/")
            try:
                with open(Path.cwd() / "ai_seasons" / f"{season.get("season_name")}.json", "w") as file:
                    file.write(json.dumps(season_file, indent=4))
                logger.debug("File write successful")
            except Exception as e:
                logger.error(f"Could not write to file {Path.cwd() / "ai_seasons" / {season.get("season_name")}}.json")
                return False
        except Exception as e:
            logger.critical(e)
            return False
    
    # TODO modify the newly copied season to reflect user choices
    #_configure_season_file(config, season)

    return season

class LoadSeasonFile:
    def _load_season_file(config, season) -> tuple[list, list]:
        colored_rows = []
        season_file_update = _season_file_check(config, season)
        if not season_file_update:
            return
        season_rows = season_data.build_season_display_info(season_file_update.get("season_file"))
        next_race = [next(x[0]-1 for x in season_rows if x[3] is False)]
        logger.debug(f"Next race is week {next_race[0]+1}")
        done_races = [([x[0]-1], "white", "green") for x in season_rows if x[3] is True]
        not_done_races = [([x[0]-1], "white", "red") for x in season_rows if x[3] is False and x[0]-1 != next_race]
        for each in not_done_races:
            colored_rows.append(each)
        for each in done_races:
            colored_rows.append(each)
        colored_rows.append((next_race, "white", "orange"))

        return season_rows, colored_rows
