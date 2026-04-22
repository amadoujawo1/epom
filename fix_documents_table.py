#!/usr/bin/env python3
"""
Fix documents table to add missing created_by column
"""

import sqlite3
import os

def fix_documents_table():
    """Add created_by column to documents table"""
    
    db_path = os.path.join(os.path.dirname(__file__), 'epom_dev.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print('=== FIXING DOCUMENTS TABLE ===')
        
        # Check if created_by column exists
        cursor.execute('PRAGMA table_info(documents)')
        columns = [row[1] for row in cursor.fetchall()]
        print(f'Documents table columns: {columns}')
        
        if 'created_by' not in columns:
            print('Adding created_by column to documents table...')
            cursor.execute('ALTER TABLE documents ADD COLUMN created_by INTEGER')
            print('created_by column added successfully')
        else:
            print('created_by column already exists')
        
        # Update existing documents to set created_by to admin user (ID 1)
        cursor.execute('UPDATE documents SET created_by = 1 WHERE created_by IS NULL')
        updated_count = cursor.rowcount
        print(f'Updated {updated_count} documents with created_by = 1')
        
        conn.commit()
        
        # Verify the fix
        cursor.execute('PRAGMA table_info(documents)')
        columns = [row[1] for row in cursor.fetchall()]
        print(f'Documents table columns after fix: {columns}')
        
        print('\n=== DOCUMENTS TABLE FIX COMPLETE ===')
        
    except Exception as e:
        print(f'Error fixing documents table: {e}')
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    fix_documents_table()
