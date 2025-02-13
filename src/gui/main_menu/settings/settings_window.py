import PySimpleGUI as sg


def _block_focus(window) -> None:
    """
    Function to block focus on main_window when the create season dialog appears
    """
    for key in window.key_dict:  # Remove dash box of all Buttons
        element = window[key]
        if isinstance(element, sg.Button):
            element.block_focus()


def _settings_layout():
    return [
        [
            sg.Exit()
        ]
    ]


def main():
    window = sg.Window(
        "Settings",
        _settings_layout(),
        no_titlebar=True,
        finalize=True,
        size=(450,250),
        keep_on_top=True
    )
    _block_focus(window)
    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, "Exit", "Cancel"):
            window.close()
            return


if __name__ == "__main__":
    main()
