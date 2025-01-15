import PySimpleGUI as sg


class StandingsTabLayout:
    @staticmethod
    def _build_standings_layout() -> list[list]:
        return [[]]

    @staticmethod
    def _build_player_stats_layout() -> list[list]:
        return [
            [
                sg.Frame(
                    title="Points (Stage)",
                    layout=[
                        [
                            sg.Text(
                                key="_-POINTS-_",
                                justification="center",
                                auto_size_text=True,
                            )
                        ]
                    ],
                    element_justification="center",
                    title_location="n",
                    expand_x=True,
                    expand_y=True,
                ),
                sg.Frame(
                    title="Starts",
                    layout=[
                        [
                            sg.Text(
                                key="_-STARTS-_",
                                justification="center",
                                auto_size_text=True,
                            )
                        ]
                    ],
                    element_justification="center",
                    title_location="n",
                    expand_x=True,
                    expand_y=True,
                ),
                sg.Frame(
                    title="Wins",
                    layout=[
                        [
                            sg.Text(
                                key="_-WINS-_",
                                justification="center",
                                auto_size_text=True,
                            )
                        ]
                    ],
                    element_justification="center",
                    title_location="n",
                    expand_x=True,
                    expand_y=True,
                ),
                sg.Frame(
                    title="Top 5s",
                    layout=[
                        [
                            sg.Text(
                                key="_-TOP5-_",
                                justification="center",
                                auto_size_text=True,
                            )
                        ]
                    ],
                    element_justification="center",
                    title_location="n",
                    expand_x=True,
                    expand_y=True,
                ),
                sg.Frame(
                    title="Top 10s",
                    layout=[
                        [
                            sg.Text(
                                key="_-TOP10-_",
                                justification="center",
                                auto_size_text=True,
                            )
                        ]
                    ],
                    element_justification="center",
                    title_location="n",
                    expand_x=True,
                    expand_y=True,
                ),
            ],
            [
                sg.Frame(
                    title="DNFs",
                    layout=[
                        [
                            sg.Text(
                                key="_-DNF-_",
                                justification="center",
                                auto_size_text=True,
                            )
                        ]
                    ],
                    element_justification="center",
                    title_location="n",
                    expand_x=True,
                    expand_y=True,
                ),
                sg.Frame(
                    title="Laps Led",
                    layout=[
                        [
                            sg.Text(
                                key="_-LAPSLED-_",
                                justification="center",
                                auto_size_text=True,
                            )
                        ]
                    ],
                    element_justification="center",
                    title_location="n",
                    expand_x=True,
                    expand_y=True,
                ),
                sg.Frame(
                    title="Stage Wins",
                    layout=[
                        [
                            sg.Text(
                                key="_-STAGEWINS-_",
                                justification="center",
                                auto_size_text=True,
                            )
                        ]
                    ],
                    element_justification="center",
                    title_location="n",
                    expand_x=True,
                    expand_y=True,
                ),
                sg.Frame(
                    title="Poles",
                    layout=[
                        [
                            sg.Text(
                                key="_-POLES-_",
                                justification="center",
                                auto_size_text=True,
                            )
                        ]
                    ],
                    element_justification="center",
                    title_location="n",
                    expand_x=True,
                    expand_y=True,
                ),
            ],
        ]

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
                    size=(85, 80),
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
                    size=(None, 80),
                    title_location="n",
                ),
            ],
            [
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
    def build_standings_tab_layout(cls) -> list[list]:
        return [
            [
                sg.Frame(
                    title="Next Race",
                    layout=cls._build_next_race_layout(),
                    size=(None, 215),
                    expand_x=True,
                ),
                sg.Frame(
                    title="Player Stats",
                    layout=cls._build_player_stats_layout(),
                    size=(None, 215),
                    expand_x=True,
                ),
            ],
            [
                sg.Frame(
                    title="Standings",
                    layout=cls._build_standings_layout(),
                    expand_x=True,
                    expand_y=True,
                )
            ],
        ]
