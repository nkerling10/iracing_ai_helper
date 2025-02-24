import PySimpleGUI as sg

class NextRaceTabLayout:
    @staticmethod
    def _build_next_race_layout() -> list[list]:
        return [
            [
                sg.Frame(
                    title="Week",
                    layout=[
                        [
                            sg.Text(
                                key="_-WEEK-_",
                                justification="center",
                                auto_size_text=True,
                            )
                        ]
                    ],
                    element_justification="center",
                    expand_x=True,
                    expand_y=True,
                    title_location="n",
                ),
                sg.Frame(
                    title="Track",
                    layout=[
                        [
                            sg.Text(
                                key="_-TRACK-_",
                                justification="center",
                                auto_size_text=True,
                            )
                        ]
                    ],
                    element_justification="center",
                    expand_x=True,
                    expand_y=True,
                    title_location="n",
                ),
                sg.Frame(
                    title="Stage 1",
                    layout=[[sg.Text(key="_-STAGE1-_", justification="center")]],
                    element_justification="center",
                    expand_x=True,
                    expand_y=True,
                    title_location="n",
                ),
                sg.Frame(
                    title="Stage 2",
                    layout=[[sg.Text(key="_-STAGE2-_", justification="center")]],
                    element_justification="center",
                    expand_x=True,
                    expand_y=True,
                    title_location="n",
                ),
                sg.Frame(
                    title="End",
                    layout=[[sg.Text(key="_-STAGE3-_", justification="center")]],
                    element_justification="center",
                    expand_x=True,
                    expand_y=True,
                    title_location="n",
                ),
            ],
        ]
    
    @classmethod
    def build_next_race_tab_layout(cls) -> list[list]:
        return [
            [
                sg.Frame(
                    title="Next Race",
                    layout=cls._build_next_race_layout(),
                    #size=(None, 75),
                    expand_x=True,
                )
            ],
            [
                sg.Button(
                    button_text="RACE",
                    key="-STARTRACEBUTTON-",
                    size=(None, 30)
                )
            ]
        ]
