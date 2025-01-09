import PySimpleGUI as sg
from os.path import exists
from pathlib import Path
import configparser

class Settings:
    def __init__(self):
        self.path = Path.cwd() / "src" / "gui" / "config"
        self.config_file = "config.ini"
        self.first_time_setup = None
        self.database_path = None
        self.local_roster_file = None
        self.local_season_file = None
        self.iracing_ai_roster_folder = None
        self.iracing_ai_season_folder = None
        self._load_settings()
    
    def _load_settings(self):
        self._check_if_settings_file()
        if self.first_time_setup is True:
            return
        self._set_settings()
    
    def _check_if_settings_file(self):
        if not exists(self.path / self.config_file):
            with open(self.path / "base_config_setup.txt") as setup_file:
                base = setup_file.read()
            with open(self.path / self.config_file, 'w') as file:
                file.write(base)
            self.first_time_setup = True
            return
        self.first_time_setup = False
    
    def _set_settings(self):
        settings = sg.UserSettings(
            path=self.path,
            filename=self.config_file,
            use_config_file=True,
            convert_bools_and_none=True,
        )
        self.database_path = settings["SYSTEM"]["DATABASE_PATH"]
        self.local_roster_file = settings["PATHS"]["LOCAL_ROSTER_FILE"]
        self.local_season_file = settings["PATHS"]["LOCAL_SEASON_FILE"]
        self.iracing_ai_roster_folder = settings["PATHS"]["AI_ROSTER_FOLDER"]
        self.iracing_ai_season_folder = settings["PATHS"]["AI_SEASON_FOLDER"]

    def _write_settings(self,
                        local_db_file,
                        local_roster_file,
                        local_season_file,
                        ai_roster_folder,
                        ai_season_folder):
        config = configparser.ConfigParser()
        config.read(self.path / self.config_file)
        config["SYSTEM"]["DATABASE_PATH"] = local_db_file
        config["PATHS"]["LOCAL_ROSTER_FILE"] = local_roster_file
        config["PATHS"]["LOCAL_SEASON_FILE"] = local_season_file
        config["PATHS"]["AI_ROSTER_FOLDER"] = ai_roster_folder
        config["PATHS"]["AI_SEASON_FOLDER"] = ai_season_folder

        with open(self.path / self.config_file, 'w') as configfile:
            config.write(configfile)
        self._set_settings()