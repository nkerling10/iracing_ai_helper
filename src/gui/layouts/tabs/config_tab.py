import PySimpleGUI as sg
from pathlib import Path


class ConfigTabLayout:
    def build_config_tab_layout(
        local_database_file: str = "", iracing_folder: str = ""
    ) -> list[list]:
        return [
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
                            ),
                            sg.Input(
                                default_text=iracing_folder,
                                text_color="black",
                                disabled=True,
                                key="_IRACINGFOLDER_",
                                expand_x=True,
                            ),
                        ]
                    ],
                    expand_x=True,
                    pad=((0, 0), (15, 10)),
                    title_location="n",
                )
            ],
            [sg.Button(button_text="Save config", key="-SAVECONFIGBUTTON-")],
        ]
