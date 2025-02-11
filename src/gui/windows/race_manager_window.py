import PySimpleGUI as sg

def main_layout():
    return [
        [
            sg.Frame(
                layout=[[]],
                title="Race Active",
                expand_x=True,
                expand_y=True
            )
        ]
    ]


def _block_focus(window) -> None:
    """
    Function to block focus on main_window when the create season dialog appears
    """
    for key in window.key_dict:  # Remove dash box of all Buttons
        element = window[key]
        if isinstance(element, sg.Button):
            element.block_focus()


def main():
    window = sg.Window(
        "Create New Season", main_layout(), use_default_focus=False, finalize=True, modal=True
    )
    _block_focus(window)
    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, "Exit", "Cancel"):
            window.close()
            return