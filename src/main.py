## Standard library imports
import coloredlogs
import json
import logging
from pathlib import Path

## Third party imports

## Local imports
from config.app_settings.settings import Settings

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(module)s [%(levelname)s] %(message)s",
    force=True
)

class IracingData:
    def __init__(self):
        self.cars = self._load_data("cars.json")
        self.tracks = self._load_data("tracks.json")
    
    def _load_data(self, file: str):
        with open(Path.cwd() / "src" / "assets" / "references" / file) as data_file:
            return json.loads(data_file.read())

def main():
    iracing_data = IracingData()

if __name__ == "__main__":
    logger = logging.getLogger()
    coloredlogs.install(level='DEBUG', logger=logger)
    config = Settings()
    main()
