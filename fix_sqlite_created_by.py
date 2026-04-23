#!/usr/bin/env python3
"""
Fix SQLite database by adding missing created_by column to actions table
"""

import sqlite3
import os

def fix_sqlite_database():
    """Add missing created_by column to actions table in SQLite database"""
    db_path = "backend/instance/epom_dev.db"
    
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if created_by column exists
        cursor.execute("PRAGMA table_info(actions)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        print(f"Current columns in actions table: {column_names}")
        
        if 'created_by' not in column_names:
            print("Adding missing created_by column...")
            cursor.execute("ALTER TABLE actions ADD COLUMN created_by INTEGER")
            conn.commit()
            print("✅ created_by column added successfully!")
        else:
            print("✅ created_by column already exists")
        
        # Verify the column was added
        cursor.execute("PRAGMA table_info(actions)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        print(f"Updated columns in actions table: {column_names}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error fixing database: {e}")
        return False

if __name__ == "__main__":
    print("Fixing SQLite database schema...")
    if fix_sqlite_database():
        print("Database fix completed successfully!")
    else:
        print("Database fix failed!")
