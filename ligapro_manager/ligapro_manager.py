
from flask import Flask, render_template
from extensions import db, bcrypt, login_manager
from routes import register_blueprints
from config import Config
from models import User
import stripe
import os

def create_app(config_class=Config):
    # Initialize Flask app
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Stripe API Key
    if app.config.get('STRIPE_SECRET_KEY'):
        stripe.api_key = app.config['STRIPE_SECRET_KEY']

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    # Register Blueprints
    register_blueprints(app)

    # Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('500.html'), 500
        
    # Context Processor for Global Variables
    @app.context_processor
    def inject_stripe_key():
        return {'stripe_public_key': app.config.get('STRIPE_PUBLIC_KEY')}

    return app

app = create_app()

# Database Initialization Logic (from server.py)
def init_database():
    """Initialize database and create default admin user"""
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Run Migrations FIRST to ensure schema is up to date
        run_migrations()
        
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
            
        print('Database initialized!')

def run_migrations():
    """Run manual migrations for schema changes"""
    from sqlalchemy import text
    try:
        with app.app_context():
            with db.engine.connect() as conn:
                # Add migrations as needed
                migrations = [
                    "ALTER TABLE leagues ADD COLUMN show_stats BOOLEAN DEFAULT TRUE",
                    "ALTER TABLE leagues ADD COLUMN logo_url TEXT",
                    "ALTER TABLE leagues ADD COLUMN slogan VARCHAR(255)",
                    "ALTER TABLE teams ADD COLUMN is_deleted BOOLEAN DEFAULT FALSE",
                    "ALTER TABLE teams ADD COLUMN is_hidden BOOLEAN DEFAULT FALSE",
                    "ALTER TABLE teams ADD COLUMN is_hidden BOOLEAN DEFAULT FALSE",
                    "ALTER TABLE leagues ADD COLUMN num_vueltas INTEGER DEFAULT 1",
                    "ALTER TABLE users ADD COLUMN color_win VARCHAR(7) DEFAULT '#22c55e'",
                    "ALTER TABLE users ADD COLUMN color_loss VARCHAR(7) DEFAULT '#ef4444'",
                    "ALTER TABLE users ADD COLUMN highlight_mode VARCHAR(20) DEFAULT 'simple'"
                ]
                
                for migration in migrations:
                    try:
                        conn.execute(text(migration))
                        conn.commit()
                        print(f"Executed migration: {migration}")
                    except Exception as e:
                        conn.rollback()
                        # Only ignore if column already exists (DuplicateColumn)
                        if 'DuplicateColumn' in str(e) or 'already exists' in str(e):
                            print(f"Column already exists: {migration}")
                        else:
                            print(f"Migration Error for '{migration}': {e}")
                            # Optional: Fail if critical? For now just log.

    except Exception as e:
        print(f"Migration Setup Error: {e}")

# CLI Commands
@app.cli.command("init-db")
def init_db_command():
    """Clear existing data and create new tables."""
    db.create_all()
    print("Initialized the database.")

# Initialize on startup
if __name__ == '__main__':
    init_database()
    app.run(host='0.0.0.0', port=8001, debug=True)
