
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
    def inject_global_vars():
        # Read version from VERSION file
        app_version = "0.0.0"
        version_file = os.path.join(os.path.dirname(__file__), '..', 'VERSION')
        if os.path.exists(version_file):
            with open(version_file, 'r') as f:
                app_version = f.read().strip()
                
        return {
            'stripe_public_key': app.config.get('STRIPE_PUBLIC_KEY'),
            'app_version': app_version
        }

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
                    "ALTER TABLE leagues ADD COLUMN num_vueltas INTEGER DEFAULT 1",
                    "ALTER TABLE users ADD COLUMN color_win VARCHAR(7) DEFAULT '#22c55e'",
                    "ALTER TABLE users ADD COLUMN color_loss VARCHAR(7) DEFAULT '#ef4444'",
                    "ALTER TABLE users ADD COLUMN highlight_mode VARCHAR(20) DEFAULT 'simple'",
                    "ALTER TABLE leagues ADD COLUMN credential_color VARCHAR(10) DEFAULT '#dc2626'",
                    "ALTER TABLE leagues ADD COLUMN show_team_logos BOOLEAN DEFAULT FALSE",
                    "ALTER TABLE matches ADD COLUMN match_round INTEGER DEFAULT 1",
                    "ALTER TABLE users ADD COLUMN is_ultra BOOLEAN DEFAULT FALSE",
                    "ALTER TABLE matches ADD COLUMN referee_cost INTEGER DEFAULT 0",
                    "ALTER TABLE matches ADD COLUMN referee_cost_home INTEGER DEFAULT 0",
                    "ALTER TABLE matches ADD COLUMN referee_cost_away INTEGER DEFAULT 0",
                    "ALTER TABLE matches ALTER COLUMN referee_cost TYPE VARCHAR(50)",
                    "ALTER TABLE matches ALTER COLUMN referee_cost_home TYPE VARCHAR(50)",
                    "ALTER TABLE matches ALTER COLUMN referee_cost_away TYPE VARCHAR(50)",
                    "ALTER TABLE leagues ADD COLUMN price_per_match INTEGER DEFAULT 0",
                    "ALTER TABLE leagues ADD COLUMN price_referee INTEGER DEFAULT 0",
                    "ALTER TABLE leagues ADD COLUMN charge_from_start BOOLEAN DEFAULT TRUE",
                    "ALTER TABLE leagues ADD COLUMN charge_start_date DATE",
                    "ALTER TABLE leagues ADD COLUMN highlight_standings BOOLEAN DEFAULT FALSE",
                    "ALTER TABLE leagues ADD COLUMN highlight_start INTEGER DEFAULT 1",
                    "ALTER TABLE leagues ADD COLUMN highlight_end INTEGER DEFAULT 4",
                    "ALTER TABLE leagues ADD COLUMN highlight_color VARCHAR(10) DEFAULT '#4ade80'",
                    "ALTER TABLE courts ADD COLUMN color VARCHAR(10) DEFAULT '#22d3ee'",
                    "ALTER TABLE courts ADD COLUMN alignment VARCHAR(10) DEFAULT 'left'",
                    "ALTER TABLE leagues ADD COLUMN report_date_color VARCHAR(10) DEFAULT '#ffffff99'",
                    "ALTER TABLE leagues ADD COLUMN report_date_size INTEGER DEFAULT 14"
                ]
                
                for migration in migrations:
                    # Skip ALTER COLUMN for SQLite as it's not supported and not strictly needed for dynamic typing
                    if "ALTER COLUMN" in migration:
                        continue
                        
                    try:
                        conn.execute(text(migration))
                        conn.commit()
                        print(f"Executed migration: {migration}")
                    except Exception as e:
                        conn.rollback()
                        # Better check for already existing columns in various dialects (SQLite specifically)
                        err_str = str(e).lower()
                        if 'duplicate column name' in err_str or 'already exists' in err_str or 'duplicatecolumn' in err_str:
                            print(f"Column already exists: {migration}")
                        else:
                            print(f"Migration Error for '{migration}': {e}")

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
