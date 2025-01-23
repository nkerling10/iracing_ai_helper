## Standard library imports
import logging
import random

## Third party imports

## Local imports

logger = logging.getLogger(__name__)


class PracticeService:
    @staticmethod
    def _disable_chat(race_manager, global_=False) -> None:
        """
        Disable chat so AI drivers won't type when they are
            supposedly pitting.
        BUG: Currently disabling their chat 1 by 1 will not
            prevent them from using chat.
        """
        if global_ is True:
            race_manager.send_iracing_command("!nchat")
        else:
            for driver in race_manager.ir["DriverInfo"]["Drivers"]:
                if driver["CarIsAI"] == 1:
                    race_manager.send_iracing_command(
                        f"!nchat {driver['UserName'].replace(' ', '.')}"
                    )

    @staticmethod
    def _disqualify_drivers(race_manager, cars_to_dq) -> None:
        """
        Disqualify driverless cars in the session, they will
            be denoted by their name: NODRIVER{carnumber}.
        """
        for number in cars_to_dq:
            logging.info(f"Disqualifying NODRIVER{number}")
            race_manager.send_iracing_command(f"!dq {number} Car unused this week.")

    @staticmethod
    def _calculate_pre_race_penalties(race_manager) -> None:
        """
        Calculate pre-race penalties for each driver in the field based
            off the chance modifier in the race_settings subclass.
        """
        for driver in race_manager.race_weekend.drivers:
            failed_one = False
            failed_two = False

            if (
                random.randint(1, 100)
                < race_manager.race_settings.inspection_fail_chance_one
            ):
                logger.debug(f"Car #{driver.car} has failed inspection once")
                failed_one = True
            else:
                if (
                    random.randint(1, 100)
                    == race_manager.race_settings.unapproved_adjustments_chance
                ):
                    logger.debug(
                        f"Car #{driver.car} is penalized for unapproved adjustments"
                    )
                    race_manager.race_weekend.race_data.pre_race_penalties.append(
                        [driver.car, "Unapproved Adjustments"]
                    )
                else:
                    continue

            if failed_one:
                if (
                    random.randint(1, 100)
                    < race_manager.race_settings.inspection_fail_chance_two
                ):
                    logger.debug(f"Car #{driver.car} has failed inspection twice")
                    failed_two = True
                else:
                    continue

            if failed_two:
                if (
                    random.randint(1, 100)
                    < race_manager.race_settings.inspection_fail_chance_three
                ):
                    logger.debug(f"Car #{driver.car} has failed inspection three times")
                    race_manager.race_weekend.race_data.pre_race_penalties.append(
                        [driver.car, "Failed Inspection x3"]
                    )
                else:
                    race_manager.race_weekend.race_data.pre_race_penalties.append(
                        [driver.car, "Failed Inspection x2"]
                    )

    @classmethod
    def practice(cls, race_manager, cars_to_dq, disable=False) -> None:
        """
        1. Disable chat for AI drivers (optional)
        2. Disqualify all drivers who are named NODRIVER{car_num}
        3. Generate any pre-race penalties
        """
        if disable is True:
            logging.info("Disabling chat")
            cls._disable_chat(race_manager, global_=False)
        logging.info("Disqualifying driverless cars")
        cls._disqualify_drivers(race_manager, cars_to_dq)
        logging.info("Issuing pre-race penalties")
        cls._calculate_pre_race_penalties(race_manager)
