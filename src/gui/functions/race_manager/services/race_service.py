## Standard library imports
import logging
import os
import random
import time
from enum import Enum
from pathlib import Path

## Third party imports
import irsdk
import sounddevice as sd
import soundfile as sf

## Local imports

logger = logging.getLogger(__name__)
audio_device = "Speakers (Realtek(R) Audio), MME"


class SessionName(Enum):
    INVALID = 0
    GET_IN_CAR = 1
    WARMUP = 2
    PARADE_LAPS = 3
    RACING = 4
    CHECKERED = 5
    COOLDOWN = 6


def _get_flag(flag):
    """
    Big thanks to `fruzyna` for this function
        source: https://github.com/fruzyna/iracing-apps

    Determines the current flag status of the race.
    """
    if flag & irsdk.Flags.checkered:
        return "checkered"
    else:
        if flag & irsdk.Flags.blue:
            return "blue"
        elif flag & irsdk.Flags.black:
            return "black"
        elif flag & irsdk.Flags.furled:
            return "gray"
        elif flag & irsdk.Flags.red:
            return "red"
        elif flag & irsdk.Flags.white:
            return "white"
        elif (
            flag & irsdk.Flags.yellow
            or flag & irsdk.Flags.yellow_waving
            or flag & irsdk.Flags.caution
            or flag & irsdk.Flags.caution_waving
            or flag & irsdk.Flags.debris
        ):
            return "yellow"
        elif flag & irsdk.Flags.green or flag & irsdk.Flags.green_held:
            return "green"
        elif flag & irsdk.Flags.one_lap_to_green:
            return "one_to_green"
        else:
            return "green"


