import PySimpleGUI as sg

class LoggingTabLayout:
    @staticmethod
    def _build_logging_tab_layout() -> list[list]:
        return [
            [
                sg.Multiline(
                    key="-LOGGINGBOX-",
                    write_only=True,
                    auto_refresh=True,
                    autoscroll_only_at_bottom = True,
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
