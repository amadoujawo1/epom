import sys
import os
import bcrypt
# Add root directory to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from flask import Flask
from dotenv import load_dotenv
from backend.models import db, User

# Force load .env from the backend directory relative to this script
dotenv_path = os.path.join(os.path.dirname(__file__), '..', 'backend', '.env')
load_dotenv(dotenv_path=dotenv_path)

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///epom_dev.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

with app.app_context():
    print(f"Updating admin password in {app.config['SQLALCHEMY_DATABASE_URI']}")
    admin = User.query.filter_by(username='admin').first()
    if admin:
        hashed_password = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        admin.password_hash = hashed_password
        db.session.commit()
        print("Admin password updated to 'admin123' successfully.")
    else:
        print("Admin user not found, creating it...")
        hashed_password = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        admin = User(
            username='admin',
            email='admin@digidelivery.gm',
            password_hash=hashed_password,
            role='Admin',
            is_active=True
        )
        db.session.add(admin)
        db.session.commit()
        print("Admin user created with password 'admin123'.")
