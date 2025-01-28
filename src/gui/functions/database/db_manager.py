import sqlite3
from pathlib import Path


class DatabaseManager:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(Path(db_path))
        self.cursor = self.conn.cursor()
        self.tables = self._get_db_tables()

    def _get_db_tables(self):
        try:
            return [
                table[0]
                for table in self.cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='table';"
                )
                if "sqlite" not in table[0]
            ]
        except Exception as e:
            print(e)
            return

    def _get_db_table_columns(self, table: str):
        column_names = []
        try:
            results = self.cursor.execute(f"PRAGMA table_info({table});")
            for column in results.fetchall():
                column_names.append(column[1])
            return column_names
        except Exception as e:
            print(e)
            return

    def execute_query(self, table: str, order_by: str = ""):
        results_return = []
        try:
            if order_by != "":
                results = self.cursor.execute(
                    f"SELECT * FROM {table} ORDER BY {order_by} DESC"
                )
            else:
                results = self.cursor.execute(f"SELECT * FROM {table}")
            for row in results.fetchall():
                results_return.append(list(row))
            return results_return, self._get_db_table_columns(table)
        except Exception as e:
            print(e)
            return

    def execute_select_query(
        self, table: str, condition: str, columns: str = "*"
    ) -> list[list]:
        try:
            results = self.cursor.execute(
                f"SELECT {columns} FROM {table} WHERE {condition};"
            )
            return results.fetchall()
        except Exception as e:
            print(e)
            return

    def execute_select_columns_query(
        self, table: str, columns: str = "*"
    ) -> list[list]:
        try:
            results = self.cursor.execute(f"SELECT {columns} FROM {table}")
            return results.fetchall()
        except Exception as e:
            print(e)
            return

    def delete_tables(self, tables: list):
        for table in tables:
            try:
                self.cursor.execute(f"DROP TABLE {table}")
            except Exception as e:
                print(e)
                return
