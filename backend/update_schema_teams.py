import sqlite3
import os

basedir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(basedir, 'instance', 'ligapro.db')

if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
c = conn.cursor()

try:
    c.execute('ALTER TABLE teams ADD COLUMN is_deleted BOOLEAN DEFAULT 0')
    print("Added is_deleted column to teams table")
except sqlite3.OperationalError as e:
    print(f"Error (column might already exist): {e}")

conn.commit()
conn.close()
print("Database updated successfully")
