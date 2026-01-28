import os
import psycopg2
from urllib.parse import urlparse

DATABASE_URL = os.environ.get('DATABASE_URL')

if not DATABASE_URL:
    print("Error: DATABASE_URL not found.")
    exit(1)

try:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    print("Migrating database schema...")
    
    # Alter teams table
    cur.execute("ALTER TABLE teams ALTER COLUMN shield_url TYPE TEXT;")
    
    conn.commit()
    cur.close()
    conn.close()
    
    print("Migration successful: 'shield_url' column changed to TEXT.")

except Exception as e:
    print(f"Migration failed: {e}")
