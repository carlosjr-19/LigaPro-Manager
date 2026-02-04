from app import app, db, User, bcrypt

def create_dev_user():
    with app.app_context():
        email = 'carlosvillarroeljr@hotmail.com'
        password = 'brasil0812'
        
        # Check if user exists
        existing = User.query.filter_by(email=email).first()
        
        if existing:
            print(f"User {email} already exists.")
            # Optional: Update to ensure they are admin/premium if they already exist
            existing.role = 'admin'
            existing.is_premium = True
            db.session.commit()
            print(f"Updated {email} to have Admin role and Premium status.")
            return

        # Create new user
        hashed = bcrypt.generate_password_hash(password).decode('utf-8')
        dev_user = User(
            name='Developer',
            email=email,
            password=hashed,
            role='admin',
            is_premium=True
        )
        
        db.session.add(dev_user)
        db.session.commit()
        
        print(f"Successfully created developer user:")
        print(f"Email: {email}")
        print(f"Password: {password}")
        print(f"Role: admin")
        print(f"Premium: Yes")

if __name__ == '__main__':
    create_dev_user()
