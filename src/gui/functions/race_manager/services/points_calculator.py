class PointsCalculator:
    @staticmethod
    def calculate_stage_points(race_manager):
        for stage in race_manager.race_weekend.stage_results[:2]:
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
                driver_obj = [
                    driver
                    for driver in race_manager.race_weekend.drivers
                    if driver.car_idx == position.get("CarIdx")
                ][0]
            except IndexError:
                continue
            if not position["ReasonOutStr"] == "DQInv":
                driver_obj.fastest_lap = (
                    True
                    if race_manager.ir["SessionInfo"]["Sessions"][
                        race_manager.race_session_num
                    ]["ResultsPositions"]["ResultsFastestLap"]["CarIdx"]
                    == driver_obj.car_idx
                    else False
                )
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
                if driver_obj.fastest_lap:
                    driver_obj.owner_points += 1
                    driver_obj.driver_points += 1
            else:
                driver_obj.made_race = False

    @classmethod
    def main(cls, race_manager):
        cls.calculate_stage_points(race_manager)
        cls.calculate_race_points(race_manager)
