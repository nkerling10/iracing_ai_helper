import PySimpleGUI as sg
from pathlib import Path


class ConfigTabLayout:
    def build_config_tab_layout(
        player_name: str = "", local_database_file: str = "", iracing_folder: str = ""
    ) -> list[list]:
        return [
            [
                sg.Frame(
                    "Player Name",
                    layout=[
                        [
                            sg.Input(
                                default_text=player_name,
                                text_color="black",
                                disabled=False,
                                key="-PLAYERNAME-",
                                expand_x=True,
                                tooltip="Enter your name exactly as it appears in iRacing!",
                                focus = False,
                                background_color="white"
                            ),
                        ]
                    ],
                    expand_x=True,
                    pad=((0, 0), (20, 5)),
                    title_location="n",
                )
            ],
            [
                sg.Frame(
                    "Local Database File",
                    layout=[
                        [
                            sg.FileBrowse(
                                initial_folder=Path.cwd() / "database",
                                key="-LOCALDATABASEFILE-",
                                target="_LOCALDATABASEFILE_",
                            ),
                            sg.Input(
                                default_text=local_database_file,
                                text_color="black",
                                disabled=True,
                                key="_LOCALDATABASEFILE_",
                                expand_x=True,
                                focus = False
                            ),
                        ]
                    ],
                    expand_x=True,
                    pad=((0, 0), (20, 5)),
                    title_location="n",
                )
            ],
            [
                sg.Frame(
                    "iRacing filepath",
                    layout=[
                        [
                            sg.FolderBrowse(
                                initial_folder=Path.home()
                                / "Documents"
                                / "iRacing"
                                / "aiseasons",
                                key="-IRACINGFOLDER-",
                                target="_IRACINGFOLDER_",
                                tooltip="Be sure to select the root iRacing folder itself!"
                            ),
                            sg.Input(
                                default_text=iracing_folder,
                                text_color="black",
                                disabled=True,
                                key="_IRACINGFOLDER_",
                                expand_x=True,
                                tooltip="Be sure to select the root iRacing folder itself!",
                                focus = False
                            ),
                        ]
                    ],
                    expand_x=True,
                    pad=((0, 0), (15, 10)),
                    title_location="n",
                )
            ],
            [sg.Button(button_text="Save config", key="-SAVECONFIGBUTTON-", focus=True)],
        ]
