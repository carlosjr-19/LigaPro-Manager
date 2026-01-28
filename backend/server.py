"""
Flask Server Entry Point for ASGI compatibility with uvicorn
"""

from app import app as flask_app, db, User, bcrypt
from asgiref.wsgi import WsgiToAsgi
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
        
        print('Database initialized!')

# Initialize database on startup
init_database()

# Create ASGI wrapper for uvicorn
app = WsgiToAsgi(flask_app)

if __name__ == '__main__':
    flask_app.run(host='0.0.0.0', port=8001, debug=True)
