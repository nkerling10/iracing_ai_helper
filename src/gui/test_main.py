## THIS FILE IS HERE TO TEST OUT ANY FUNCTIONALITY
## THAT REQUIRES SOME SEPERATION :)

import sqlite3
from functions.database.db_manager import DatabaseManager
from pathlib import Path

try:
    db = DatabaseManager(Path("C:\\Users\\Nick\\Documents\\iracing_ai_helper\\database\\iracing_ai_helper.db"))
except Exception as e:
    print(e)

column_names = []

results = db.cursor.execute("PRAGMA table_info(CAR);")
for column in results.fetchall():
    column_names.append(column[1])
print(column_names)
db.conn.close()