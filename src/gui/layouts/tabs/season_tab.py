import PySimpleGUI as sg
from gui.layouts.tabs.season_subtabs.standings_tab import StandingsTabLayout
from gui.layouts.tabs.season_subtabs.roster_tab import RosterTabLayout
from gui.layouts.tabs.season_subtabs.schedule_tab import ScheduleTabLayout


class SeasonTab:
    def _build_season_tab() -> list[list]:
        return [
            [
                sg.TabGroup(
                    [
                        [
                            sg.Tab(
                                "Standings",
                                layout=StandingsTabLayout.build_standings_tab_layout(),
                                expand_x=True,
                                expand_y=True,
                            ),
                            sg.Tab(
                                "Roster",
                                layout=RosterTabLayout.build_roster_tab_layout(),
                                expand_x=True,
                                expand_y=True,
                            ),
                            sg.Tab(
                                "Schedule",
                                layout=ScheduleTabLayout.build_schedule_tab_layout(),
                                expand_x=True,
                                expand_y=True,
                            ),
                        ]
                    ],
                    key="-SEASONTABS-",
                    tab_location="topleft",
                    expand_x=True,
                    expand_y=True,
                )
            ]
        ]
