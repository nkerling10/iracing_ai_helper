from pathlib import Path
import platform
import tkinter as tk
import os
import json
from tkinter import filedialog
from assets import tracks

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
    file_select = Path(default/"2025 NSK Xfinity Series.json")
    with open(file_select, "r") as file:
        ai_season_file = json.loads(file.read())

    for event in ai_season_file.get("events"):
        print(tracks.Track(event.get("trackId")).name)

# gather requiered input

## process through cars with rotating drivers to set for the next race
## kick off the randomizer and paint assigner
## load the race_helper

if __name__ == '__main__':
    main()