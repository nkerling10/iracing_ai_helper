class Driver:
    def __new__(cls, car_idx: int, name: str, car: any, team: str, points_eligibile: bool):
        instance = super().__new__(cls)
        return instance

    def __init__(
        self, car_idx: int, name: str, car: any, team: str, points_eligibile: bool
    ):
        self.car_idx = car_idx
        self.name = name
        self.car = str(car)
        self.team = team
        self.points_eligible = points_eligibile
        self.made_race = True
        self.pole_winner = False
        self.finish_pos = None
        self.dnf = False
        self.fastest_lap = False
        self.laps_led = 0
        self.stage_wins = 0
        self.stage_points = 0
        self.driver_points = 0
        self.owner_points = 0
        self.playoff_points = 0
        self.poles = 0
