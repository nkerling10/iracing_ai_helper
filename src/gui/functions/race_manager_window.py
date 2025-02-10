import PySimpleGUI as sg

def main_layout():
    return [[]]


def main():
    window = sg.Window(
        "Create New Season", main_layout(), use_default_focus=False, finalize=True, modal=True
    )
    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, "Exit", "Cancel"):
            window.close()
            return