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
    user = User.query.filter_by(username='admin').first()
    if user:
        is_match = bcrypt.checkpw('admin123'.encode('utf-8'), user.password_hash.encode('utf-8'))
        print(f"Password 'admin123' for user 'admin' matches: {is_match}")
    else:
        print("User 'admin' not found.")
