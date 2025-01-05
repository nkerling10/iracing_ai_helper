## Standard library imports
import logging
import time

## Third party imports

## Local imports


class QualifyingService:
    @classmethod
    def _set_field_size(cls, race_manager) -> None:
        for position in race_manager.ir["SessionInfo"]["Sessions"][
            race_manager.qualifying_session_num
        ]["ResultsPositions"]:
            if position["Position"] == 1:
                race_manager.race_weekend.pole_winner = [
                    driver["UserName"]
                    for driver in race_manager.ir["DriverInfo"]["Drivers"]
                    if driver["CarIdx"] == position["CarIdx"]
                ][0]
                logging.info(
                    f"Congrats to {race_manager.race_weekend.pole_winner} for winning the pole this week."
                )
            if position["Position"] > race_manager.race_settings.field_size:
                match = [
                    driver["CarNumber"]
                    for driver in race_manager.ir["DriverInfo"]["Drivers"]
                    if driver["CarIdx"] == position["CarIdx"]
                    and "NO DRIVER" not in driver["UserName"]
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
