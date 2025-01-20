class Stage:
    def __init__(self, stage, stage_end_lap):
        self.stage = stage
        self.stage_end_lap = stage_end_lap
        self.stage_results = []
        self.pit_penalties = []
        self.stage_ending_early = False
        self.pits_are_closed = False
        self.last_lap_notice = False
        self.stage_complete = False
        self.advance_to_next_stage = False
