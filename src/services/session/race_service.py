## Standard library imports
import logging
import os
import random
import threading
import time
from pathlib import Path
from enum import Enum

## Third party imports
import irsdk
import sounddevice as sd
import soundfile as sf

## Local imports

audio_device = "Speakers (Realtek(R) Audio), MME"


class CustomException(Exception):
    pass


class SessionName(Enum):
    INVALID = 0
    GET_IN_CAR = 1
    WARMUP = 2
    PARADE_LAPS = 3
    RACING = 4
    CHECKERED = 5
    COOLDOWN = 6


class RaceService:
    @staticmethod
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

    @classmethod
    def _pit_penalty(cls, race_manager, car_num, stage):
        """
        Select and issue a pit penalty to designated car number
        """
        penalty = random.choice(
            race_manager.race_settings.penalties_player
            if car_num == race_manager.race_weekend.player_car_num
            else race_manager.race_settings.penalties
        )

        race_manager.ir.freeze_var_buffer_latest()
        flag_color = cls._get_flag(race_manager.ir["SessionFlags"])

        if flag_color == "green":
            logging.info(f"PENALTY: Passthrough for #{car_num}: {penalty}")
            race_manager.send_iracing_command(f"!bl {car_num} D")
            penalty_message = f"Passthrough PENALTY #{car_num}: {penalty}"
        elif flag_color == "yellow":
            logging.info(f"PENALTY: EOL for #{car_num}: {penalty}")
            race_manager.send_iracing_command(f"!eol {car_num}")
            penalty_message = f"EOL PENALTY #{car_num}: {penalty}"

        record = {"car": car_num, "penalty": penalty}
        if stage == 1:
            race_manager.race_weekend.stage_1.pit_penalties.append(record)
        elif stage == 2:
            race_manager.race_weekend.stage_2.pit_penalties.append(record)
        elif stage == 3:
            race_manager.race_weekend.stage_3.pit_penalties.append(record)

        race_manager.send_iracing_command(penalty_message)

    @staticmethod
    def _issue_pre_race_penalty(race_manager):
        """
        Issue a pre-race penalty to each defined car
        """
        for car_num, penalty in race_manager.race_weekend.pre_race_penalties:
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
        Plays packaged sound file of start engine command
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
            if race_manager.ir["PlayerTrackSurface"] != -1:
                break
            logging.debug("Waiting for player to enter car")
        cls._play_sound()
        logging.debug("Sleeping for 30 seconds while sound plays")
        time.sleep(30)
        ## This will change session state from 1 -> 3
        ## get_in_car -> parade_laps
        logging.debug("Issuing gridstart command")
        race_manager.send_iracing_command("!gridstart")
        time.sleep(10)
        ## Wait for cars to get rolling, then issue any pre-race penalties
        if len(race_manager.race_weekend.pre_race_penalties) > 0:
            logging.debug("Issuing pre-race penalties")
            cls._issue_pre_race_penalty(race_manager)
        else:
            logging.debug("No pre-race penalties to issue")
        logging.info("Pre-race actions are complete")
        logging.debug(f"Stage lengths: {race_manager.race_weekend.stage_1.stage_end_lap}/{race_manager.race_weekend.stage_2.stage_end_lap}/{race_manager.race_weekend.stage_3.stage_end_lap}")
        race_manager.send_iracing_command(f"Stage lengths: {race_manager.race_weekend.stage_1.stage_end_lap}/{race_manager.race_weekend.stage_2.stage_end_lap}/{race_manager.race_weekend.stage_3.stage_end_lap}")

    @classmethod
    def _penalty_tracker(cls, race_manager, stage):
        logging.debug(f"Starting penalty tracker for stage {stage}")
        pit_tracking = []
        while True:
            if race_manager.ir["Lap"] > 0:
                logging.debug(f"Lap {race_manager.ir['Lap']} (penalty_tracker)")
                race_manager.ir.freeze_var_buffer_latest()
                # get all cars currently on pit road
                cars_on_pit_road = [
                    driver["CarNumber"]
                    for driver in race_manager.ir["DriverInfo"]["Drivers"]
                    if race_manager.ir["CarIdxOnPitRoad"][driver["CarIdx"]]
                    and driver["UserName"] != "Pace Car"
                ]
                # if there is at least 1 car on pit road
                if len(cars_on_pit_road) > 0:
                    # for each car in this pulled instance
                    for car_num in cars_on_pit_road:
                        # if the car has not been processed this cycle
                        if car_num not in pit_tracking:
                            # track the car number
                            logging.info(f"Tracking pitstop for {car_num}")
                            pit_tracking.append(car_num)
                        # if the car has already been processed, skip it
                        else:
                            continue
                    # track for when a car leaves pit road
                    for car in pit_tracking:
                        if car not in cars_on_pit_road:
                            logging.info(f"{car} left pit road, penalty check")
                            # calculate penalty chance once car leaves pit road
                            if random.randint(1, 100) < race_manager.race_settings.penalty_chance:
                                cls._pit_penalty(race_manager, car_num, stage)
                            pit_tracking.remove(car)
                else:
                    logging.debug("No cars on pitroad")
                    time.sleep(1)

    @classmethod
    def _process_stage(cls, race_manager, stage):
        if stage == 1:
            stage_end = race_manager.race_weekend.stage_1.stage_end_lap
        elif stage == 2:
            stage_end = race_manager.race_weekend.stage_2.stage_end_lap
        elif stage == 3:
            stage_end = race_manager.race_weekend.stage_3.stage_end_lap
        
        logging.debug(
            f"Stage {stage} started - ends on lap {stage_end}"
        )

        pits_closed = False
        last_lap_notice = False
        stage_end_early = False
        stage_complete = False

        while True:
            race_manager.ir.freeze_var_buffer_latest()
            logging.debug(f"Lap {race_manager.ir['Lap']} (process_stage)")
            current_flag = cls._get_flag(race_manager.ir["SessionFlags"])

            ## TODO: If the caution is out within 3 laps of stage end
            ## the stage will end early
            if current_flag == "yellow" and race_manager.ir["Lap"] <= stage_end - 3:
                logging.debug(f"Stage needs to end early: \
                              {stage_end - race_manager.ir['Lap']} laps until stage end")
                race_manager.send_iracing_command(f"Stage {stage} will end early under caution")
                stage_end_early = True
                break

            ## Close the pits with 2 laps to go in the stage
            if race_manager.ir["Lap"] == stage_end - 2 and stage_end_early is False and pits_closed is False:
                logging.debug("Closing pits - 2 laps to go in stage")
                race_manager.send_iracing_command("!pitclose")
                pits_closed = True
            ## Announce when there is 1 lap left in the stage
            elif race_manager.ir["Lap"] == stage_end - 1 and stage_end_early is False and last_lap_notice is False:
                logging.debug(f"1 lap to go in stage {stage}")
                race_manager.send_iracing_command(f"1 lap to go in Stage {stage}")
                last_lap_notice = True
            ## When the current lap equals the stage end
            elif race_manager.ir["Lap"] == stage_end:
                logging.info("Stage end has been reached")
                break
            else:
                time.sleep(1)

        while stage_complete is False:
            race_manager.ir.freeze_var_buffer_latest()
            if stage_end_early is True:
                ## determine how many caution laps should be added
                ## wait until the stage lap actually comes
                logging.warning("Early caution feature needs to be implemented")
                stage_complete = True
            else:
                ## Wait until 10th place crosses the finish line
                positions = race_manager.ir["SessionInfo"]["Sessions"] \
                            [race_manager.race_session_num]["ResultsPositions"]
                if positions[10]["LapsComplete"] != stage_end:
                    logging.debug(f"Waiting for 10th place to cross the line")
                else:
                    stage_complete = True

        ## Throw the caution flag if necessary
        current_flag = cls._get_flag(race_manager.ir["SessionFlags"])
        if current_flag == "green":
            race_manager.send_iracing_command(f"!yellow End of Stage {stage}")
        ## Grab the results for top 10
        race_manager.ir.freeze_var_buffer_latest()
        stage_top_ten_raw = race_manager.ir["SessionInfo"]["Sessions"] \
                            [race_manager.race_session_num]["ResultsPositions"][:10]
        stage_top_ten = []
        for position in stage_top_ten_raw:
            stage_top_ten.append([driver["UserName"] for driver in
                                  race_manager.ir["DriverInfo"]["Drivers"]
                                  if position["CarIdx"] == driver["CarIdx"]][0])
        ## Announce stage winner via chat
        logging.info(f"{stage_top_ten[0]} is the winner of Stage {stage}!")
        race_manager.send_iracing_command(f"{stage_top_ten[0]} is the winner of Stage {stage}!")
        ## Update race_manager.race_weekend.stage_X values
        if stage == 1:
            race_manager.race_weekend.stage_1.stage_results = stage_top_ten
        elif stage == 2:
            race_manager.race_weekend.stage_2.stage_results = stage_top_ten

        ##
        raise CustomException

    @classmethod
    def _process_race(cls, race_manager):
        for stage in [1, 2]:
            process_stage = threading.Thread(target=cls._process_stage, args=(race_manager, stage))
            process_stage.daemon = True
            process_stage.start()
            penalty_tracker = threading.Thread(target=cls._penalty_tracker, args=(race_manager, stage))
            penalty_tracker.daemon = True
            penalty_tracker.start()

            try:
                while True:
                    time.sleep(2)
            except CustomException:
                continue
            except KeyboardInterrupt:
                quit()
            
            logging.debug(f"Multithreading of stage {stage} is complete")
        logging.debug("Processing of first 2 stages complete")
        ## Stage 3 only needs the penalty tracker
        cls._penalty_tracker(race_manager, stage=3)
        

    @classmethod
    def race(cls, race_manager):
        while True:
            race_manager.ir.freeze_var_buffer_latest()
            ## Enum is useful to map session state id to its name
            logging.debug(
                f"Session state is {SessionName(race_manager.ir['SessionState']).name}"
            )
            ## Session state GET_IN_CAR (garage/settings menu)
            ## Session state PARADE_LAPS is also handled in this logic
            if race_manager.ir["SessionState"] == 1:
                logging.debug("Sessionstate 1 detected")
                ## Perform pre-race actions
                cls._pre_race_actions(race_manager)
            ## Pre-race penalties will finish being issued before session state
            ## changes from 3 -> 4. Just sleep and wait until the race starts
            elif race_manager.ir["SessionState"] == 3:
                logging.debug("Sleeping for sessionstate 3")
                time.sleep(1)
            ## Session state RACING
            elif race_manager.ir["SessionState"] == 4:
                logging.debug("Race has started!")
                cls._process_race(race_manager)
            ## Session state CHECKERED
            ## Checkered flag is officially out
            elif race_manager.ir["SessionState"] == 5:
                #start finalizing and assigning race results
                pass
            ## Session state COOLDOWN
            ## All cars have taken the checkered, time remaining counter has expired
            elif race_manager.ir["SessionState"] == 6:
                #probably break here, or even before it reaches this state
                pass
            else:
                logging.warning(
                    f"Unexpected issue: session state is \
                                {race_manager.ir['SessionState']}"
                )
