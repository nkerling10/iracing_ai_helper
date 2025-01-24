import sqlite3

class PointsImporter:
    def __init__(self, race_manager):
        self.conn = sqlite3.connect("C:/Users/Nick/Documents/iracing_ai_helper/database/iracing_ai_helper.db")
        self.driver_points_table = "XFINITY_2025_POINTS_DRIVER"
        self.owner_points_table = "XFINITY_2025_POINTS_OWNER"
        self.main(race_manager)

    def update_driver_points(self, result, driver):
        win = True if driver.finish_pos == 1 else False
        top5 = True if driver.finish_pos <= 5 else False
        top10 = True if driver.finish_pos <= 10 else False

        name, driver_points, stage_points, playoff_points, starts, \
            wins, top5s, top10s, dnfs, laps_led, stage_wins, poles = result

        driver_points += driver.driver_points
        stage_points += driver.stage_points
        playoff_points += driver.playoff_points
        starts += 1
        wins += 1 if win else 0
        top5s += 1 if top5 else 0
        top10s += 1 if top10 else 0
        dnfs += 1 if driver.dnf else 0
        laps_led += driver.laps_led
        stage_wins += driver.stage_wins
        poles += 1 if driver.pole_winner else 0
        try:
            self.conn.execute(f"""UPDATE {self.driver_points_table} SET
                                POINTS = ?,
                                STAGE_POINTS = ?,
                                PLAYOFF_POINTS = ?,
                                STARTS = ?,
                                WINS = ?,
                                TOP_5s = ?,
                                TOP_10s = ?,
                                DNFs = ?,
                                LAPS_LED = ?,
                                STAGE_WINS = ?,
                                POLES = ?
                                WHERE NAME = ?
                                """, (driver_points, stage_points, playoff_points,
                                    starts, wins, top5s, top10s, dnfs, laps_led,
                                    stage_wins, poles, name))
            self.conn.commit()
            print(f"Update of {driver.name} was successful")
        except Exception as e:
            print(e)
            self.conn.close()
            quit()

    def add_driver_points_entry(self, driver):
        win = True if driver.finish_pos == 1 else False
        top5 = True if driver.finish_pos <= 5 else False
        top10 = True if driver.finish_pos <= 10 else False
        try:
            self.conn.execute(f"""INSERT INTO {self.driver_points_table} (
                            NAME,
                            POINTS,
                            STAGE_POINTS,
                            PLAYOFF_POINTS,
                            STARTS,
                            WINS,
                            TOP_5s,
                            TOP_10s,
                            DNFs,
                            LAPS_LED,
                            STAGE_WINS,
                            POLES
                            ) VALUES (
                            ?,
                            ?,
                            ?,
                            ?,
                            1,
                            ?,
                            ?,
                            ?,
                            ?,
                            ?,
                            ?,
                            ?)""", (driver.name, driver.driver_points,
                                    driver.stage_points, driver.playoff_points,
                                    1 if win else 0,
                                    1 if top5 else 0, 1 if top10 else 0,
                                    1 if driver.dnf else 0,
                                    driver.laps_led, driver.stage_wins,
                                    1 if driver.pole_winner else 0))
            self.conn.commit()
            print(f"Insert of {driver.name} was successful")
        except Exception as e:
            print(e)

    def update_owner_points(self, result, driver):
        win = True if driver.finish_pos == 1 else False

        car, _team, attempts, points, wins, stage_wins = result
        attempts += 1
        points += driver.owner_points
        wins += 1 if win else 0
        stage_wins += driver.stage_wins
        try:
            self.conn.execute(f"""UPDATE {self.owner_points_table} SET
                                CAR = ?,
                                ATTEMPTS = ?,
                                POINTS = ?,
                                WINS = ?,
                                STAGE_WINS = ?
                                WHERE CAR = ?
                                """, (car, attempts, points,
                                      wins, stage_wins, car))
            self.conn.commit()
            print(f"Update of {driver.car} was successful")
        except Exception as e:
            print(e)
            self.conn.close()
            quit()

    def add_owner_points_entry(self, driver):
        win = True if driver.finish_pos == 1 else False
        try:
            self.conn.execute(f"""INSERT INTO {self.owner_points_table} (
                            CAR,
                            TEAM,
                            ATTEMPTS,
                            POINTS,
                            WINS,
                            STAGE_WINS
                            ) VALUES (
                            ?,
                            ?,
                            ?,
                            ?,
                            ?,
                            ?)""", (driver.car, driver.team, 1,
                                    driver.owner_points, 1 if win else 0,
                                    driver.stage_wins))
            self.conn.commit()
            print(f"Insert of {driver.car} car was successful")
        except Exception as e:
            print(e)


    def main(self, race_manager):
        for driver in race_manager.race_weekend.drivers:
            if driver.made_race:
                ## Process driver points
                '''
                if driver.points_eligible:
                    try:
                        result = self.conn.execute(f"SELECT * FROM {self.driver_points_table} WHERE NAME is ?", (driver.name,)).fetchall()[0]
                        self.update_driver_points(result, driver)
                    except sqlite3.OperationalError:
                        self.add_driver_points_entry(driver)
                '''
                ## Process owner points
                try:
                    result = self.conn.execute(f"SELECT * FROM {self.owner_points_table} WHERE CAR is ?", (driver.car,)).fetchall()[0]
                    self.update_owner_points(result, driver)
                except (sqlite3.OperationalError, IndexError):
                    self.add_owner_points_entry(driver)

        self.conn.close()
            