class RaceService:
    @staticmethod
    def _pit_penalty(race_manager, car_num, lap, current_stage):
        """
        Select and issue a pit penalty to designated car number
        """
        penalty = random.choice(
            race_manager.race_weekend.race_settings.penalties_player
            if car_num == race_manager.race_weekend.player_car_num[0]
            else race_manager.race_weekend.race_settings.penalties
        )

        race_manager.ir.freeze_var_buffer_latest()
        flag_color = _get_flag(race_manager.ir["SessionFlags"])

        if flag_color == "green":
            logging.info(f"PENALTY: Passthrough for #{car_num}: {penalty}")
            race_manager.send_iracing_command(f"!bl {car_num} D")
            penalty_message = f"Passthrough PENALTY #{car_num}: {penalty}"
        elif flag_color == "yellow":
            logging.info(f"PENALTY: EOL for #{car_num}: {penalty}")
            race_manager.send_iracing_command(f"!eol {car_num}")
            penalty_message = f"EOL PENALTY #{car_num}: {penalty}"

        current_stage.pit_penalties.append(
            {"car": car_num, "penalty": penalty, "lap": lap}
        )
        race_manager.send_iracing_command(penalty_message)

    @staticmethod
    def _issue_pre_race_penalty(race_manager):
        """
        Issue a pre-race penalty to each defined car
        """
        for car_num, penalty in race_manager.race_weekend.race_data.pre_race_penalties:
            if penalty in ["Failed Inspection x2", "Unapproved Adjustments"]:
                logging.info(f"#{car_num} to the rear: {penalty}")
                race_manager.send_iracing_command(f"!eol {car_num}")
                penalty_message = f"PENALTY: #{car_num} to the rear: {penalty}"
            elif penalty in ["Failed Inspection x3"]:
                logging.info(f"#{car_num} to the rear plus drivethrough: {penalty}")
                race_manager.send_iracing_command(f"!eol {car_num}")
                race_manager.send_iracing_command(f"!bl {car_num} D")
                penalty_message = f"PENALTY: #{car_num} to the rear plus drivethrough penalty: {penalty}"
            race_manager.send_iracing_command(penalty_message)

    @staticmethod
    def _play_sound():
        """
        Plays packaged sound file of Kevin James' start engine command
        """
        if sd.query_devices(device=audio_device):
            logging.debug(f"Setting audio output to {audio_device}")
            sd.default.device = audio_device
        logging.debug("Trying to play sound file")
        try:
            data, fs = sf.read(
                Path(f"{os.getcwd()}\\src\\assets\\sounds\\start-your-engines.wav"),
                dtype="float32",
            )
            sd.play(data, fs)
            logging.debug("Sound played successfully")
        except Exception as e:
            logging.error(f"{e.__class__.__name__}: {e}")

    @classmethod
    def _pre_race_actions(cls, race_manager):
        """
        Executes pre-race actions to:
            1. Play engine start command
            2. Start the grid/parade laps
            3. Issue calculated pre-race penalties
        """
        ## Play start engine command
        while True:
            race_manager.ir.freeze_var_buffer_latest()
            if race_manager.ir["PlayerTrackSurface"] != -1 or race_manager.observe:
                break
            logging.debug("Waiting for player to enter car")
            time.sleep(1)
        # cls._play_sound()
        # logging.debug("Sleeping for 20 seconds while sound plays")
        time.sleep(10)
        ## Session state right now is 2 (warmup) because of DQ'd AI cars
        logging.debug("Issuing gridstart command")
        ## This will change session state from 2 -> 3
        ## warmup -> parade_laps
        race_manager.send_iracing_command("!gridstart")
        time.sleep(10)
        ## Wait for cars to get rolling, then issue any pre-race penalties
        if len(race_manager.race_weekend.race_data.pre_race_penalties) > 0:
            logging.debug("Issuing pre-race penalties")
            cls._issue_pre_race_penalty(race_manager)
        else:
            logging.debug("No pre-race penalties to issue")
        logging.info("Pre-race actions are complete")
        race_manager.send_iracing_command(
            f"Stage lengths: {race_manager.race_weekend.stage_results[0].stage_end_lap}/{race_manager.race_weekend.stage_results[1].stage_end_lap}/{race_manager.race_weekend.stage_results[2].stage_end_lap}"
        )

    @classmethod
    def _penalty_tracker(cls, race_manager, pit_tracking, current_stage):
        race_manager.ir.freeze_var_buffer_latest()
        ## Quit tracking penalties once the checkered flag comes out
        if race_manager.ir["SessionState"] == 5:
            logger.debug("Sessionstate is now 5")
            return pit_tracking
        try:
            leader_laps_complete = race_manager.ir["SessionInfo"]["Sessions"][
                race_manager.race_session_num
            ]["ResultsPositions"][0]["LapsComplete"]
        except TypeError:
            return pit_tracking
        if (
            leader_laps_complete > 0
            and leader_laps_complete < race_manager.race_weekend.race_length
        ):
            # get all cars currently on pit road
            cars_on_pit_road = [
                driver["CarNumber"]
                for driver in race_manager.ir["DriverInfo"]["Drivers"]
                if race_manager.ir["CarIdxOnPitRoad"][driver["CarIdx"]]
                and driver["UserName"] != "Pace Car"
            ]
            if len(cars_on_pit_road) > 0:
                for car_num in cars_on_pit_road:
                    if car_num not in pit_tracking:
                        logging.info(f"Tracking pitstop for {car_num}")
                        pit_tracking.append(car_num)
                    # if the car has already been processed, skip it
                    else:
                        continue
                for car in pit_tracking:
                    if car not in cars_on_pit_road:
                        logging.debug(f"{car} left pit road, penalty check")
                        # calculate penalty chance once car leaves pit road
                        if (
                            random.randint(1, 100)
                            < race_manager.race_weekend.race_settings.penalty_chance
                        ):
                            caridx = [
                                driver["CarIdx"]
                                for driver in race_manager.ir["DriverInfo"]["Drivers"]
                                if driver["CarNumber"] == car
                            ][0]
                            car_pos = [
                                position["LapsComplete"]
                                for position in race_manager.ir["SessionInfo"][
                                    "Sessions"
                                ][race_manager.race_session_num]["ResultsPositions"]
                                if position["CarIdx"] == caridx
                            ][0]
                            car_on_lap = race_manager.ir["SessionInfo"]["Sessions"][
                                race_manager.race_session_num
                            ]["ResultsPositions"][car_pos]["LapsComplete"]
                            cls._pit_penalty(
                                race_manager, car_num, car_on_lap, current_stage
                            )
                        pit_tracking.remove(car)

        return pit_tracking

    @staticmethod
    def _process_stage_results(race_manager, current_stage):
        race_manager.ir.freeze_var_buffer_latest()
        stage_top_ten_raw = race_manager.ir["SessionInfo"]["Sessions"][
            race_manager.race_session_num
        ]["ResultsPositions"][:10]
        for position in stage_top_ten_raw:
            current_stage.stage_results.append(
                [
                    driver["UserName"]
                    for driver in race_manager.ir["DriverInfo"]["Drivers"]
                    if position["CarIdx"] == driver["CarIdx"]
                ][0]
            )
        logging.info(
            f"{current_stage.stage_results[0]} is the winner of Stage {current_stage.stage}!"
        )
        race_manager.send_iracing_command(
            f"{current_stage.stage_results[0]} is the winner of Stage {current_stage.stage}!"
        )
        logging.info(f"Results: {current_stage.stage_results}")

    @classmethod
    def _stage_logic_tree(cls, race_manager, current_stage):
        race_manager.ir.freeze_var_buffer_latest()
        try:
            leader_laps_complete = race_manager.ir["SessionInfo"]["Sessions"][
                race_manager.race_session_num
            ]["ResultsPositions"][0]["LapsComplete"]
        except Exception as e:
            # logger.error(f"{type(e).__name__}: {e}")
            return

        current_flag = _get_flag(race_manager.ir["SessionFlags"])
        if (
            current_flag == "yellow"
            and leader_laps_complete <= current_stage.stage_end_lap - 3
            and current_stage.stage_ending_early is False
        ):
            logger.warning("Early caution feature is not yet implemented")
            # race_manager.send_iracing_command(f"Stage {current_stage.stage} will end early under caution")
            # current_stage.stage_ending_early = True

        if not current_stage.stage_ending_early:
            ## when leader reaches 2 laps before end of stage, close the pits
            if (
                leader_laps_complete == current_stage.stage_end_lap - 2
                and current_stage.stage_ending_early is False
                and current_stage.pits_are_closed is False
            ):
                logging.info("Closing pits - 2 laps to go in stage")
                race_manager.send_iracing_command("!pitclose")
                current_stage.pits_are_closed = True

            ## Announce when there is 1 lap left in the stage
            elif (
                leader_laps_complete == current_stage.stage_end_lap - 1
                and current_stage.stage_ending_early is False
                and current_stage.last_lap_notice is False
            ):
                logging.info(f"Final lap of stage {current_stage.stage}")
                race_manager.send_iracing_command(
                    f"Final lap of stage {current_stage.stage}"
                )
                current_stage.last_lap_notice = True

            ## When the current lap equals the stage end
            elif (
                leader_laps_complete == current_stage.stage_end_lap
                and current_stage.stage_complete is False
            ):
                ## Throw the caution once the leader crosses the line because it's not possible to re-order cars
                ## if they pass each other after crossing the line at end of stage
                logging.info("Stage end has been reached")
                ## Throw the caution flag if necessary
                if (
                    race_manager.race_weekend.race_settings.stage_cautions
                    and _get_flag(race_manager.ir["SessionFlags"]) == "green"
                ):
                    race_manager.send_iracing_command(
                        f"!yellow End of Stage {current_stage.stage}"
                    )

                cls._process_stage_results(race_manager, current_stage)
                current_stage.stage_complete = True

            elif current_stage.stage_complete is True:
                if _get_flag(race_manager.ir["SessionFlags"]) == "yellow":
                    pass
                elif _get_flag(race_manager.ir["SessionFlags"]) == "green":
                    logger.debug("Advancing to next stage")
                    current_stage.advance_to_next_stage = True

    @classmethod
    def _process_race(cls, race_manager):
        logging.info("Race has started!")
        for current_stage in race_manager.race_weekend.stage_results:
            logging.info(f"Starting to process stage {current_stage.stage}")
            race_manager.send_iracing_command(
                f"Stage {current_stage.stage} end: lap {current_stage.stage_end_lap}"
            )
            pit_tracking = []
            while True:
                pit_tracking = cls._penalty_tracker(
                    race_manager, pit_tracking, current_stage
                )
                # stages 1 and 2 run through stage logic processing
                # stage 3 only needs penalty tracker
                if current_stage.stage in [1, 2]:
                    cls._stage_logic_tree(race_manager, current_stage)
                    if current_stage.advance_to_next_stage:
                        break
                if race_manager.ir["SessionState"] == 5:
                    break
            logging.info(f"Handling of stage {current_stage.stage} is complete")
        logging.info("Race processing is complete!")

    @classmethod
    def race(cls, race_manager):
        while True:
            race_manager.ir.freeze_var_buffer_latest()
            ## Session state GET_IN_CAR
            if race_manager.ir["SessionState"] == 1:
                logging.debug("Sessionstate 1 detected")
                cls._pre_race_actions(race_manager)
            ## Session state RACING
            elif race_manager.ir["SessionState"] == 4:
                logging.debug("Race has started!")
                cls._process_race(race_manager)
            ## Session state COOLDOWN
            elif race_manager.ir["SessionState"] == 6:
                logger.debug("SessionState is now 6, dumping results data")
                race_manager.ir.freeze_var_buffer_latest()
                irsdk.IRSDK.parse_to(
                    race_manager.ir,
                    to_file="C:/Users/Nick/Documents/iracing_ai_helper/session_data/race_logic_complete.bin",
                )
                race_manager.race_weekend.stage_results[2].stage_results = (
                    race_manager.ir["SessionInfo"]["Sessions"][
                        race_manager.race_session_num
                    ]["ResultsPositions"]
                )
                return
