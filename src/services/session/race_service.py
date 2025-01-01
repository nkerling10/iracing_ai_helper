## Standard library imports
import logging
import random

## Third party imports
import irsdk

## Local imports


class RaceService:
    def __init__(self):
        self.player_car_num = 0

    @staticmethod
    def _get_flag(flag):
        '''
            Big thanks to `fruzyna` for this function
                source: https://github.com/fruzyna/iracing-apps
            
            Determines the current flag status of the race. 
        '''
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
            elif flag & irsdk.Flags.yellow or flag & irsdk.Flags.yellow_waving \
                 or flag & irsdk.Flags.caution or flag & irsdk.Flags.caution_waving \
                 or flag & irsdk.Flags.debris:
                return "yellow"
            elif flag & irsdk.Flags.green or flag & irsdk.Flags.green_held:
                return "green"
            else:
                return "green"
    
    def _pit_penalty(self, car_num):
        '''
            Select and issue a pit penalty to designated car number
        '''
        penalty = random.choice(self.race_settings.penalties_player
                                if car_num == self.player_car_num
                                else self.race_settings.penalties)

        self.ir.freeze_var_buffer_latest()
        flag_color = self._get_flag(self.ir["SessionFlags"])

        if flag_color == "green":
            logging.info(f"PENALTY: Passthrough for #{car_num}: {penalty}")
            self._send_iracing_command(f"!bl {car_num} D")
            self._send_iracing_command(f"PT PENALTY #{car_num}: {penalty}")
        elif flag_color == "yellow":
            logging.info(f"PENALTY: EOL for #{car_num}: {penalty}")
            self._send_iracing_command(f"!eol {car_num}")
            self._send_iracing_command(f"EOL PENALTY #{car_num}: {penalty}")

    def _issue_pre_race_penalty(self, penalty_cars):
        '''
            Issue a pit penalty to each car as necessary
        '''
        for car_num, penalty in penalty_cars:
            if penalty in ["Failed Inspection x2", "Unapproved Adjustments"]:
                logging.info(f"#{car_num} to the rear: {penalty}")
                self._send_iracing_command(f"!eol {car_num}")
                self._send_iracing_command(f"PENALTY: #{car_num} to the rear: {penalty}")
            elif penalty in ["Failed Inspection x3"]:
                logging.info(f"#{car_num} to the rear: {penalty}")
                logging.info(f"#{car_num} drivethrough")
                self._send_iracing_command(f"!eol {car_num}")
                self._send_iracing_command(f"!bl {car_num} D")
                self._send_iracing_command(f"PENALTY: #{car_num} to the rear plus drivethrough penalty: {penalty}")


    def _pre_race_events(self):
        '''
            Handle all desired pre-race events

            Currently Implemented:
            1. Play `start your engines` sound file
            2. Issue gridstart command after waiting 30 seconds
            3. Issue pre-race penalties that were calculated
            4. TODO: Set up autostage/race result exporter
        '''
        logging.info("Playing sound file")
        try:
            sd.default.device = "Speakers (Realtek(R) Audio), MME"
            data, fs = sf.read(Path(f"{os.getcwd()}\\src\\assets\\start-your-engines.wav"), dtype='float32')  
            sd.play(data, fs)
        except Exception as e:
            logging.info(e)
        # wait 30 seconds for AI cars to grid
        self._send_iracing_command(f"Race will start in 30 seconds.")
        self._send_iracing_command(f"REMEMBER TO OPEN AUTOSTAGES!")
        logging.info("Sleeping for 30 seconds")
        time.sleep(30)
        logging.info("Issuing gridstart command")
        self._send_iracing_command("!gridstart")
        self.ir.freeze_var_buffer_latest()
        logging.info("Sleeping for 5 seconds")
        time.sleep(5)
        logging.info("Issuing pre-race penalties")
        self._issue_pre_race_penalty(penalty_cars)

    def main(self):
        pass