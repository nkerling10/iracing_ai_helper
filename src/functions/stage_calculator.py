import json
from pathlib import Path

with open(Path.cwd() / "src" / "assets" / "references" / "iracing_tracks.json", "r") as track_file:
    track_data = json.loads(track_file.read())


def calculate_stage_lengths(track_name, laps):
    track_short = [r["short_name"] for _k,r in track_data.items() if r["long_name"] == track_name][0]

    if track_short in ["Sebring"]:
        modifier = 0.3333
        
    elif track_short in ["COTA", "Laguna Seca"]:
        modifier = 0.3077
        
    elif track_short in ["Darlington"]:
        modifier = 0.3061
        
    elif track_short in ["Chicago", "Indianapolis",
                         "Dayonta"]:
        modifier = 0.3000
        
    elif track_short in ["Charlotte Roval"]:
        modifier = 0.2985
        
    elif track_short in ["Bristol"]:
        modifier = 0.2833
        
    elif track_short in ["Atlanta"]:
        modifier = 0.2761
        
    elif track_short in ["Talladega"]:
        modifier = 0.2660
        
    elif track_short in ["Sonoma"]:
        modifier = 0.2532
        
    elif track_short in ["Pocono"]:
        modifier = 0.2500
        
    elif track_short in ["Watkins Glen"]:
        modifier = 0.2439
        
    elif track_short in ["Martinsville", "Rockingham",
                         "Iowa"]:
        modifier = 0.2400
        
    elif track_short in ["Nashville"]:
        modifier = 0.2394
        
    elif track_short in ["Phoenix", "Las Vegas", "Homestead",
                         "Texas", "Charlotte", "Dover", "Kansas"]:
        modifier = 0.2250
        
    else:
        modifier = 0.2250

    stage_1 = laps * modifier
    print(stage_1)
    stage_2 = stage_1 * 2
    print(stage_2)
    quit()