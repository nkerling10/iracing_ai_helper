## Standard library imports
import logging
import os
import random
import time
from pathlib import Path

## Third party imports
import irsdk
import sounddevice as sd
import soundfile as sf

## Local imports


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
            else:
                return "green"

    @staticmethod
    def _pit_penalty(cls, race_manager, car_num):
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
            race_manager._send_iracing_command(f"!bl {car_num} D")
            penalty_message = f"Passthrough PENALTY #{car_num}: {penalty}"
        elif flag_color == "yellow":
            logging.info(f"PENALTY: EOL for #{car_num}: {penalty}")
            race_manager._send_iracing_command(f"!eol {car_num}")
            penalty_message = f"EOL PENALTY #{car_num}: {penalty}"
        race_manager._send_iracing_command(penalty_message)

    @staticmethod
    def _issue_pre_race_penalty(race_manager):
        """
        Issue a pre-race penalty to each defined car
        """
        for car_num, penalty in race_manager.race_weekend.pre_race_penalties:
            if penalty in ["Failed Inspection x2", "Unapproved Adjustments"]:
                logging.info(f"#{car_num} to the rear: {penalty}")
                race_manager._send_iracing_command(f"!eol {car_num}")
                penalty_message = f"PENALTY: #{car_num} to the rear: {penalty}"
            elif penalty in ["Failed Inspection x3"]:
                logging.info(f"#{car_num} to the rear plus drivethrough: {penalty}")
                race_manager._send_iracing_command(f"!eol {car_num}")
                race_manager._send_iracing_command(f"!bl {car_num} D")
                penalty_message = f"PENALTY: #{car_num} to the rear plus drivethrough penalty: {penalty}"
            race_manager._send_iracing_command(penalty_message)

    @staticmethod
    def _play_sound():
        logging.debug("Playing sound file")
        try:
            sd.default.device = "Speakers (Realtek(R) Audio), MME"
            data, fs = sf.read(
                Path(f"{os.getcwd()}\\src\\assets\\sounds\\start-your-engines.wav"),
                dtype="float32",
            )
            sd.play(data, fs)
        except Exception as e:
            logging.error(e)

    @classmethod
    def _pre_race_actions(cls, race_manager):
        """
        Ideally wait until player has gotten into car first

        if player in car:
            cls._play_sound()
        else:
            time.sleep(1)
        """
        ## Play starting command
        cls._play_sound()
        ## Wait 30 seconds while sound plays
        logging.debug("Sleeping for 30 seconds")
        time.sleep(30)
        ## Issue gridstart command, then sleep 10 seconds
        logging.debug("Issuing gridstart command")
        race_manager._send_iracing_command("!gridstart")
        time.sleep(10)
        ## Issue calculated pre-race penalties
        if len(race_manager.race_weekend.pre_race_penalties) > 0:
            logging.debug("Issuing pre-race penalties")
            cls._issue_pre_race_penalty(race_manager)
        else:
            logging.debug("No pre-race penalties to issue")

    @classmethod
    def race(cls, race_manager):
        while True:
            ## IF RACE HAS NOT ALREADY STARTED!!
            ## Perform pre-race actions
            cls._pre_race_actions(race_manager)


RaceService.race("blah")
