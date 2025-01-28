class PointsCalculator:
    @staticmethod
    def calculate_stage_points(race_manager):
        for stage in race_manager.race_weekend.stage_results[0:1]:
            for driver_name in stage.stage_results:
                driver_obj = [
                    driver
                    for driver in race_manager.race_weekend.drivers
                    if driver_name == driver.name
                ][0]
                driver_obj.stage_wins += (
                    1 if stage.stage_results.index(driver_name) == 0 else 0
                )
                driver_obj.stage_points += 10 - stage.stage_results.index(driver_name)
                driver_obj.playoff_points += (
                    1
                    if stage.stage_results.index(driver_name) == 0
                    and driver_obj.points_eligible
                    else 0
                )

    @staticmethod
    def calculate_race_points(race_manager):
        for position in race_manager.race_weekend.stage_results[2].stage_results:
            try:
                driver_name = race_manager.race_weekend.race_data.driver_caridx_map[
                    position.get("CarIdx")
                ].get("name")
                driver_obj = [
                    driver
                    for driver in race_manager.race_weekend.drivers
                    if driver.name == driver_name
                ][0]
            except IndexError:
                continue
            if not position["ReasonOutStr"] == "DQInv":
                driver_obj.laps_led = position.get("LapsLed")
                driver_obj.finish_pos = position.get("Position")
                driver_obj.dnf = (
                    True if position["ReasonOutStr"] != "Running" else False
                )
                driver_obj.owner_points += race_manager.season_data.point_values[
                    position.get("Position") - 1
                ]
                driver_obj.driver_points += (
                    race_manager.season_data.point_values[position.get("Position") - 1]
                    if driver_obj.points_eligible
                    else 0
                )
                driver_obj.playoff_points += (
                    5
                    if race_manager.race_weekend.stage_results[2].stage_results.index(
                        position
                    )
                    == 0
                    and driver_obj.points_eligible
                    else 0
                )
            else:
                driver_obj.made_race = False

    @classmethod
    def main(cls, race_manager):
        cls.calculate_stage_points(race_manager)
        cls.calculate_race_points(race_manager)
