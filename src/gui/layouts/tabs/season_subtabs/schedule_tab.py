import PySimpleGUI as sg

class ScheduleTabLayout:
    @staticmethod
    def _season_file_headers() -> list:
        return ["Week", "Track", "Laps", "Results"]

    @classmethod
    def build_schedule_tab_layout(cls, season_data: list = []) -> list[list]:
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
                    hide_vertical_scroll = True,
                    enable_click_events = True,
                    enable_events=True,
                    starting_row_number=1
                )
            ]
        ]
