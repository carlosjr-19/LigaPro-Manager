import sys
import os

# Add ligapro_manager subdirectory to path PREPENDED
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(current_dir, 'ligapro_manager'))

print(f"Running from: {current_dir}")
print(f"Sys path inserted: {os.path.join(current_dir, 'ligapro_manager')}")

try:
    # Now valid to import modules inside ligapro_manager/ directly
    from ligapro_manager import app, db
    from sqlalchemy import text
    
    print("App imported successfully")

    with app.app_context():
        with db.engine.connect() as conn:
            try:
                conn.execute(text("ALTER TABLE leagues ADD COLUMN credential_color VARCHAR(10) DEFAULT '#dc2626'"))
                conn.commit()
                print("Migration successful: Added credential_color to leagues")
            except Exception as e:
                print(f"Migration note: {e}")
                
except ImportError as e:
    print(f"Import Error: {e}")
    import traceback
    traceback.print_exc()
