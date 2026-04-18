import os
import sys
from dotenv import load_dotenv

# Ensure we are running from the backend directory context
# This script should be located in the 'backend' folder
load_dotenv()

from app import create_app
from models import db

app = create_app()

def initialize_database():
    with app.app_context():
        try:
            db.create_all()
            print("✓ Database tables initialized successfully.")
        except Exception as e:
            print(f"✗ Error initializing database: {e}")

if __name__ == "__main__":
    initialize_database()
