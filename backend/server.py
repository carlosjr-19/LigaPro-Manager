"""
Flask Server Entry Point for ASGI compatibility with uvicorn
"""

from app import app as flask_app, db, User, bcrypt
import os

def init_database():
    """Initialize database and create default admin user"""
    with flask_app.app_context():
        # Create tables
        db.create_all()
        
        # Create default admin if not exists
        existing = User.query.filter_by(email='delegado@ligapro.com').first()
        if not existing:
            hashed = bcrypt.generate_password_hash('password123').decode('utf-8')
            admin = User(
                email='delegado@ligapro.com',
                password=hashed,
                name='Delegado Admin',
                role='owner',
                is_premium=False
            )
            db.session.add(admin)
            db.session.commit()
            print('Admin user created: delegado@ligapro.com / password123')
        else:
            print('Admin user already exists')
            
        # Run Migrations (Safe to run multiple times)
        run_migrations()
        
        print('Database initialized!')

def run_migrations():
    """Run manual migrations for schema changes"""
    from sqlalchemy import text
    try:
        with flask_app.app_context():
            with db.engine.connect() as conn:
                # Migration 1: Add show_stats to leagues
                try:
                    # Postgres/Standard SQL
                    conn.execute(text("ALTER TABLE leagues ADD COLUMN show_stats BOOLEAN DEFAULT TRUE"))
                    conn.commit()
                    print("Migration applied: show_stats column added.")
                except Exception as e:
                    # Ignore error if column likely exists
                    # print(f"Migration skipped (likely exists): {e}")
                    pass
    except Exception as e:
        print(f"Migration Error: {e}")

# Initialize database on startup
init_database()

if __name__ == '__main__':
    flask_app.run(host='0.0.0.0', port=8001, debug=True)
