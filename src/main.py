from pathlib import Path
import platform
import tkinter as tk
import os
import json
from tkinter import filedialog
from assets import tracks

def get_next_race(ai_season_file):
    for event in ai_season_file.get("events"):
        if not event.get("results"):
            next_event = tracks.Track(event.get("trackId")).name
            return f"{next_event} is the next race"

def main():
    root = tk.Tk()
    root.withdraw()

    if platform.system() == "Darwin":
        default = Path.cwd()/"seasons"
    else:
        default = Path.home()/"Documents"/"iRacing"/"aiseasons"
    '''
    file_select = filedialog.askopenfilename(initialdir=default)
    '''
    file_select = Path(default/"2025 NSK Xfinity Series_withresults.json")
    with open(file_select, "r") as file:
        ai_season_file = json.loads(file.read())

    if ai_season_file["carId"] in [114, 115, 116]:
        season_type = "Xfinity"
    if ai_season_file["carId"] in [111, 123, 155]:
        season_type = "Truck"

    print(get_next_race(ai_season_file))

# gather requiered input

## process through cars with rotating drivers to set for the next race
## kick off the randomizer and paint assigner
## load the race_helper

if __name__ == '__main__':
    main()


# load a season file
# determine what race is up next (cycle through for results)