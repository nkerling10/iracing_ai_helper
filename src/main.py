## Standard library imports
import coloredlogs
import logging

## Third party imports

## Local imports
from config.app_settings.settings import Settings

def main():
    pass


if __name__ == "__main__":
    # create logger with 'spam_application'
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(module)s [%(levelname)s] %(message)s",
        force=True
    )
    logger = logging.getLogger()
    coloredlogs.install(level='DEBUG', logger=logger)

    logger.critical("test!")


    config = Settings()
    main()
