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

    print("Migration finished.")

if __name__ == "__main__":
    run_migration()
