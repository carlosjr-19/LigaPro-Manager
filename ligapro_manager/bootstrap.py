import sys
import os

# Add the current directory to sys.path to ensure we can import ligapro_manager
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ligapro_manager import app, init_database

if __name__ == "__main__":
    print("Starting database bootstrap...")
    try:
        init_database()
        print("Database bootstrap completed successfully.")
    except Exception as e:
        print(f"Database bootstrap failed: {e}")
        sys.exit(1)
