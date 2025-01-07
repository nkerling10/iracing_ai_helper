## Standard library imports
import logging
import random

## Third party imports

## Local imports


class PracticeService:
    @classmethod
    def _disable_chat(cls, race_manager, driver_data, global_=False) -> None:
        """
        Disable chat so AI drivers won't type when they are
            supposedly pitting.
        TODO: Currently disabling their chat 1 by 1 will not
            prevent them from using chat.
        """
        if global_ is True:
            race_manager.send_iracing_command("!nchat")
        else:
            for driver in driver_data:
                if driver["CarIsAI"] == 1:
                    race_manager.send_iracing_command(
                        f"!nchat {driver['UserName'].replace(' ', '.')}"
                    )

    @classmethod
    def _disqualify_drivers(cls, race_manager, driver_data) -> None:
        """
        Disqualify driverless cars in the session, they will
            be denoted by their name: NODRIVER{carnumber}.
        """
        logging.debug(f"{len(driver_data)} total cars in event")
        dq_drivers = [
            driver["CarNumber"]
            for driver in driver_data
            if "NODRIVER" in driver["UserName"]
        ]
        for number in dq_drivers:
            logging.info(f"Disqualifying car {number} for NODRIVER name")
            race_manager.send_iracing_command(f"!dq {number} Car unused this week.")

    @classmethod
    def _calculate_pre_race_penalties(cls, race_manager, driver_data) -> None:
        """
        Calculate pre-race penalties for each driver in the field based
            off the chance modifier in the race_settings class.
        """
        for driver in driver_data:
            if (
                random.randint(1, 100)
                < race_manager.race_settings.pre_race_penalty_chance
            ):
                penalty = random.choice(race_manager.race_settings.pre_race_penalties)
                logging.debug(f"{driver['CarNumber']} hit with penalty: {penalty}")
                race_manager.race_weekend.pre_race_penalties.append(
                    [driver["CarNumber"], penalty]
                )

    @classmethod
    def practice(cls, race_manager, disable=False) -> None:
        """
        1. Disable chat for AI drivers (optional)
        2. Disqualify all drivers who are named NODRIVER{car_num}
        3. Calculate any pre-race penalties
        """
        driver_data = [
            driver
            for driver in race_manager.ir["DriverInfo"]["Drivers"]
            if driver["CarIsPaceCar"] == 0
        ]
        if disable is True:
            logging.info("Disabling chat")
            cls._disable_chat(race_manager, driver_data, global_=False)
        logging.info("Disqualifying driverless cars")
        cls._disqualify_drivers(race_manager, driver_data)
        logging.info("Issuing pre-race penalties")
        cls._calculate_pre_race_penalties(race_manager, driver_data)
