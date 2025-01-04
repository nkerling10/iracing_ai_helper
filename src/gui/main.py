import PySimpleGUI as sg
from src.gui.pages.roster.roster import Roster
from splash.splash import Splash
from pathlib import Path


def side_thread():
    window.read(timeout=5)

layout = [
   [
    sg.Text('Roster: '),
    sg.Input(key='_ROSTERFILE_', enable_events=True, disabled=True),
    sg.FileBrowse(file_types=(("JSON Files", "*.json"),),
                  button_text='ROSTER',
                  target='_ROSTERFILE_',
                  initial_folder="C:\\Users\\Nick\\Documents\\iracing_ai_helper\\rosters\\2025_Xfinity_Series_NSK_AI")
    ],
   [
    sg.Text('Season: '),
    sg.Input(key='_SEASONFILE_', enable_events=True, disabled=True),
    sg.FileBrowse(file_types=(("JSON Files", "*.json"),),
                  button_text='SEASON',
                  target='_SEASONFILE_',
                  initial_folder="C:\\Users\\Nick\\Documents\\iracing_ai_helper\\seasons")
    ],
   [
    sg.Text('Standings: '),
    sg.Text(key='-STANDINGS-', size=(6, 1)),
    sg.FileBrowse(file_types=(("JSON Files", "*.json"),))
    ],
   [
    sg.OK(button_text="Load"),
    sg.Cancel(button_text="Reset"),
    sg.Text(text="Status: "),
    sg.Text(key='-STATUS-')
    ]
]

window = sg.Window('NSK AI Season Manager - Alpha v0.1', layout, finalize=True)

roster_file = ''
season_file = ''

while True:
    event, values = window.read()
    if event in (sg.WIN_CLOSED, None, 'Exit'):
        break
    elif event == 'Reset':
        roster_file = ''
        window["_ROSTERFILE_"].update('')
        season_file = ''
        window["_SEASONFILE_"].update('')
        window["-STATUS-"].update("Files were cleared")
    elif event == '_ROSTERFILE_':
        roster_file_display =f"{values["_ROSTERFILE_"].split('/')[-2]}/{values["_ROSTERFILE_"].split('/')[-1]}"
        roster_file = Path(values["_ROSTERFILE_"])
        window["_ROSTERFILE_"].update(roster_file_display)
    elif event == '_SEASONFILE_':
        season_file_display = values["_SEASONFILE_"].split('/')[-1]
        season_file = Path(values["_SEASONFILE_"])
        window["_SEASONFILE_"].update(season_file_display)
    elif event == 'Load':
        if not roster_file and not season_file or not roster_file or not season_file:
            if not roster_file and not season_file:
                status = "Both files must be loaded"
            elif not roster_file and season_file:
                status = "Roster file must be loaded"
            elif roster_file and not season_file:
                status = "Season file must be loaded"
            window["-STATUS-"].update(status)
        else:
            window["-STATUS-"].update("Success!")
            #event, values = window.read(timeout=4000)
            Roster.main(roster_file)
            #window.close()
    else:
        print(f"Event: {event} - {values}")

'''
sg.set_options(font=("Arial Bold",14))
l1=sg.Text("Enter Name")
lt1=sg.Text("Address")
t1=sg.Input("", key='-NM-')
a11=sg.Input(key='-a11-')
a12=sg.Input(key='-a12-')
a13=sg.Input(key='-a13-')
tab1=[[l1,t1],[lt1],[a11], [a12], [a13]]
lt2=sg.Text("EmailID:")
lt3=sg.Text("Mob No:")
a21=sg.Input("", key='-ID-')
a22=sg.Input("", key='-MOB-')
tab2=[[lt2, a21], [lt3, a22]]
layout = [[sg.TabGroup([
   [sg.Tab('Basic Info', tab1),
   sg.Tab('Contact Details', tab2)]])],
   [sg.OK(), sg.Cancel()]
]


window = sg.Window('Tab Group Example', layout)
while True:
   event, values = window.read()
   print (event, values)
   if event in (sg.WIN_CLOSED, 'Exit'):
      break

window.close()
'''