class Stage:
    def __init__(self, stage_end_lap=0):
        self.stage_end_lap = stage_end_lap
        self.stage_results = []
        self.caution_count = 0
        self.pit_penalties = []
