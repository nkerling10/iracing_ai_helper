import PySimpleGUI as sg
from pathlib import Path


class ConfigTabLayout:
    def build_config_tab_layout(local_database_file="",
                                local_roster_file="",
                                local_season_file="",
                                iracing_ai_roster_folder="",
                                iracing_ai_season_folder=""):
        return [
            [
                sg.Frame("Local Database File",
                    layout=[
                        [
                            sg.FileBrowse(
                                initial_folder= Path.cwd() / "database",
                                key="-LOCALDATABASEFILE-",
                                target="_LOCALDATABASEFILE_"),
                            sg.Input(
                                default_text=local_database_file,
                                text_color="black",
                                disabled=True,
                                key="_LOCALDATABASEFILE_",
                                expand_x=True)
                        ]
                    ],
                    expand_x=True,
                    pad=((0,0), (20, 5)),
                    title_location="n"
                )
            ],
            [
                sg.Frame("Local Roster File",
                    layout=[
                        [
                            sg.FileBrowse(
                                initial_folder= Path.cwd() / "rosters",
                                key="-LOCALROSTERFILE-",
                                target="_LOCALROSTERFILE_"),
                            sg.Input(
                                default_text=local_roster_file,
                                text_color="black",
                                disabled=True,
                                key="_LOCALROSTERFILE_",
                                expand_x=True)
                        ]
                    ],
                    expand_x=True,
                    pad=((0,0), (15, 5)),
                    title_location="n"
                )
            ],
            [
                sg.Frame("Local Season File",
                    layout=[
                        [
                            sg.FileBrowse(
                                initial_folder= Path.cwd() / "seasons",
                                key="-LOCALSEASONFILE-",
                                target="_LOCALSEASONFILE_"),
                            sg.Input(
                                default_text=local_season_file,
                                text_color="black",
                                disabled=True,
                                key="_LOCALSEASONFILE_",
                                expand_x=True)
                        ]
                    ],
                    expand_x=True,
                    pad=((0,0), (15, 5)),
                    title_location="n"
                )
            ],
            [
                sg.Frame("iRacing airosters -> roster folder",
                    layout=[
                        [
                            sg.FolderBrowse(
                                initial_folder=Path.home() / "Documents" / "iRacing" / "airosters",
                                key="-IRACINGAIROSTERFOLDER-",
                                target="_IRACINGAIROSTERFOLDER_"),
                            sg.Input(
                                default_text=iracing_ai_roster_folder,
                                text_color="black",
                                disabled=True,
                                key="_IRACINGAIROSTERFOLDER_",
                                expand_x=True)
                        ]
                    ],
                    expand_x=True,
                    pad=((0,0), (15, 5)),
                    title_location="n"
                )
            ],
            [
                sg.Frame("iRacing aiseasons -> season file",
                    layout=[
                        [
                            sg.FolderBrowse(
                                initial_folder=Path.home() / "Documents" / "iRacing" / "aiseasons",
                                key="-IRACINGAISEASONFOLDER-",
                                target="_IRACINGAISEASONFOLDER_"),
                            sg.Input(
                                default_text=iracing_ai_season_folder,
                                text_color="black",
                                disabled=True,
                                key="_IRACINGAISEASONFOLDER_",
                                expand_x=True),
                        ]
                    ],
                    expand_x=True,
                    pad=((0,0), (15, 10)),
                    title_location="n"
                )
            ],
            [
                sg.Button(button_text="Save config", key="-SAVECONFIGBUTTON-")
            ]

        ]
