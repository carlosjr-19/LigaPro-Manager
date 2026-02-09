from app import app, db
from sqlalchemy import text, inspect

def run_migration():
    print("Starting database migration...")
    
    with app.app_context():
        inspector = inspect(db.engine)
        
        # Check if table exists
        if not inspector.has_table("leagues"):
            print("Table 'leagues' not found. Skipping.")
            return

        # Get existing columns
        columns = [c['name'] for c in inspector.get_columns('leagues')]
        print(f"Existing columns: {columns}")

        with db.engine.connect() as conn:
            # 1. Add logo_url if not exists
            if 'logo_url' not in columns:
                try:
                    print("Adding logo_url column...")
                    conn.execute(text("ALTER TABLE leagues ADD COLUMN logo_url TEXT"))
                    conn.commit()
                    print("Success: logo_url added.")
                except Exception as e:
                    print(f"Error adding logo_url: {e}")
            else:
                print("Skipped: logo_url already exists.")
            
            # 2. Add slogan if not exists
            if 'slogan' not in columns:
                try:
                    print("Adding slogan column...")
                    conn.execute(text("ALTER TABLE leagues ADD COLUMN slogan VARCHAR(255)"))
                    conn.commit()
                    print("Success: slogan added.")
                except Exception as e:
                    print(f"Error adding slogan: {e}")
            else:
                print("Skipped: slogan already exists.")

            # 3. Add teams.is_deleted if not exists
            if inspector.has_table("teams"):
                team_columns = [c['name'] for c in inspector.get_columns('teams')]
                if 'is_deleted' not in team_columns:
                    try:
                        print("Adding teams.is_deleted column...")
                        conn.execute(text("ALTER TABLE teams ADD COLUMN is_deleted BOOLEAN DEFAULT FALSE"))
                        conn.commit()
                        print("Success: teams.is_deleted added.")
                    except Exception as e:
                        print(f"Error adding teams.is_deleted: {e}")
                else:
                    print("Skipped: teams.is_deleted already exists.")

    print("Migration finished.")

if __name__ == "__main__":
    run_migration()
