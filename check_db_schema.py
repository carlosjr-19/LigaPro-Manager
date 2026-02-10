import sqlite3
import os

# Use absolute path to ensure we hit the right DB
# Based on project structure, db is likely in ligapro_manager/instance/ligapro.db or root ligapro.db
# We'll check both locations or the one defined in app.py

base_dir = os.path.dirname(os.path.abspath(__file__))
# Try common locations
paths = [
    os.path.join(base_dir, "ligapro_manager", "instance", "ligapro.db"),
    os.path.join(base_dir, "ligapro.db"),
    os.path.join(base_dir, "ligapro_manager", "ligapro.db")
]

db_path = None
for p in paths:
    if os.path.exists(p):
        db_path = p
        break

if not db_path:
    print("Could not find ligapro.db in common locations.")
    # Default to one just to try
    db_path = paths[0] 

print(f"Checking database at: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(users)")
    columns = cursor.fetchall()
    print(f"Columns in 'users' table:")
    found = False
    for col in columns:
        print(f"- {col[1]} ({col[2]})")
        if col[1] == 'is_premium':
            found = True
            
    if found:
        print("\nSUCCESS: 'is_premium' column FOUND.")
    else:
        print("\nWARNING: 'is_premium' column NOT FOUND.")
    
    conn.close()
except Exception as e:
    print(f"Error: {e}")
