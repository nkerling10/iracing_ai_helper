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
                                       in race_manager.season_data.declared_points_drivers else 0),
                    "playoff_points": race_manager.race_weekend.weekend_points[driver]["playoff_points"]
                                    + (1 if stage.stage_results.index(driver) == 0 and
                                       driver in race_manager.season_data.declared_points_drivers else 0)
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
                                + (race_manager.season_data.point_values[position.get("Position")][0]),
                "driver_points": race_manager.race_weekend.weekend_points[driver]["driver_points"]
                                + (race_manager.season_data.point_values[position.get("Position")][0] if driver
                                   in race_manager.season_data.declared_points_drivers else 0),
                "playoff_points": race_manager.race_weekend.weekend_points[driver]["playoff_points"]
                                + (5 if race_manager.race_weekend.race_results.index(position) == 0 and
                                   driver in race_manager.season_data.declared_points_drivers else 0)
            }

    @classmethod
    def main(cls, race_manager):
        cls.calculate_stage_points(race_manager)
        cls.calculate_race_points(race_manager)

    @classmethod
    def main_2(cls):
        pass

if __name__ == "__main__":
    drivers_in_race = [["William Byron", 17, False], ["Justin Allgaier", 7, True], ["Sheldon Creed", 00, True]]
    driver_objs = []
    for driver in drivers_in_race:
        driver_objs.append(Driver(driver_info=driver))
    for each in driver_objs:
        print(each.driver_points)

    PointsCalculator.main_2()