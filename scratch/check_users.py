import sys
import os
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
    print(f"Checking database: {app.config['SQLALCHEMY_DATABASE_URI']}")
    users = User.query.all()
    print(f"Total users found: {len(users)}")
    for user in users:
        print(f"- ID: {user.id}, Username: {user.username}, Role: {user.role}, Active: {user.is_active}")
