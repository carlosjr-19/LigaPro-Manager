import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

try:
    from ligapro_manager import app, db
    from sqlalchemy import text
    
    print("App imported successfully")

    with app.app_context():
        with db.engine.connect() as conn:
            try:
                # Check if column exists first to avoid error? Or just try-except
                conn.execute(text("ALTER TABLE leagues ADD COLUMN credential_color VARCHAR(10) DEFAULT '#dc2626'"))
                conn.commit()
                print("Migration successful: Added credential_color to leagues")
            except Exception as e:
                print(f"Migration note: {e}")
                # If error contains "duplicate column name", it's fine
                
except ImportError as e:
    print(f"Import Error: {e}")
    # Try importing extensions directly if running from inside package
    try:
        from extensions import db
        print("Managed to import db from extensions, but app is missing")
    except:
        pass
