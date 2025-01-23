## Standard library imports
import logging
import time
from operator import itemgetter

## Third party imports

## Local imports

logger = logging.getLogger(__name__)

class QualifyingService:
    @staticmethod
    def _sort_owner_points(race_manager, cars_drivers_left):
        points_sorting = []
        for car_driver in cars_drivers_left:
            try:
                points_rank = [race_manager.season_data.owner_points.index(points_entry) for
                               points_entry in race_manager.season_data.owner_points if
                               car_driver[0] == points_entry[0]][0]
                points_sorting.append([car_driver[0], points_rank])
            except IndexError:
                pass

        return sorted(points_sorting, key=itemgetter(1))

    @classmethod
    def _set_field_size(cls, race_manager) -> None:
        qualifying_results = []
        cars_in_race = []

        qual_results_raw = race_manager.ir["SessionInfo"]["Sessions"][
            race_manager.qualifying_session_num]["ResultsPositions"]

        ## Filter out cars that are not running this week and are already disqualified
        for position in qual_results_raw:
            driver = [driver["UserName"]
                      for driver in race_manager.ir["DriverInfo"]["Drivers"]
                      if driver["CarIdx"] == position["CarIdx"]][0]
            if "NODRIVER" not in driver:
                qualifying_results.append(position)

        ## Store the pole winner
        race_manager.season_data.pole_winner = [driver["UserName"]
                                                 for driver in race_manager.ir["DriverInfo"]["Drivers"]
                                                 if driver["CarIdx"] == qualifying_results[0]["CarIdx"]][0]
        logging.info(
            f"Congrats to {race_manager.season_data.pole_winner} for winning the pole this week."
        )

        ## Example 38 car field = set positions 1-33
        logger.debug(f"Setting positions 1-{race_manager.race_settings.field_size - 5}")
        for position in range(0, race_manager.race_settings.field_size - 5):
            cars_in_race.append([
                    driver["CarNumber"]
                    for driver in race_manager.ir["DriverInfo"]["Drivers"]
                    if driver["CarIdx"] == qualifying_results[position]["CarIdx"]
                ][0])

        # 38 car field = set positions 34-37
        non_locked_in_qual_cars = qualifying_results[race_manager.race_settings.field_size - 5:]
        cars_drivers_left = []
        for position in non_locked_in_qual_cars:
            cars_drivers_left.append([(driver["CarNumber"], driver["UserName"]) for driver in 
                                       race_manager.ir["DriverInfo"]["Drivers"] if driver["CarIdx"]
                                       == position["CarIdx"]][0])
        
        points_sorting_ranked = cls._sort_owner_points(race_manager, cars_drivers_left)

        logger.debug(f"Setting positions {race_manager.race_settings.field_size - 4}-{race_manager.race_settings.field_size - 1}")
        
        if points_sorting_ranked:
            for car in range(0, 3):
                logger.debug(f"{points_sorting_ranked[car][0]} car made the field on owners points provisional")
                cars_in_race.append(points_sorting_ranked[car][0])
                match = [pair for pair in cars_drivers_left if pair[0] == points_sorting_ranked[car][0]][0]
                cars_drivers_left.remove(match)
        else:
            logger.warning("No owner points provisional detected, skipping to winner's provisional")

        ## Check for any past champions
        ## Check for any previous season winners & current season winners
        series_past_champions = []
        last_current_season_winners = []
        for car_driver in cars_drivers_left:
            try:
                driver_info = [driver for driver in race_manager.season_data.drivers_list
                               if driver[0] == car_driver[1]][0]
            # Bypass any driver (such as human) not in the driver table
            except IndexError:
                continue
            if driver_info[7]:
                series_past_champions.append(car_driver)
            elif driver_info[0] in race_manager.season_data.past_season_winners:
                last_current_season_winners.append(car_driver)
            else:
                try:
                    match = [driver for driver in race_manager.season_data.current_season_winners if car_driver[1] == driver[0]][0]
                    last_current_season_winners.append(car_driver)
                except IndexError:
                    continue

        if len(series_past_champions) == 1:
            logger.debug(f"{series_past_champions[0][1]} made the field on past champion provisional")
            cars_in_race.append(series_past_champions[0][0])
            cars_drivers_left.remove(series_past_champions[0])
        elif len(series_past_champions) > 1:
            logger.warning(f"Number of series champions is more than one. Only adding the first found ({series_past_champions[0][1]}) into the list")
            logger.critical("This tie-breaking feature needs to be implemented!")
            cars_in_race.append(series_past_champions[0][0])
            cars_drivers_left.remove(series_past_champions[0])
        # No past champions, check for previous/current season race winners
        else:
            logger.debug("No past champions detected")
            if len(last_current_season_winners) == 1:
                logger.debug(f"{last_current_season_winners[0][1]} made the field on previous/current season winner's provisional")
                cars_in_race.append(last_current_season_winners[0][0])
                cars_drivers_left.remove(last_current_season_winners[0])
            elif len(last_current_season_winners) > 1:
                logger.warning(f"Number of race winners is more than one. Only adding the first found ({last_current_season_winners[0][1]}) into the list")
                logger.critical("This tie-breaking feature needs to be implemented!")
                cars_in_race.append(last_current_season_winners[0][0])
                cars_drivers_left.remove(last_current_season_winners[0])
            # As a last effort, take the next highest in owners points
            else:
                logger.debug("No past winners detected")
                points_sorting_ranked_final = cls._sort_owner_points(race_manager, cars_drivers_left)
                if points_sorting_ranked_final:
                    logger.debug(f"{points_sorting_ranked_final[0][0]} made the final spot on owners points provisional")
                    cars_in_race.append(points_sorting_ranked_final[0][0])
                else:
                    logger.debug("No owner points provisional detected, skipping to speed entries")

        while len(cars_in_race) < race_manager.race_settings.field_size:
            logger.debug(f"{cars_drivers_left[0][1]} has made the race on speed after provisionals were applied")
            cars_in_race.append(cars_drivers_left[0][0])
            cars_drivers_left.remove(cars_drivers_left[0])

        for car in cars_drivers_left:
            logging.info(f"{car[0]} car has missed the race")
            race_manager.send_iracing_command(
                f"!dq {car[0]} #{car[0]} missed the race"
            )

    @classmethod
    def qualifying(cls, race_manager) -> None:
        ## Loop until the qualifying session state is finalized
        while True:
            race_manager.ir.freeze_var_buffer_latest()
            if race_manager.ir["SessionState"] != 6:
                time.sleep(1)
            else:
                break
        logging.info("Session state is finalized, waiting for official results..")
        while True:
            race_manager.ir.freeze_var_buffer_latest()
            if race_manager.ir["SessionInfo"]["Sessions"][race_manager.qualifying_session_num]["ResultsOfficial"] == 1:
                logging.info("Qualifying results are now official.")
                break

        logging.info(
            f"Setting field size to {race_manager.race_settings.field_size} cars"
        )
        cls._set_field_size(race_manager)
