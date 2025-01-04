import PySimpleGUI as sg
import json

class Driver:
    def __init__(self, driver):
        self.car = driver["carNumber"]
        self.name = driver["driverName"]
        self.age = driver["driverAge"]
        self.skill = driver["driverSkill"]
        self.aggression = driver["driverAggression"]
        self.optimism = driver["driverOptimism"]
        self.smoothness = driver["driverSmoothness"]
        self.pitcrew = driver["pitCrewSkill"]
        self.strategy = driver["strategyRiskiness"]

class Roster:
    def _build_table(driver_objs):
        driver_data = []

        headers = [
            "Car",
            "Name",
            "Age",
            "Skill",
            "Aggr.",
            "Opt.",
            "Smth.",
            "Pitcrew",
            "Strat."
        ]

        col_widths = list(map(lambda x:len(x)+2, headers))

        for obj in driver_objs:
            driver_data.append(
                [
                    obj.car,
                    obj.name,
                    obj.age,
                    obj.skill,
                    obj.aggression,
                    obj.optimism,
                    obj.smoothness,
                    obj.pitcrew,
                    obj.strategy
                ]
            )

        return headers, driver_data, col_widths

    @classmethod
    def _format_drivers(cls, driver_data):
        driver_objs = []
        for driver in driver_data:
            driver_objs.append(Driver(driver))

        return driver_objs

    @classmethod
    def _assemble_data(cls, drivers):
        driver_objs = cls._format_drivers(drivers)
        headers, driver_data, col_widths = cls._build_table(driver_objs)
        return headers, driver_data, col_widths

    @classmethod
    def main(cls, data):
        with open(data, 'r') as file:
            roster_data = json.loads(file.read())

        headers, driver_data, col_widths = cls._assemble_data(roster_data.get("drivers"))

        layout = [[sg.Table(driver_data,
                            headings=headers,
                            justification='center',
                            key='-TABLE-',
                            num_rows=len(driver_data))],]

        window = sg.Window('NSK AI Roster Randomizer - Alpha v0.1',
                           layout,
                           finalize=True,
                           size=(715, 700))
        while True:
            event, values = window.read()
            print(event)
            if event in (sg.WIN_CLOSED, None, 'Exit'):
                break

if __name__ == '__main__':
    Roster.main("C:\\Users\\Nick\\Documents\\iracing_ai_helper\\rosters\\2025_Xfinity_Series_NSK_AI\\roster.json")
