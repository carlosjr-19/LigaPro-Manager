from app import app, db
from sqlalchemy import text

def run_migration():
    print("Starting database migration...")
    
    with app.app_context():
        # Define the column types based on the database engine
        # In this simple case, TEXT and VARCHAR are compatible enough or we use generic types
        # But raw SQL is often easiest for simple ADD COLUMN if we catch errors
        
        commands = [
            "ALTER TABLE leagues ADD COLUMN logo_url TEXT",
            "ALTER TABLE leagues ADD COLUMN slogan VARCHAR(255)"
        ]
        
        with db.engine.connect() as conn:
            for clean_command in commands:
                try:
                    conn.execute(text(clean_command))
                    conn.commit()
                    print(f"Executed: {clean_command}")
                except Exception as e:
                    # Catching error if column already exists
                    # The error message varies by DB (sqlite vs postgres), so we print it but don't crash
                    print(f"Skipped (might already exist): {clean_command}")
                    print(f"Details: {e}")

    print("Migration completed.")

if __name__ == "__main__":
    run_migration()
