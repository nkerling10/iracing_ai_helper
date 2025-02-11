import PySimpleGUI as sg
from os.path import exists
from pathlib import Path
import configparser
import coloredlogs
import logging

logger = logging.getLogger(__name__)


class Settings:
    def __init__(self) -> None:
        self.path = Path.cwd() / "src" / "config"
        self.config_file = "config.ini"
        self.first_time_setup = None
        self.database_path = None
        self.iracing_folder = None
        self._load_settings()

    def _load_settings(self) -> None:
        self._check_if_settings_file()
        if self.first_time_setup is True:
            return
        self._set_settings()

    def _check_if_settings_file(self) -> None:
        if not exists(self.path / self.config_file):
            with open(self.path / "base_config_setup.txt") as setup_file:
                base = setup_file.read()
            with open(self.path / self.config_file, "w") as file:
                file.write(base)
            self.first_time_setup = True
            return
        self.first_time_setup = False

    def _set_settings(self) -> None:
        settings = sg.UserSettings(
            path=self.path,
            filename=self.config_file,
            use_config_file=True,
            convert_bools_and_none=True,
        )
        self.database_path = settings["SYSTEM"]["DATABASE_PATH"]
        self.iracing_folder = Path(settings["PATHS"]["IRACING_FOLDER"])

    def _write_settings(self, local_db_file: Path, iracing_folder: Path) -> None:
        config = configparser.ConfigParser()
        config.read(self.path / self.config_file)
        config["SYSTEM"]["DATABASE_PATH"] = local_db_file
        config["PATHS"]["IRACING_FOLDER"] = iracing_folder

        with open(self.path / self.config_file, "w") as configfile:
            config.write(configfile)
        self._set_settings()
