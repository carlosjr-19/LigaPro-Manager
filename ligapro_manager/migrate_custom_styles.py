import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'instance', 'ligapro.db')

def migrate():
    print(f"Migrating database at: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if users already has can_custom_role_style
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'can_custom_role_style' not in columns:
            print("Adding can_custom_role_style to users table...")
            cursor.execute("ALTER TABLE users ADD COLUMN can_custom_role_style BOOLEAN DEFAULT 0")
        else:
            print("can_custom_role_style already exists in users.")

        # Check if leagues already has custom_role_style
        cursor.execute("PRAGMA table_info(leagues)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'custom_role_style' not in columns:
            print("Adding custom_role_style to leagues table...")
            cursor.execute("ALTER TABLE leagues ADD COLUMN custom_role_style VARCHAR(50) DEFAULT NULL")
        else:
            print("custom_role_style already exists in leagues.")
            
        conn.commit()
        print("Migration successful.")
    except Exception as e:
        print(f"Error during migration: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    migrate()
