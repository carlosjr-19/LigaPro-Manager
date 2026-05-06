import sqlite3
import os

db_paths = [
    'ligapro_manager/instance/ligafutbol.db',
    'ligapro_manager/instance/ligapro.db'
]

for db_path in db_paths:
    if os.path.exists(db_path):
        print(f"Updating {db_path}...")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("ALTER TABLE leagues ADD COLUMN enable_player_limit BOOLEAN DEFAULT 0;")
            print("Added enable_player_limit")
        except sqlite3.OperationalError as e:
            print(f"Column might exist or error: {e}")
            
        try:
            cursor.execute("ALTER TABLE leagues ADD COLUMN max_players_per_team INTEGER;")
            print("Added max_players_per_team")
        except sqlite3.OperationalError as e:
            print(f"Column might exist or error: {e}")
            
        conn.commit()
        conn.close()
        print(f"Finished {db_path}\n")
    else:
        print(f"DB not found: {db_path}")

