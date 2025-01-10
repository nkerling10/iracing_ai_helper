import PySimpleGUI as sg

class SplashTabLayout:
    def build_splash_tab_layout() -> list[list]:
        return [
            [
                sg.Column(
                    layout=[
                        [
                            sg.Button("Load Season", key="-LOADSAVEDSEASONBUTTON-", size=(25, 10), font=50),
                            sg.Button("Create Season", key="-CREATESEASONBUTTON-", size=(25, 10), font=50)
                        ]
                    ],
                    justification="center")
            ]
        ]
