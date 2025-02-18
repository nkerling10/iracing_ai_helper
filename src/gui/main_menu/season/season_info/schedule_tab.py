import PySimpleGUI as sg

def _color_table_rows(season_data) -> tuple[list, list]:
    """
    Loads data from a season json file, assembles it into displayable format with custom
    row colors for the next race, completed races, and non-completed races.
    """
    colored_rows = []
    next_race = [next(x[0] - 1 for x in season_data if x[3] is False)]
    done_races = [
        ([x[0] - 1], "white", "green") for x in season_data if x[3] is True
    ]
    not_done_races = [
        ([x[0] - 1], "white", "red")
        for x in season_data
        if x[3] is False and x[0] - 1 != next_race
    ]
    for each in not_done_races:
        colored_rows.append(each)
    for each in done_races:
        colored_rows.append(each)
    colored_rows.append((next_race, "white", "orange"))

    return colored_rows

class ScheduleTabLayout:
    @staticmethod
    def _season_file_headers() -> list:
        return ["Week", "Track", "Laps", "Results"]

    @classmethod
    def build_schedule_tab_layout(cls, season_data: list) -> list[list]:
        return [
            [
                sg.Table(
                    values=season_data,
                    headings=cls._season_file_headers(),
                    justification="center",
                    key="-SCHEDULETABLE-",
                    num_rows=34,
                    expand_x=True,
                    expand_y=True,
                    hide_vertical_scroll=True,
                    enable_click_events=True,
                    enable_events=True,
                    starting_row_number=1,
                    row_colors=_color_table_rows(season_data)
                )
            ]
        ]
