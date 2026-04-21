from app import create_app
from models import db, User
import bcrypt
from sqlalchemy import text

def reset_database():
    app = create_app()
    with app.app_context():
        print("Dropping all tables to ensure schema sync...")
        try:
            # Disable foreign key checks for dropping tables in MySQL
            db.session.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
            db.drop_all()
            db.session.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))
            db.session.commit()
            print("Tables dropped.")
        except Exception as e:
            print(f"Error dropping tables: {e}")
            db.session.rollback()

        print("Creating all tables from current models...")
        db.create_all()
        print("Tables created.")

        print("Database reset successfully!")

if __name__ == "__main__":
    reset_database()
