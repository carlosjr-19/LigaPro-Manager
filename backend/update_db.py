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
    c.execute('ALTER TABLE leagues ADD COLUMN logo_url TEXT')
    print("Added logo_url column")
except sqlite3.OperationalError:
    print("logo_url column already exists")

try:
    c.execute('ALTER TABLE leagues ADD COLUMN slogan VARCHAR(255)')
    print("Added slogan column")
except sqlite3.OperationalError:
    print("slogan column already exists")

try:
    c.execute('ALTER TABLE leagues ADD COLUMN playoff_type VARCHAR(20)')
    print("Added playoff_type column")
except sqlite3.OperationalError:
    print("playoff_type column already exists")

conn.commit()
conn.close()
print("Database updated successfully")
