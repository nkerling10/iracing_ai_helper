class RaceSettings:
    def __init__(self):
        self.field_size = 50
        self.penalty_chance = 8
        self.pre_race_penalty_chance = 5
        self.penalties_player = ["Crew members over the wall too soon",
                                 "Too many men over the wall",
                                 "Tire violation"]
        self.penalties = ["Speeding - Too fast entering",
                          "Speeding - Too fast exiting",
                          "Crew members over the wall too soon",
                          "Too many men over the wall",
                          "Tire violation"]
        self.pre_race_penalties = ["Failed Inspection x2",
                                   "Failed Inspection x3",
                                   "Unapproved Adjustments"]