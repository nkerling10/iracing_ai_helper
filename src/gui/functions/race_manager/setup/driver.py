class Driver:
    def __new__(cls, name: str, car: any, points_eligibile: bool):
        instance = super().__new__(cls)
        return instance

    def __init__(self, name: str, car: any, points_eligibile: bool):
        self.name = name
        self.car = str(car)
        self.points_eligible = points_eligibile
        self.made_race = True
        self.stage_points = 0
        self.driver_points = 0
        self.owner_points = 0
        self.playoff_points = 0
