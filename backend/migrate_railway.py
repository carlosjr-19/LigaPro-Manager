import sqlite3
import os
import uuid
from datetime import datetime, timezone

# Database path
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'instance', 'ligapro.db')

def migrate():
    print(f"Starting migration on database: {db_path}")
    
    if not os.path.exists(db_path):
        print("Database not found! Ensure the volume is mounted correctly or the app has initialized it.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # --- 1. Teams: Add is_deleted column ---
        print("\n[1/3] Checking 'teams' table schema...")
        cursor.execute("PRAGMA table_info(teams)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if 'is_deleted' not in columns:
            print("  -> Adding 'is_deleted' column...")
            cursor.execute('ALTER TABLE teams ADD COLUMN is_deleted BOOLEAN DEFAULT 0')
        else:
            print("  -> 'is_deleted' column already exists.")

        # --- 2. Courts: Create table ---
        print("\n[2/3] Checking 'courts' table...")
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS courts (
            id VARCHAR(36) PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            league_id VARCHAR(36) NOT NULL,
            created_at DATETIME,
            FOREIGN KEY(league_id) REFERENCES leagues(id)
        )
        ''')
        print("  -> 'courts' table ensured.")

        # --- 3. Matches: Add court_id column ---
        print("\n[3/3] Checking 'matches' table schema...")
        cursor.execute("PRAGMA table_info(matches)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if 'court_id' not in columns:
            print("  -> Adding 'court_id' column...")
            cursor.execute('ALTER TABLE matches ADD COLUMN court_id VARCHAR(36) REFERENCES courts(id)')
        else:
            print("  -> 'court_id' column already exists.")

        # --- 4. Data Migration: Create Default Courts ---
        print("\n[4/4] Migrating existing data (Default Courts)...")
        cursor.execute("SELECT id, name FROM leagues")
        leagues = cursor.fetchall()
        
        migrated_count = 0
        for league_id, league_name in leagues:
            cursor.execute("SELECT count(*) FROM courts WHERE league_id = ?", (league_id,))
            court_count = cursor.fetchone()[0]
            
            if court_count == 0:
                print(f"  -> Creating default court for league '{league_name}'...")
                default_court_id = str(uuid.uuid4())
                cursor.execute(
                    "INSERT INTO courts (id, name, league_id, created_at) VALUES (?, ?, ?, ?)",
                    (default_court_id, "Cancha Principal", league_id, datetime.now(timezone.utc))
                )
                
                # Assign existing matches
                cursor.execute(
                    "UPDATE matches SET court_id = ? WHERE league_id = ? AND court_id IS NULL",
                    (default_court_id, league_id)
                )
                migrated_count += 1
        
        if migrated_count == 0:
            print("  -> No leagues needed migration.")
        else:
            print(f"  -> Migrated {migrated_count} leagues.")

        conn.commit()
        print("\nMigration completed successfully!")

    except Exception as e:
        print(f"\nERROR during migration: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    migrate()
