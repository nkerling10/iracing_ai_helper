## Standard library imports
import json
import logging
import PySimpleGUI as sg


class RosterTabLayout:

    @staticmethod
    def _tier_settings_drivers_table(title: str, tier_subject: str):
        return [
            [
                sg.Text(text=title, justification="c", pad=(0,0),
                        expand_x=True)
            ],
            [
                sg.Table(values=[], headings=[tier_subject, "Tier"],
                         expand_x=True)
            ]
        ]

    @classmethod
    def _tier_settings_tab_layout(cls):
        return [
            [
                sg.Column(layout=cls._tier_settings_drivers_table("Drivers", "Name"),
                           expand_x=True),
                sg.VerticalSeparator(color="black"),
                sg.Column(layout=cls._tier_settings_drivers_table("Car", "Car"),
                           expand_x=True)
            ]
        ]

    @staticmethod
    def _roster_file_track_choices(race_count: int = 0) -> list:
        races = []
        for num in range(1, race_count+1):
            races.append(num)
        return races

    @staticmethod
    def _roster_file_headers() -> list:
        return [
            "Car",
            "Name",
            "Age",
            "Skill",
            "Aggression",
            "Optimism",
            "Smoothness",
            "Pitcrew",
            "Strategy Risk",
        ]

    @classmethod
    def _roster_tab_layout(cls, key: str, driver_data: list = {}) -> list:
        return [
            [
                sg.Table(
                    values=driver_data,
                    headings=cls._roster_file_headers(),
                    justification="center",
                    key=key,
                    num_rows=len(driver_data),
                    expand_x=True,
                    expand_y=True,
                    auto_size_columns=False,
                    col_widths=[3, 15, 4, 4, 8, 7, 9, 6, 10],
                )
            ]
        ]

    @classmethod
    def build_roster_tab_layout(
        cls, active_driver_data: list = [], inactive_driver_data: list = []
    ) -> list:
        return [
            [
                sg.TabGroup(
                    [
                        [
                            sg.Tab(
                                "Active",
                                layout=cls._roster_tab_layout(
                                    "-ACTIVEDRIVERS-", active_driver_data
                                ),
                                expand_x=True,
                                expand_y=True,
                            ),
                            sg.Tab(
                                "Inactive",
                                layout=cls._roster_tab_layout(
                                    "-INACTIVEDRIVERS-", inactive_driver_data
                                ),
                                expand_x=True,
                                expand_y=True,
                            ),
                            sg.Tab(
                                "Tier Settings",
                                layout=cls._tier_settings_tab_layout(
                                    
                                ),
                                expand_x=True,
                                expand_y=True
                            )
                        ]
                    ],
                    key="-ROSTERTABLETABS-",
                    tab_location="topleft",
                    expand_x=True,
                    expand_y=True,
                ),
            ],
            [
                sg.Text(text="Race:", key="-TRACKBOXLABEL-", visible=False),
                sg.Combo(cls._roster_file_track_choices(), key="-TRACKBOX-", visible=False),
                sg.Text(key="-TRACKSTATUS-"),
            ],
            [sg.Text(key="-ROSTERFILELOADED-")],
            [
                sg.Button("Load", key="-LOADROSTERBUTTON-"),
                sg.Button("Randomize"),
                sg.Button("Copy"),
            ],
        ]


class SeasonTabLayout:
    @staticmethod
    def _season_file_headers() -> list:
        return ["Week", "Track", "Laps", "Results"]

    @classmethod
    def build_season_tab_layout(cls, season_data: list = []) -> list:
        return [
            [
                sg.Table(
                    values=season_data,
                    headings=cls._season_file_headers(),
                    justification="center",
                    key="-SEASONTABLE-",
                    num_rows=34,
                    expand_x=True,
                    expand_y=True,
                    hide_vertical_scroll = True,
                    enable_click_events = True,
                    enable_events=True,
                    starting_row_number=1
                )
            ],
            [sg.Text(text="File loaded:"), sg.Text(key="-SEASONFILELOADED-")],
            [sg.Button("Load", key="-LOADSEASONBUTTON-")]
        ]


class LoggingTabLayout:
    @staticmethod
    def _build_logging_tab_layout() -> list[list]:
        return [
            [
                sg.Multiline(
                    key="-LOGGINGBOX-",
                    write_only=True,
                    auto_refresh=True,
                    autoscroll=True,
                    expand_x=True,
                    expand_y=True,
                    disabled=True,
                    reroute_stdout=True,
                    reroute_stderr=True,
                    echo_stdout_stderr=True,
                )
            ],
            [sg.Button("CLEAR", key="-CLEARLOGBOX-")],
        ]
