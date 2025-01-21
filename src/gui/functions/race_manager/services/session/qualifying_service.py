## Standard library imports
import logging
import time

## Third party imports

## Local imports

logger = logging.getLogger(__name__)

class QualifyingService:
    @staticmethod
    def _set_field_size(race_manager) -> None:
        qualifying_results = []
        cars_in_race = []
        cars_to_dq = []

        qual_results_raw = race_manager.ir["SessionInfo"]["Sessions"][
            race_manager.qualifying_session_num]["ResultsPositions"]

        ## Filter out cars that are not running this week and are already disqualified
        for position in qual_results_raw:
            driver = [driver["UserName"]
                      for driver in race_manager.ir["DriverInfo"]["Drivers"]
                      if driver["CarIdx"] == position["CarIdx"]][0]
            if "NODRIVER" not in driver:
                qualifying_results.append(position)

        race_manager.race_weekend.pole_winner = [driver["UserName"]
                                                 for driver in race_manager.ir["DriverInfo"]["Drivers"]
                                                 if driver["CarIdx"] == qualifying_results[0]["CarIdx"]][0]
        logging.info(
            f"Congrats to {race_manager.race_weekend.pole_winner} for winning the pole this week."
        )

        ## Example 38 car field = set 1-33
        for position in range(1, race_manager.race_settings.field_size - 5):
            cars_in_race.append([
                    driver["CarNumber"]
                    for driver in race_manager.ir["DriverInfo"]["Drivers"]
                    if driver["CarIdx"] == qualifying_results[position]["CarIdx"]
                ][0])
            logger.debug(f"{[
                    driver["UserName"], driver["CarNumber"]
                    for driver in race_manager.ir["DriverInfo"]["Drivers"]
                    if driver["CarIdx"] == position["CarIdx"]][0]} is locked in")

        # 38 car field = set 34-37
        non_locked_in_qual_cars = qualifying_results[race_manager.race_settings.field_size - 4:]
        cars_drivers_left = []
        for position in non_locked_in_qual_cars:
            cars_drivers_left.append([(driver["CarNumber"], driver["Username"]) for driver in 
                                       race_manager.ir["DriverInfo"]["Drivers"] if driver["CarIdx"]
                                       == position["CarIdx"]][0])
        
        for car_driver in cars_drivers_left:
            car_num = car_driver[0]
            driver = car_driver[1]



        ## final car in the field
        # 1. past series champion
        # 2. race winner from the previous or current season
        # 3. fifth owner points provisional

        for car in cars_to_dq:
            match = [
                driver["CarNumber"]
                for driver in race_manager.ir["DriverInfo"]["Drivers"]
                if driver["CarNumber"] == car
                and "NODRIVER" not in driver["UserName"]
            ]
            if match:
                logging.info(f"{match[0]} car missed the race")
                race_manager.send_iracing_command(
                    f"!dq {match[0]} #{match[0]} missed the race"
                )

    @classmethod
    def qualifying(cls, race_manager) -> None:
        ## Loop until the qualifying session state is finalized
        while True:
            race_manager.ir.freeze_var_buffer_latest()
            if race_manager.ir["SessionState"] != 6:
                logging.debug("Session state is not finalized..")
                time.sleep(1)
            else:
                break

        while True:
            logging.info("Session state is finalized, waiting for official results..")
            race_manager.ir.freeze_var_buffer_latest()
            if (
                race_manager.ir["SessionInfo"]["Sessions"][
                    race_manager.qualifying_session_num
                ]["ResultsOfficial"]
                != 1
            ):
                logging.debug("Waiting for results to become official..")
                time.sleep(1)
            else:
                logging.info("Qualifying results are now official.")
                break

        logging.info(
            f"Setting field size to {race_manager.race_settings.field_size} cars"
        )
        cls._set_field_size(race_manager)
