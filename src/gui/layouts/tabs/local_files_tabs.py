import PySimpleGUI as sg
from gui.layouts.tabs.local_files.roster_tab import RosterTabLayout
from gui.layouts.tabs.local_files.season_tab import SeasonTabLayout

class LocalFileTab:
    def _build_local_file_tab() -> list[list]:
        return [
            [
                sg.TabGroup(
                    [
                        [
                            sg.Tab(
                                "Roster",
                                layout=RosterTabLayout.build_roster_tab_layout(),
                                expand_x=True,
                                expand_y=True,
                            ),
                            sg.Tab(
                                "Season",
                                layout=SeasonTabLayout.build_season_tab_layout(),
                                expand_x=True,
                                expand_y=True,
                            )
                        ]
                    ],
                    key="-LOCALFILETABS-",
                    tab_location="topleft",
                    expand_x=True,
                    expand_y=True,
                )
            ]
        ]
