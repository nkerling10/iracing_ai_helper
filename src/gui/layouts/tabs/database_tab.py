import PySimpleGUI as sg


class DatabaseTabLayout:
    @classmethod
    def build_db_tab_layout(cls):
        return [
            [
                sg.Button("Connect", key="-DBTABCONNECTBUTTON-", pad=(15, 15)),
                sg.Text("Connected to:"),
                sg.Text(f"", key="-DBTABCONNECTTEXT-", visible=True),
            ],
            [sg.HorizontalSeparator()],
            [
                sg.Combo(
                    values=[], pad=(15, 15), key="-DBTABCONNECTCOMBO-", visible=True, readonly=True, enable_events=True
                )
            ],
            [sg.HorizontalSeparator(key="-DBCONNECTLINE-")],
            [sg.Column(key="-DBTABLECOLUMN-", layout=[[]], expand_x=True, expand_y=True)],
        ]
