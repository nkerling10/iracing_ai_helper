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
                for table in self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
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

    def execute_query(self, table: str):
        results_return = []
        try:
            results = self.cursor.execute(f"SELECT * FROM {table}")
            for row in results.fetchall():
                results_return.append(list(row))
            return results_return, self._get_db_table_columns(table)
        except Exception as e:
            print(e)
            return
