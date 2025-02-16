import json
import logging

logger = logging.getLogger(__name__)

CUP_SERIES = [139, 140, 141]
XFINITY_SERIES = [114, 115, 116]
TRUCK_SERIES = [111, 123, 155]
ARCA_SERIES = [24]
INDYCAR_SERIES = [99]
SRX_SERIES = [179]
LATEMODEL_SERIES = [164]


def _load_iracing_season(season_file: str):
    with open(season_file, "r") as file:
        iracing_season = json.loads(file.read())
    cars_selected = [car.get("car_id") for car in iracing_season.get("carSettings")]
    if cars_selected == CUP_SERIES:
        return "CUP"
    elif cars_selected == XFINITY_SERIES:
        return "XFINITY"
    elif cars_selected == TRUCK_SERIES:
        return "TRUCK"
    elif cars_selected == ARCA_SERIES:
        return "ARCA"
    elif cars_selected == INDYCAR_SERIES:
        return "INDYCAR"
    elif cars_selected == SRX_SERIES:
        return "SRX"
    elif cars_selected == LATEMODEL_SERIES:
        return "LATEMODEL"
    else:
        logger.debug(f"Car IDs for loaded season: {cars_selected}")
        return "CUSTOM"
    