#!/usr/bin/env python3
"""
Fix missing actions table in the database
"""

import sqlite3
import os
from datetime import datetime

def fix_actions_table():
    """Create the missing actions table and other required tables"""
    
    db_path = os.path.join(os.path.dirname(__file__), 'epom_dev.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print('=== FIXING MISSING ACTIONS TABLE ===')
        
        # Check existing tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        existing_tables = [row[0] for row in cursor.fetchall()]
        print(f'Existing tables: {existing_tables}')
        
        # Create actions table if it doesn't exist
        if 'actions' not in existing_tables:
            print('Creating actions table...')
            cursor.execute('''
                CREATE TABLE actions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title VARCHAR(255) NOT NULL,
                    description TEXT,
                    status VARCHAR(50) DEFAULT 'Pending',
                    priority VARCHAR(50) DEFAULT 'Medium',
                    due_date DATETIME,
                    assigned_to INTEGER NOT NULL,
                    created_by INTEGER NOT NULL,
                    document_id INTEGER,
                    project_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (assigned_to) REFERENCES users (id),
                    FOREIGN KEY (created_by) REFERENCES users (id),
                    FOREIGN KEY (document_id) REFERENCES documents (id),
                    FOREIGN KEY (project_id) REFERENCES projects (id)
                )
            ''')
            print('Actions table created successfully')
        else:
            print('Actions table already exists')
        
        # Create projects table if it doesn't exist
        if 'projects' not in existing_tables:
            print('Creating projects table...')
            cursor.execute('''
                CREATE TABLE projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(255) NOT NULL,
                    description TEXT,
                    status VARCHAR(50) DEFAULT 'Active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            print('Projects table created successfully')
        else:
            print('Projects table already exists')
        
        # Create documents table if it doesn't exist
        if 'documents' not in existing_tables:
            print('Creating documents table...')
            cursor.execute('''
                CREATE TABLE documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title VARCHAR(255) NOT NULL,
                    content TEXT,
                    category VARCHAR(100),
                    status VARCHAR(50) DEFAULT 'Draft',
                    created_by INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (created_by) REFERENCES users (id)
                )
            ''')
            print('Documents table created successfully')
        else:
            print('Documents table already exists')
        
        # Create notifications table if it doesn't exist
        if 'notifications' not in existing_tables:
            print('Creating notifications table...')
            cursor.execute('''
                CREATE TABLE notifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    message TEXT NOT NULL,
                    link VARCHAR(255),
                    is_read BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            print('Notifications table created successfully')
        else:
            print('Notifications table already exists')
        
        # Create events table if it doesn't exist
        if 'events' not in existing_tables:
            print('Creating events table...')
            cursor.execute('''
                CREATE TABLE events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title VARCHAR(255) NOT NULL,
                    description TEXT,
                    start_time DATETIME NOT NULL,
                    end_time DATETIME NOT NULL,
                    location VARCHAR(255),
                    created_by INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (created_by) REFERENCES users (id)
                )
            ''')
            print('Events table created successfully')
        else:
            print('Events table already exists')
        
        # Create resources table if it doesn't exist
        if 'resources' not in existing_tables:
            print('Creating resources table...')
            cursor.execute('''
                CREATE TABLE resources (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title VARCHAR(255) NOT NULL,
                    description TEXT,
                    file_path VARCHAR(500),
                    category VARCHAR(100),
                    created_by INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (created_by) REFERENCES users (id)
                )
            ''')
            print('Resources table created successfully')
        else:
            print('Resources table already exists')
        
        # Create attendance_records table if it doesn't exist
        if 'attendance_records' not in existing_tables:
            print('Creating attendance_records table...')
            cursor.execute('''
                CREATE TABLE attendance_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    event_id INTEGER NOT NULL,
                    status VARCHAR(50) DEFAULT 'Present',
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (event_id) REFERENCES events (id)
                )
            ''')
            print('Attendance_records table created successfully')
        else:
            print('Attendance_records table already exists')
        
        # Create document_audits table if it doesn't exist
        if 'document_audits' not in existing_tables:
            print('Creating document_audits table...')
            cursor.execute('''
                CREATE TABLE document_audits (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    document_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    action VARCHAR(100) NOT NULL,
                    details TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (document_id) REFERENCES documents (id),
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            print('Document_audits table created successfully')
        else:
            print('Document_audits table already exists')
        
        # Add some sample data for testing
        print('\nAdding sample data...')
        
        # Add sample projects
        cursor.execute('SELECT COUNT(*) FROM projects')
        project_count = cursor.fetchone()[0]
        if project_count == 0:
            cursor.execute('''
                INSERT INTO projects (name, description) VALUES 
                ('Health Sector Reform', 'Comprehensive healthcare system improvement initiative'),
                ('Digital Transformation', 'Modernization of government digital services'),
                ('Infrastructure Development', 'National infrastructure upgrade program')
            ''')
            print('Sample projects added')
        
        # Add sample documents
        cursor.execute('SELECT COUNT(*) FROM documents')
        doc_count = cursor.fetchone()[0]
        if doc_count == 0:
            cursor.execute('''
                INSERT INTO documents (title, content, category, created_by) VALUES 
                ('Q1 Strategic Briefing', 'Summary of Q1 achievements and challenges', 'Minister Briefings', 1),
                ('Digital Policy Memo', 'Policy recommendations for digital transformation', 'Decision Memos', 1)
            ''')
            print('Sample documents added')
        
        # Add sample events
        cursor.execute('SELECT COUNT(*) FROM events')
        event_count = cursor.fetchone()[0]
        if event_count == 0:
            cursor.execute('''
                INSERT INTO events (title, description, start_time, end_time, location, created_by) VALUES 
                ('Cabinet Meeting', 'Weekly cabinet meeting to discuss strategic initiatives', '2026-04-23 09:00:00', '2026-04-23 11:00:00', 'Conference Room A', 1),
                ('Strategy Session', 'Quarterly strategy planning session', '2026-04-24 14:00:00', '2026-04-24 16:00:00', 'Executive Office', 1)
            ''')
            print('Sample events added')
        
        conn.commit()
        
        # Verify all tables were created
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        all_tables = [row[0] for row in cursor.fetchall()]
        print(f'\nAll tables after fix: {all_tables}')
        
        print('\n=== ACTIONS TABLE FIX COMPLETE ===')
        print('? The Register New Directive / Decision form should now work properly')
        
    except Exception as e:
        print(f'Error fixing database: {e}')
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    fix_actions_table()
