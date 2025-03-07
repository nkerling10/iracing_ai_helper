import PySimpleGUI as sg


class StandingsTabLayout:
    @staticmethod
    def _driver_points_headers() -> list:
        return [
            "DRIVER",
            "POINTS",
            "STG PTS",
            "PLY PTS",
            "STARTS",
            "WINS",
            "TOP 5s",
            "TOP 10s",
            "DNFs",
            "LAPS LED",
            "STG WINS",
            "POLES",
        ]

    @staticmethod
    def _owner_points_headers() -> list:
        return ["CAR", "TEAM", "ATTEMPTS", "POINTS", "WINS", "STAGE WINS"]

    @staticmethod
    def _playoff_standings_headers() -> list:
        return ["CAR", "DRIVER", "WINS", "PLAYOFF PTS"]

    @classmethod
    def _build_driver_points_table(cls, driver_points: list = []) -> list[list]:
        return [
            [
                sg.Table(
                    values=driver_points,
                    headings=cls._driver_points_headers(),
                    justification="center",
                    key="-DRIVERPOINTSTABLE-",
                    num_rows=20,
                    expand_x=True,
                    expand_y=True,
                    auto_size_columns=False,
                    col_widths=[15],
                    starting_row_number=1,
                )
            ]
        ]

    @classmethod
    def _build_owner_points_table(cls, owner_points: list = []) -> list[list]:
        return [
            [
                sg.Table(
                    values=owner_points,
                    headings=cls._owner_points_headers(),
                    justification="center",
                    key="-OWNERPOINTSTABLE-",
                    num_rows=20,
                    expand_x=True,
                    expand_y=True,
                    auto_size_columns=True,
                    starting_row_number=1,
                )
            ]
        ]
    
    @classmethod
    def _build_playoffs_table(cls, playoff_standings: list = []) -> list[list]:
        return [
            [
                sg.Table(
                    values=playoff_standings,
                    headings=cls._playoff_standings_headers(),
                    justification="center",
                    key="-PLAYOFFSTANDINGSTABLE-",
                    num_rows=16,
                    expand_x=True,
                    expand_y=True,
                    auto_size_columns=True,
                    starting_row_number=1,
                )
            ]
        ]

    @classmethod
    def _build_standings_layout(cls) -> list[list]:
        return [
            [
                sg.TabGroup(
                    [
                        [
                            sg.Tab(
                                "Driver",
                                cls._build_driver_points_table(),
                                key="-driverpointsetab-",
                            ),
                            sg.Tab(
                                "Owner",
                                cls._build_owner_points_table(),
                                key="-ownerpointstab-",
                            ),
                            sg.Tab(
                                "Playoffs",
                                cls._build_playoffs_table(),
                                key="-playoffstandingstab-",
                            ),
                        ]
                    ],
                    key="-tabgroup1-",
                    tab_location="topleft",
                    expand_x=True,
                    expand_y=True,
                )
            ]
        ]

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

    @classmethod
    def build_standings_tab_layout(cls) -> list[list]:
        return [
            [
                sg.Frame(
                    title="Player Stats",
                    layout=cls._build_player_stats_layout(),
                    size=(None, 150),
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
