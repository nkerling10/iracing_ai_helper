import json
import logging
import os
import PySimpleGUI as sg
import shutil
from pathlib import Path

from create_new_season import _create_new_season
from check_season_type import _load_iracing_season


logger = logging.getLogger(__name__)

ai_seasons_file_path = Path.cwd() / "ai_seasons"
base_files_roster_path = Path.cwd() / "base_files" / "rosters"


def _block_focus(window) -> None:
    """
    Function to block focus on main_window when the create season dialog appears
    """
    for key in window.key_dict:  # Remove dash box of all Buttons
        element = window[key]
        if isinstance(element, sg.Button):
            element.block_focus()


def _delete_file(file_path, dir=False):
    try:
        if dir:
            shutil.rmtree(file_path)
        else:
            os.remove(file_path)
        logger.info(f"{file_path} deleted successfully.")
        return True
    except FileNotFoundError:
        logger.warning(f"{file_path} not found.")
    except PermissionError:
        logger.critical(f"You don't have permission to delete this {file_path}.")
    except Exception as e:
        logger.critical("An error occurred:", e)
    return False


def _delete_season_file() -> None:
    select_season_settings_file = sg.popup_get_file(
        "Delete a Season",
        initial_folder=Path.cwd() / "ai_seasons",
        no_window=True,
        file_types=(("JSON Files", "*.json"),)
    )
    if select_season_settings_file:
        if (
            sg.popup_yes_no(
                f"Confirm deletion of:\n{select_season_settings_file}",
                keep_on_top=True
            )
            == "Yes"
        ):
            # read the season file
            with open(select_season_settings_file, "r") as file:
                season_delete_info = json.loads(file.read())
            del_settings_result = _delete_file(select_season_settings_file)
            if del_settings_result:
                sg.popup("Season delete was successful!")


def _load_season_file() -> None | str:
    select_season_settings_file = sg.popup_get_file(
        "Load a Season",
        initial_folder=Path.cwd() / "ai_seasons",
        no_window=True,
        file_types=(("JSON Files", "*.json"),)
    )
    return None if not select_season_settings_file else select_season_settings_file


def _create_season_file(season_name: str, season_type: str) -> dict:
    if not os.path.exists(ai_seasons_file_path):
        logger.debug(f"Folder {ai_seasons_file_path} does not exist, creating")
        os.makedirs(ai_seasons_file_path)
    if os.path.exists(ai_seasons_file_path / f"{season_name}.json"):
        sg.Popup(
            "Warning! A season_settings file with that name already exists",
            no_titlebar=True,
        )
        return {}
    season_settings_data = {
        "season_name": season_name,
        "season_series": season_type
    }
    try:
        with open(
            ai_seasons_file_path / f"{season_name}.json", "w"
        ) as new_season_file:
            new_season_file.write(json.dumps(season_settings_data, indent=4))
    except Exception as e:
        logger.error("Unable to write file")
        return {}
    
    return season_settings_data


def _season_selection_layout() -> list[list]:
    return [
        [
            sg.Button("New Season - Real", key="--NEWREALSEASONBUTTON--", expand_x=True, expand_y=True),
            sg.Button("New Season - Custom", key="--NEWCUSTOMSEASONBUTTON--", expand_x=True, expand_y=True )
        ],
        [
            sg.Button("Load Season", key="--LOADSEASONBUTTON--", expand_x=True, expand_y=True)
        ],
        [
            sg.Button("Delete Season", key="--DELETESEASONBUTTON--", expand_x=True, expand_y=True)
        ],
        [
            sg.Button("Back", key="--BACKSEASONBUTTON--", expand_x=True, expand_y=True)
        ]
    ]


def main():
    window = sg.Window(
        "Season Selection",
        _season_selection_layout(),
        no_titlebar=False,
        finalize=True,
        size=(400,150),
        keep_on_top=True
    )
    _block_focus(window)
    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, "--BACKSEASONBUTTON--", "Cancel"):
            window.close()
            return
        if event == "--NEWREALSEASONBUTTON--":
            window.Hide()
            new_created_season = _create_new_season(None)
            if new_created_season:
                window.close()
            else:
                window.UnHide()
        if event == "--NEWCUSTOMSEASONBUTTON--":
            iracing_season_file = sg.popup_get_file(
                "Load iRacing Season",
                initial_folder=Path.home() / "Documents" / "iRacing" / "aiseasons",
                no_window=True,
                file_types=(("JSON Files", "*.json"),),
                keep_on_top=True
            )
            if iracing_season_file:
                season_settings_data = _create_season_file(season_name="test1",
                                                           season_type=_load_iracing_season(iracing_season_file))
            if season_settings_data:
                _create_new_season(None, season_settings_data.get("season_series"))
        if event == "--LOADSEASONBUTTON--":
            window.Hide()
            season_file = _load_season_file()
            if season_file:
                window.UnHide()
            else:
                window.UnHide()
        if event == "--DELETESEASONBUTTON--":
            window.Hide()
            _delete_season_file()
            window.UnHide()


if __name__ == "__main__":
    main()