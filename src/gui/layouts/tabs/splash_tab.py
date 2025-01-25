import os
import PySimpleGUI as sg
from pathlib import Path


class SplashTabLayout:
    def build_splash_tab_layout() -> list[list]:
        return [
            [
                sg.Column(
                    layout=[
                        [
                            sg.Button(
                                "Create a Season",
                                key="-CREATESEASONBUTTON-",
                                size=(25, 5),
                                font=50,
                            ),
                            sg.Button(
                                "Load a Season",
                                key="-LOADSAVEDSEASONBUTTON-",
                                size=(25, 5),
                                font=50,
                                disabled=(
                                    False
                                    if os.path.exists(Path.cwd() / "ai_seasons")
                                    else True
                                ),
                            )
                        ]
                    ],
                    justification="center",
                )
            ],
            [sg.HorizontalSeparator(color="black")],
            [sg.Text("Season Details", justification="center", font=36, expand_x=True)],
            [
                sg.Frame(
                    "Settings",
                    layout=[[]],
                    size=(None, 50),
                    expand_x=True,
                    expand_y=True,
                )
            ],
        ]
