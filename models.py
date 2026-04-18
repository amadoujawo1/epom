from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=True)
    last_name = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(50), default='Staff') # Admin, Staff, Leader
    is_active = db.Column(db.Boolean, default=True)
    mfa_enabled = db.Column(db.Boolean, default=False)
    mfa_secret = db.Column(db.String(100), nullable=True)
    mfa_code = db.Column(db.String(10), nullable=True)
    contact = db.Column(db.String(100), nullable=True)
    department = db.Column(db.String(100), nullable=True)
    must_change_password = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class Resource(db.Model):
    __tablename__ = 'resources'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), default='Room') # Room, Vehicle, Equipment
    capacity = db.Column(db.Integer, nullable=True)
    is_available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    start_time = db.Column(db.DateTime(timezone=True), nullable=False)
    end_time = db.Column(db.DateTime(timezone=True), nullable=False)
    priority = db.Column(db.String(20), default='Medium') # High, Medium, Low
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    mandatory_attendees = db.Column(db.Text, nullable=True) 
    optional_attendees = db.Column(db.Text, nullable=True)
    resource_id = db.Column(db.Integer, db.ForeignKey('resources.id'), nullable=True)
    location = db.Column(db.String(255), nullable=True)
    meeting_link = db.Column(db.String(512), nullable=True) 
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class Document(db.Model):
    __tablename__ = 'documents'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=True)
    file_path = db.Column(db.String(500), nullable=True)
    doc_type = db.Column(db.String(50), default='text') # text, pdf, image
    category = db.Column(db.String(50), default='General') # General, Restricted, Confidential
    status = db.Column(db.String(20), default='Draft') # Draft, Published, Archived
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class DocumentAudit(db.Model):
    __tablename__ = 'document_audits'
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(50), default='viewed') # viewed, downloaded, edited, deleted
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class Action(db.Model):
    __tablename__ = 'actions'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='Pending') # Pending, In Progress, Completed
    priority = db.Column(db.String(20), default='Medium') # High, Medium, Low
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    due_date = db.Column(db.DateTime(timezone=True), nullable=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id'), nullable=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class Project(db.Model):
    __tablename__ = 'projects'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='Active') # Active, Completed, On Hold
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    link = db.Column(db.String(255), nullable=True)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class AttendanceRecord(db.Model):
    __tablename__ = 'attendance_records'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.String(10), nullable=False) # YYYY-MM-DD
    clock_in_time = db.Column(db.DateTime(timezone=True), nullable=False)
    clock_out_time = db.Column(db.DateTime(timezone=True), nullable=True)
    status = db.Column(db.String(20), default='Present') # Present, Absent, Late
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
