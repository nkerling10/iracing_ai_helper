import PySimpleGUI as sg

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

