#!/usr/bin/env python3
"""
Direct SQLite Database Creation for e-POM
"""

import sqlite3
import os
import bcrypt
from datetime import datetime

def create_database():
    print("=== Direct SQLite Database Creation ===")
    
    # Remove existing database
    if os.path.exists('epom_dev.db'):
        os.remove('epom_dev.db')
        print("Removed existing database")
    
    # Create database connection
    conn = sqlite3.connect('epom_dev.db')
    cursor = conn.cursor()
    
    # Create users table with correct schema
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(80) UNIQUE NOT NULL,
            first_name VARCHAR(50),
            last_name VARCHAR(50),
            email VARCHAR(120) UNIQUE NOT NULL,
            password_hash VARCHAR(128) NOT NULL,
            role VARCHAR(50) DEFAULT 'Staff',
            is_active BOOLEAN DEFAULT 1,
            mfa_enabled BOOLEAN DEFAULT 0,
            mfa_secret VARCHAR(100),
            mfa_code VARCHAR(10),
            contact VARCHAR(100),
            department VARCHAR(100),
            must_change_password BOOLEAN DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("Created users table")
    
    # Create other tables (basic versions)
    cursor.execute('''
        CREATE TABLE resources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) NOT NULL,
            type VARCHAR(50) DEFAULT 'Room',
            capacity INTEGER,
            is_available BOOLEAN DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title VARCHAR(255) NOT NULL,
            description TEXT,
            start_time DATETIME NOT NULL,
            end_time DATETIME NOT NULL,
            priority VARCHAR(20) DEFAULT 'Medium',
            user_id INTEGER NOT NULL,
            mandatory_attendees TEXT,
            optional_attendees TEXT,
            resource_id INTEGER,
            location VARCHAR(255),
            meeting_link VARCHAR(512),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (resource_id) REFERENCES resources (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title VARCHAR(255) NOT NULL,
            file_path VARCHAR(500),
            status VARCHAR(50) DEFAULT 'Draft',
            category VARCHAR(50),
            uploaded_by INTEGER,
            doc_type VARCHAR(50),
            content TEXT,
            upload_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (uploaded_by) REFERENCES users (id)
        )
    ''')
    
    # Create admin user
    admin_password_hash = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    cursor.execute('''
        INSERT INTO users (
            username, first_name, last_name, email, password_hash, 
            role, is_active, must_change_password
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        'admin', 'System', 'Administrator', 'admin@epom.local', 
        admin_password_hash, 'Admin', 1, 1
    ))
    
    conn.commit()
    print("Created admin user")
    
    # Verify admin user
    cursor.execute('SELECT username, role FROM users WHERE username = ?', ('admin',))
    result = cursor.fetchone()
    if result:
        print(f"Admin user verified: {result[0]} ({result[1]})")
        print("Database created successfully!")
        print("Login credentials: admin/admin123")
    else:
        print("Admin user verification failed!")
    
    conn.close()
    return True

if __name__ == '__main__':
    create_database()
