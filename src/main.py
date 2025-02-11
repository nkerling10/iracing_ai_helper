## Standard library imports
import coloredlogs
import logging

## Third party imports

## Local imports
from config.app_settings.settings import Settings
import launcher

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(module)s [%(levelname)s] %(message)s",
    force=True
)

def main():
    launcher


if __name__ == "__main__":
    logger = logging.getLogger()
    coloredlogs.install(level='DEBUG', logger=logger)
    config = Settings()
    main()
