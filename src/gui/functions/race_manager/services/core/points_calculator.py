race_points_map = {
    1: 40,
    2: 35,
    3: 34,
    4: 33,
    5: 32,
    6: 31,
    7: 30,
    8: 29,
    9: 28,
    10: 27,
    11: 26,
    12: 25,
    13: 24,
    14: 23,
    15: 22,
    16: 21,
    17: 20,
    18: 19,
    19: 18,
    20: 17,
    21: 16,
    22: 15,
    23: 14,
    24: 13,
    25: 12,
    26: 11,
    27: 10,
    28: 9,
    29: 8,
    30: 7,
    31: 6,
    32: 5,
    33: 4,
    34: 3,
    35: 2,
    36: 1,
    37: 1,
    38: 1,
    39: 1,
    40: 1,
    41: 0,
    42: 0,
    43: 0
}

class PointsCalculator:
    @staticmethod
    def calculate_stage_points(race_manager):
        for stage in race_manager.race_weekend.stage_results:
            for driver in stage.stage_results:
                if driver not in race_manager.race_weekend.weekend_points:
                    race_manager.race_weekend.weekend_points[driver] = {"owner_points": 0,
                                                                        "driver_points": 0,
                                                                        "playoff_points": 0}
                race_manager.race_weekend.weekend_points[driver] = {
                    "owner_points": race_manager.race_weekend.weekend_points[driver]["owner_points"]
                                    + (10 - stage.stage_results.index(driver)),
                    "driver_points": race_manager.race_weekend.weekend_points[driver]["driver_points"]
                                    + (10 - stage.stage_results.index(driver) if driver
                                       in race_manager.race_weekend.declared_points_drivers else 0),
                    "playoff_points": race_manager.race_weekend.weekend_points[driver]["playoff_points"]
                                    + (1 if stage.stage_results.index(driver) == 0 and
                                       driver in race_manager.race_weekend.declared_points_drivers else 0)
                }

    @staticmethod
    def calculate_race_points(race_manager):
        for position in race_manager.race_weekend.race_results:
            driver = race_manager.race_weekend.driver_caridx_map[position.get("CarIdx")].get("name")
            if driver not in race_manager.race_weekend.weekend_points:
                race_manager.race_weekend.weekend_points[driver] = {"owner_points": 0,
                                                                    "driver_points": 0,
                                                                    "playoff_points": 0}
            race_manager.race_weekend.weekend_points[driver] = {
                "owner_points": race_manager.race_weekend.weekend_points[driver]["owner_points"]
                                + (race_points_map[position.get("Position")]),
                "driver_points": race_manager.race_weekend.weekend_points[driver]["driver_points"]
                                + (race_points_map[position.get("Position")] if driver
                                   in race_manager.race_weekend.declared_points_drivers else 0),
                "playoff_points": race_manager.race_weekend.weekend_points[driver]["playoff_points"]
                                + (5 if race_manager.race_weekend.race_results.index(position) == 0 and
                                   driver in race_manager.race_weekend.declared_points_drivers else 0)
            }

    @classmethod
    def main(cls, race_manager):
        cls.calculate_stage_points(race_manager)
        cls.calculate_race_points(race_manager)

if __name__ == "__main__":
    PointsCalculator.main()