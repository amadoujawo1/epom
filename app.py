# e-POM Tactical Enterprise Node - v2.1.0-MYSQL
import os
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import bcrypt
from datetime import datetime, timezone
from werkzeug.utils import secure_filename
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding

# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__, static_folder='frontend/dist', static_url_path='')
    CORS(app)  # Enable CORS for all routes

    # Database configuration - Force SQLite for Railway to bypass PostgreSQL issues completely
    print("🔗 Forcing SQLite database for Railway deployment")
    
    # Clear any Railway DATABASE_URL environment variable
    if "DATABASE_URL" in os.environ:
        del os.environ["DATABASE_URL"]
        print("🗑️  Cleared Railway DATABASE_URL environment variable")
    
    # Force SQLite regardless of environment variables
    database_url = "sqlite:///epom_dev.db"
    
    print(f"🔗 Database URL: {database_url}")
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "fallback-jwt-secret")
    
    # Initialize extensions
    from models import db, User, Event, Document, Action
    db.init_app(app)
    jwt = JWTManager(app)

    with app.app_context():
        # Initialize database tables if they don't exist
        try:
            print("🔧 Initializing database...")
            
            # Force table creation with explicit metadata
            db.metadata.create_all(db.engine)
            print("✅ Tables created with metadata!")
            
            # Also try create_all as backup
            db.create_all()
            print("✅ Tables created with create_all!")
            
            # Create default admin user if not exists
            admin_user = User.query.filter_by(username='admin').first()
            if not admin_user:
                print("Creating default admin user...")
                admin_user = User(
                    username='admin',
                    email='admin@epom.local',
                    first_name='System',
                    last_name='Administrator',
                    role='Admin',
                    is_active=True,
                    must_change_password=True
                )
                admin_user.password_hash = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                db.session.add(admin_user)
                db.session.commit()
                print("✅ Default admin user created! Username: admin, Password: admin123")
                
                # Verify admin user was created
                verify_user = User.query.filter_by(username='admin').first()
                if verify_user:
                    print(f"✅ Admin user verified: {verify_user.username}")
                else:
                    print("❌ ERROR: Admin user verification failed!")
            else:
                print("✅ Admin user already exists")
                
            # List all tables to confirm creation
            inspector = db.inspect(db.engine)
            existing_tables = inspector.get_table_names()
            print(f"✅ Database tables verified: {existing_tables}")
            
        except Exception as e:
            print(f"❌ Database initialization error: {str(e)}")
            import traceback
            traceback.print_exc()

    # Debugging: Log the database URL being used
    print(f"Using database: {app.config['SQLALCHEMY_DATABASE_URI']}")

    @app.route('/api/health', methods=['GET'])
    def health_check():
        try:
            # Ensure database tables exist
            db.create_all()
            print("✅ Health check: Database tables ensured")
            
            # Check if admin user exists
            admin_user = User.query.filter_by(username='admin').first()
            if not admin_user:
                print("Creating admin user from health check...")
                admin_user = User(
                    username='admin',
                    email='admin@epom.local',
                    first_name='System',
                    last_name='Administrator',
                    role='Admin',
                    is_active=True,
                    must_change_password=True
                )
                admin_user.password_hash = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                db.session.add(admin_user)
                db.session.commit()
                print("✅ Admin user created from health check")
            
            return jsonify({
                "status": "success", 
                "message": "e-POM Backend is running!",
                "api_version": "v2.2.0-MOBILE-READY",
                "environment": "Operational",
                "database": "connected"
            })
        except Exception as e:
            print(f"❌ Health check error: {str(e)}")
            return jsonify({
                "status": "error", 
                "message": f"Database setup failed: {str(e)}",
                "api_version": "v2.2.0-MOBILE-READY",
                "environment": "Error"
            }), 500

    @app.route('/api/test-db', methods=['GET'])
    def test_database_connection():
        try:
            print("Testing database connection...")
            
            # Test basic database connection
            result = db.engine.execute("SELECT 1")
            print("Database connection successful!")
            
            # Check if tables exist
            inspector = db.inspect(db.engine)
            existing_tables = inspector.get_table_names()
            print(f"Existing tables: {existing_tables}")
            
            # Check database URL
            print(f"Database URL: {app.config['SQLALCHEMY_DATABASE_URI']}")
            
            return jsonify({
                "status": "success",
                "message": "Database connection working",
                "database_url": app.config['SQLALCHEMY_DATABASE_URI'],
                "existing_tables": existing_tables,
                "connection_test": "PASSED"
            })
        except Exception as e:
            print(f"Database connection test failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({
                "status": "error",
                "message": f"Database connection failed: {str(e)}",
                "database_url": app.config.get('SQLALCHEMY_DATABASE_URI', 'NOT_SET'),
                "connection_test": "FAILED"
            }), 500

    @app.route('/api/setup-database', methods=['POST'])
    def setup_database():
        try:
            print("Manually database setup initiated...")
            
            # Debug: Check database connection
            print(f"Database URL: {app.config['SQLALCHEMY_DATABASE_URI']}")
            
            # Import all models to ensure they're registered
            from models import User, Event, Document, Action, Project, Notification, Resource, AttendanceRecord, DocumentAudit
            
            print("Models imported successfully!")
            
            # Force table creation with explicit metadata
            print("Creating tables with explicit metadata...")
            db.metadata.create_all(db.engine)
            print("Tables created with metadata!")
            
            # Also try create_all as backup
            db.create_all()
            print("Tables created with create_all!")
            
            # Create admin user
            admin_user = User.query.filter_by(username='admin').first()
            if not admin_user:
                print("Creating admin user...")
                admin_user = User(
                    username='admin',
                    email='admin@epom.local',
                    first_name='System',
                    last_name='Administrator',
                    role='Admin',
                    is_active=True,
                    must_change_password=True
                )
                admin_user.password_hash = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                db.session.add(admin_user)
                db.session.commit()
                print("Admin user created!")
                
                # Verify admin user was created
                verify_user = User.query.filter_by(username='admin').first()
                if verify_user:
                    print(f"Admin user verified: {verify_user.username}")
                else:
                    print("ERROR: Admin user verification failed!")
                
                return jsonify({
                    "status": "success",
                    "message": "Database setup completed!",
                    "admin_user": {
                        "username": "admin",
                        "password": "admin123"
                    },
                    "tables_created": [table.name for table in db.metadata.tables.keys()]
                })
            else:
                print("Admin user already exists")
                return jsonify({
                    "status": "success",
                    "message": "Database already initialized",
                    "tables": [table.name for table in db.metadata.tables.keys()]
                })
        except Exception as e:
            print(f"Database setup error: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({
                "status": "error",
                "message": f"Database setup failed: {str(e)}",
                "database_url": app.config['SQLALCHEMY_DATABASE_URI']
            }), 500

    # --- TACTICAL THIRD-PARTY INTEGRATION (EMAIL) ---
    class TacticalMailer:
        @staticmethod
        def send(subject, recipient, body, priority="Normal"):
            # Simulation of SMTP dispatch for mobile/web stakeholders
            # In production: from flask_mail import Message, mail; mail.send(Message(...))
            log_time = datetime.now(timezone.utc).strftime('%H:%M:%S')
            print(f"\n[TACTICAL DISPATCH] {log_time} | Priority: {priority}")
            print(f"TO: {recipient}")
            print(f"SUBJECT: {subject}")
            print(f"CONTENT: {body}\n")
            return True

    # AES 256 Encryption Helpers
    def get_encryption_key():
        key = os.getenv("ENCRYPTION_KEY", "0123456789abcdef0123456789abcdef") # 32 bytes for AES 256
        return key.encode('utf-8')[:32]

    def encrypt_data(data: bytes):
        key = get_encryption_key()
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(data) + padder.finalize()
        
        encrypted_content = encryptor.update(padded_data) + encryptor.finalize()
        return encrypted_content, base64.b64encode(iv).decode('utf-8')

    def decrypt_data(encrypted_content: bytes, iv_b64: str):
        key = get_encryption_key()
        iv = base64.b64decode(iv_b64)
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        
        decrypted_padded_data = decryptor.update(encrypted_content) + decryptor.finalize()
        
        unpadder = padding.PKCS7(128).unpadder()
        data = unpadder.update(decrypted_padded_data) + unpadder.finalize()
        return data

    # --- MIDDLEWARES/HELPERS ---
    def role_required(required_role):
        def decorator(fn):
            def wrapper(*args, **kwargs):
                current_user_id = get_jwt_identity()
                # JWT identity was stored as a string, but the ID in the DB is an integer
                user = db.session.get(User, int(current_user_id))
                # Administrators have master access to all role-protected features
                if not user or (user.role != required_role and user.role != 'Admin'):
                    return jsonify({"error": "Unauthorized role-based access"}), 403
                return fn(*args, **kwargs)
            wrapper.__name__ = fn.__name__
            return wrapper
        return decorator

    # --- AUTH ROUTES ---
    @app.route('/api/auth/register', methods=['POST'])
    def register():
        data = request.json
        print("Registration Request Data:", data)
        if not data or not data.get('username') or not data.get('email') or not data.get('password'):
            return jsonify({"error": "Missing required fields"}), 400
        
        if User.query.filter_by(username=data['username']).first() or User.query.filter_by(email=data['email']).first():
            return jsonify({"error": "User already exists"}), 400
            
        hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Check if this is the first user; if so, make them an Admin
        is_first_user = User.query.first() is None
        role = 'Admin' if is_first_user else data.get('role', 'Staff')

        new_user = User(
            username=data['username'],
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            email=data['email'].lower(),
            password_hash=hashed_password,
            role=role,
            department=data.get('department')
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({"message": "User registered successfully"}), 201

    @app.route('/api/auth/login', methods=['POST'])
    def login():
        try:
            # Ensure database tables exist
            try:
                db.create_all()
                print("✅ Database tables ensured to exist")
            except Exception as db_error:
                print(f"⚠️ Database table creation error: {db_error}")
            
            # Create admin user if not exists
            try:
                admin_user = User.query.filter_by(username='admin').first()
                if not admin_user:
                    print("Creating default admin user...")
                    admin_user = User(
                        username='admin',
                        email='admin@epom.local',
                        first_name='System',
                        last_name='Administrator',
                        role='Admin',
                        is_active=True,
                        must_change_password=True
                    )
                    admin_user.password_hash = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                    db.session.add(admin_user)
                    db.session.commit()
                    print("✅ Default admin user created!")
            except Exception as admin_error:
                print(f"⚠️ Admin user creation error: {admin_error}")
            
            data = request.json
            user = User.query.filter_by(username=data.get('username')).first()

            if not user or not bcrypt.checkpw(data.get('password', '').encode('utf-8'), user.password_hash.encode('utf-8')):
                return jsonify({"error": "Invalid credentials"}), 401

            if not user.is_active:
                return jsonify({"error": "This account has been deactivated. Contact Admin."}), 403

            if user.mfa_enabled:
                # Generate a temporary OTP for this demo (in real app, send via email/SMS)
                user.mfa_code = "123456" # Hardcoded for demo, normally os.urandom
                db.session.commit()
                return jsonify({
                    "mfa_required": True,
                    "user_id": user.id,
                    "message": "MFA Challenge: Enter the 6-digit code sent to your tactical device (Demo: 123456)"
                }), 200

            access_token = create_access_token(identity=str(user.id))
            return jsonify({
                "token": access_token, 
                "user": {
                    "id": user.id, 
                    "username": user.username, 
                    "role": user.role, 
                    "email": user.email, 
                    "first_name": user.first_name, 
                    "last_name": user.last_name,
                    "must_change_password": user.must_change_password
                }
            }), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/api/auth/mfa/verify', methods=['POST'])
    def mfa_verify():
        from models import User, db
        data = request.json
        user_id = data.get('user_id')
        code = data.get('code')
        
        user = db.session.get(User, int(user_id))
        if not user or user.mfa_code != code:
            return jsonify({"error": "Invalid MFA code"}), 401
            
        # Clear code after use
        user.mfa_code = None
        db.session.commit()
        
        access_token = create_access_token(identity=str(user.id))
        return jsonify({
            "token": access_token, 
            "user": {
                "id": user.id, 
                "username": user.username, 
                "role": user.role, 
                "email": user.email, 
                "first_name": user.first_name, 
                "last_name": user.last_name,
                "department": user.department,
                "must_change_password": user.must_change_password
            }
        }), 200


    @app.route('/api/users', methods=['GET'])
    @jwt_required()
    def get_users():
        # Accessible to all users so they can see colleagues for task assignments
        users = User.query.all()
        return jsonify([{"id": u.id, "username": u.username, "first_name": u.first_name, "last_name": u.last_name, "role": u.role, "email": u.email, "is_active": u.is_active, "department": u.department} for u in users]), 200

    @app.route('/api/users/<int:user_id>/status', methods=['PUT'])
    @jwt_required()
    @role_required('Admin')
    def update_user_status(user_id):
        # Admin can disable/enable users
        user = db.session.get(User, user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404
        data = request.json
        if 'is_active' in data:
            user.is_active = data['is_active']
        db.session.commit()
        return jsonify({"message": f"User {'enabled' if user.is_active else 'disabled'} successfully"}), 200

    @app.route('/api/users/<int:user_id>', methods=['PUT'])
    @jwt_required()
    def update_user(user_id):
        # Admin can update user details, or user can update their own details
        current_user_id = int(get_jwt_identity())
        current_user = db.session.get(User, current_user_id)
        
        if current_user.role != 'Admin' and current_user_id != user_id:
            return jsonify({"error": "Unauthorized"}), 403

        user = db.session.get(User, user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404
        data = request.json
        
        if 'username' in data:
            # Check if username is already taken by another user
            existing = User.query.filter_by(username=data['username']).first()
            if existing and existing.id != user_id:
                return jsonify({"error": "Username already exists"}), 400
            user.username = data['username']
            
        if 'email' in data:
            # Check if email is already taken by another user
            email_lower = data['email'].lower()
            existing = User.query.filter_by(email=email_lower).first()
            if existing and existing.id != user_id:
                return jsonify({"error": "Email already exists"}), 400
            user.email = email_lower
            
        if 'first_name' in data:
            user.first_name = data['first_name']
            
        if 'last_name' in data:
            user.last_name = data['last_name']
            
        if 'department' in data:
            user.department = data['department']
            
        if 'role' in data and current_user.role == 'Admin':
            user.role = data['role']
            
        if 'password' in data and data['password']:
            user.password_hash = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            # If user updates their own password, clear the flag. 
            # If admin updates another user's password, set the flag.
            if current_user_id == user_id:
                user.must_change_password = False
            else:
                user.must_change_password = True
            
        db.session.commit()
        return jsonify({"message": "User updated successfully"}), 200

    @app.route('/api/users/<int:user_id>', methods=['DELETE'])
    @jwt_required()
    @role_required('Admin')
    def delete_user(user_id):
        from models import Notification, DocumentAudit, Event, Action, Document
        user = db.session.get(User, user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404
        if user.role == 'Admin':
            return jsonify({"error": "Cannot delete root administrator"}), 400
        try:
            # 1. Delete notifications for this user
            Notification.query.filter_by(user_id=user_id).delete()
            # 2. Delete document audit logs for this user
            DocumentAudit.query.filter_by(user_id=user_id).delete()
            # 3. Delete calendar events created by this user
            Event.query.filter_by(user_id=user_id).delete()
            # 4. Nullify or reassign actions assigned to this user
            # Re-assign to admin (user_id=1) rather than delete operational history
            admin = User.query.filter(User.role == 'Admin', User.id != user_id).first()
            fallback_id = admin.id if admin else None
            if fallback_id:
                Action.query.filter_by(assigned_to=user_id).update({"assigned_to": fallback_id})
            else:
                Action.query.filter_by(assigned_to=user_id).delete()
            # 5. Update documents uploaded by this user
            if fallback_id:
                Document.query.filter_by(uploaded_by=user_id).update({"uploaded_by": fallback_id})
            else:
                Document.query.filter_by(uploaded_by=user_id).delete()
            db.session.flush()
            # 6. Finally delete the user
            db.session.delete(user)
            db.session.commit()
            return jsonify({"message": "User permanently removed"}), 200
        except Exception as e:
            db.session.rollback()
            print(f"DELETE user error: {e}")
            return jsonify({"error": f"Failed to delete user: {str(e)}"}), 500

    # --- ATTENDANCE ROUTES ---
    @app.route('/api/attendance/clock', methods=['POST'])
    @jwt_required()
    def clock_attendance():
        from models import AttendanceRecord, db
        current_user_id = int(get_jwt_identity())
        data = request.json
        action = data.get('action') # 'in' or 'out'
        
        now = datetime.now(timezone.utc)
        today_str = now.strftime('%Y-%m-%d')
        
        if action == 'in':
            # Check if already clocked in today
            existing = AttendanceRecord.query.filter_by(user_id=current_user_id, date=today_str).first()
            if existing:
                return jsonify({"error": "Already clocked in today"}), 400
            
            record = AttendanceRecord(
                user_id=current_user_id,
                clock_in_time=now,
                date=today_str,
                status='Present'
            )
            db.session.add(record)
        elif action == 'out':
            record = AttendanceRecord.query.filter_by(user_id=current_user_id, date=today_str).first()
            if not record:
                return jsonify({"error": "No clock-in record found for today"}), 400
            record.clock_out_time = now
        else:
            return jsonify({"error": "Invalid action"}), 400
            
        db.session.commit()
        return jsonify({"message": f"Successfully clocked {action}"}), 200

    @app.route('/api/attendance', methods=['GET'])
    @jwt_required()
    @role_required('Admin')
    def get_attendance():
        from models import AttendanceRecord
        records = AttendanceRecord.query.order_by(AttendanceRecord.clock_in_time.desc()).all()
        return jsonify([{
            "id": r.id, "user_id": r.user_id, "clock_in_time": r.clock_in_time.isoformat(),
            "clock_out_time": r.clock_out_time.isoformat() if r.clock_out_time else None,
            "date": r.date, "status": r.status
        } for r in records]), 200

    # --- PROJECT MANAGEMENT ROUTES ---
    @app.route('/api/projects', methods=['GET'])
    @jwt_required()
    def get_projects():
        from models import Project
        projects = Project.query.order_by(Project.created_at.desc()).all()
        return jsonify([{
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "status": p.status,
            "created_at": p.created_at.isoformat(),
            "created_by": p.created_by
        } for p in projects]), 200

    @app.route('/api/projects', methods=['POST'])
    @jwt_required()
    def create_project():
        from models import Project
        current_user_id = int(get_jwt_identity())
        data = request.json
        if not data or 'name' not in data:
            return jsonify({"error": "Project name is required"}), 400
        
        new_project = Project(
            name=data['name'],
            description=data.get('description', ''),
            status=data.get('status', 'Active'),
            created_by=current_user_id
        )
        db.session.add(new_project)
        db.session.commit()
        return jsonify({"message": "Project created", "id": new_project.id}), 201

    @app.route('/api/projects/<int:project_id>', methods=['PUT'])
    @jwt_required()
    def update_project(project_id):
        from models import Project
        project = db.session.get(Project, project_id)
        if not project:
            return jsonify({"error": "Project not found"}), 404
        
        data = request.json
        if 'name' in data:
            project.name = data['name']
        if 'description' in data:
            project.description = data['description']
        if 'status' in data:
            project.status = data['status']
        
        db.session.commit()
        return jsonify({"message": "Project updated"}), 200

    @app.route('/api/projects/<int:project_id>', methods=['DELETE'])
    @jwt_required()
    @role_required('Admin')
    def delete_project(project_id):
        from models import Project, Action
        project = db.session.get(Project, project_id)
        if not project:
            return jsonify({"error": "Project not found"}), 404
        
        # Dissociate actions
        Action.query.filter_by(project_id=project_id).update({"project_id": None})
        db.session.delete(project)
        db.session.commit()
        return jsonify({"message": "Project deleted"}), 200


    # --- RESOURCE ROUTES ---
    @app.route('/api/resources', methods=['GET'])
    @jwt_required()
    def get_resources():
        from models import Resource
        resources = Resource.query.all()
        return jsonify([{
            "id": r.id, "name": r.name, "type": r.type, 
            "capacity": r.capacity, "is_available": r.is_available
        } for r in resources]), 200

    @app.route('/api/resources', methods=['POST'])
    @jwt_required()
    @role_required('Admin')
    def create_resource():
        from models import Resource
        data = request.json
        new_resource = Resource(
            name=data['name'],
            type=data.get('type', 'Room'),
            capacity=data.get('capacity')
        )
        db.session.add(new_resource)
        db.session.commit()
        return jsonify({"message": "Resource added", "id": new_resource.id}), 201


    @app.route('/api/calendar', methods=['GET'])
    @jwt_required()
    def get_events():
        events = Event.query.all()
        return jsonify([{
            "id": e.id, "title": e.title, "description": e.description,
            "start_time": e.start_time.isoformat(), "end_time": e.end_time.isoformat(),
            "priority": e.priority,
            "mandatory_attendees": e.mandatory_attendees,
            "optional_attendees": e.optional_attendees,
            "location": e.location,
            "meeting_link": e.meeting_link,
            "resource_id": e.resource_id
        } for e in events]), 200

    @app.route('/api/calendar', methods=['POST'])
    @jwt_required()
    def create_event():
        data = request.json
        current_user_id = get_jwt_identity()
        try:
            start_time = datetime.fromisoformat(data['start_time'].replace('Z', '+00:00'))
            end_time = datetime.fromisoformat(data['end_time'].replace('Z', '+00:00'))
            
            # SMART SCHEDULING: Check for conflicts
            # If resource_id is provided, check for conflicts on that resource
            resource_id = data.get('resource_id')
            if resource_id and resource_id != "":
                resource_id = int(resource_id)
                resource_conflict = Event.query.filter(
                    (Event.resource_id == resource_id) &
                    (Event.start_time < end_time) & (Event.end_time > start_time)
                ).first()
                if resource_conflict:
                    return jsonify({"error": f"Resource Conflict: This room/resource is already booked for '{resource_conflict.title}'"}), 400
            else:
                resource_id = None

            import json
            new_event = Event(
                title=data['title'],
                description=data.get('description', ''),
                start_time=start_time,
                end_time=end_time,
                priority=data.get('priority', 'Medium'),
                user_id=int(current_user_id),
                mandatory_attendees=json.dumps(data.get('mandatory_attendees', [])),
                optional_attendees=json.dumps(data.get('optional_attendees', [])),
                resource_id=resource_id,
                location=data.get('location', ''),
                meeting_link=data.get('meeting_link', '')
            )
            db.session.add(new_event)
            db.session.commit()
            return jsonify({"message": "Event created"}), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    @app.route('/api/calendar/<int:event_id>', methods=['PUT'])
    @jwt_required()
    def update_event(event_id):
        event = Event.query.get_or_404(event_id)
        data = request.json
        try:
            if 'title' in data:
                event.title = data['title']
            if 'description' in data:
                event.description = data['description']
            if 'start_time' in data:
                event.start_time = datetime.fromisoformat(data['start_time'].replace('Z', '+00:00'))
            if 'end_time' in data:
                event.end_time = datetime.fromisoformat(data['end_time'].replace('Z', '+00:00'))
            if 'priority' in data:
                event.priority = data['priority']
            db.session.commit()
            return jsonify({"message": "Event updated successfully"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    @app.route('/api/calendar/<int:event_id>', methods=['DELETE'])
    @jwt_required()
    def delete_event(event_id):
        event = Event.query.get_or_404(event_id)
        db.session.delete(event)
        db.session.commit()
        return jsonify({"message": "Event deleted successfully"}), 200


    # --- ACTIONS ROUTES ---
    @app.route('/api/actions', methods=['GET'])
    @jwt_required()
    def get_actions():
        from models import Action, User, Document, Project, db
        # Order by created_at DESC to show newest directives first, join documents and projects
        results = db.session.query(Action, User.username, User.first_name, User.last_name, Document.title.label('doc_title'), Project.name.label('project_name'))\
            .outerjoin(User, Action.assigned_to == User.id)\
            .outerjoin(Document, Action.document_id == Document.id)\
            .outerjoin(Project, Action.project_id == Project.id)\
            .order_by(Action.created_at.desc())\
            .all()
            
        return jsonify([{
            "id": r.Action.id, 
            "title": r.Action.title, 
            "status": r.Action.status, 
            "priority": r.Action.priority, 
            "due_date": r.Action.due_date.isoformat() if r.Action.due_date else None,
            "created_at": r.Action.created_at.isoformat(),
            "assigned_to": r.Action.assigned_to,
            "assigned_username": r.username if r.username else "Unassigned",
            "assigned_first_name": r.first_name,
            "assigned_last_name": r.last_name,
            "document_id": r.Action.document_id,
            "document_title": r.doc_title,
            "project_id": r.Action.project_id,
            "project_name": r.project_name
        } for r in results]), 200


    @app.route('/api/actions', methods=['POST'])
    @jwt_required()
    def create_action():
        from datetime import datetime, timezone
        try:
            data = request.json
            if not data or 'title' not in data or 'assigned_to' not in data:
                return jsonify({"error": "Missing title or assignee"}), 400

            due_date = None
            raw_due_date = data.get('due_date')
            if raw_due_date and str(raw_due_date).strip():
                # Handle potential formats from date picker
                due_date = datetime.fromisoformat(str(raw_due_date).replace('Z', '+00:00'))
                
            doc_id = data.get('document_id')
            if doc_id == "" or doc_id is None:
                doc_id = None
            else:
                doc_id = int(doc_id)

            project_id = data.get('project_id')
            if project_id == "" or project_id is None:
                project_id = None
            else:
                project_id = int(project_id)

            new_action = Action(
                title=data['title'],
                assigned_to=int(data['assigned_to']),
                description=data.get('description', ''),
                status=data.get('status', 'Pending'),
                priority=data.get('priority', 'Medium'),
                due_date=due_date,
                document_id=doc_id,
                project_id=project_id
            )
            db.session.add(new_action)
            db.session.commit()
            
            try:
                from models import Notification
                notif = Notification(
                    user_id=new_action.assigned_to,
                    message=f"New task assigned: {new_action.title}",
                    link="/actions"
                )
                db.session.add(notif)
                db.session.commit()
                
                # REST API Integration: Notify via email
                assignee = db.session.get(User, new_action.assigned_to)
                if assignee and assignee.email:
                    TacticalMailer.send(
                        subject=f"[e-POM] New Operational Directive: {new_action.title}",
                        recipient=assignee.email,
                        body=f"Directive: {new_action.title}\nPriority: {new_action.priority}\nDue Date: {new_action.due_date}\n\nPlease check the e-POM terminal for full tactical brief."
                    )
            except Exception as notif_e:
                db.session.rollback()
                print(f"DEBUG Error creating notification: {str(notif_e)}")
                
            return jsonify({"message": "Action created successfully", "id": new_action.id}), 201
        except Exception as e:
            db.session.rollback()
            print(f"DEBUG Error in create_action: {str(e)}")
            return jsonify({"error": f"Directive creation failure: {str(e)}"}), 500

    @app.route('/api/actions/<int:action_id>', methods=['PUT'])
    @jwt_required()
    def update_action(action_id):
        current_user_id = int(get_jwt_identity())
        current_user = db.session.get(User, current_user_id)
        action = db.session.get(Action, action_id)
        if not action:
            return jsonify({"error": "Action not found"}), 404
        
        # Task can be modified ONLY by the assigned person or an Admin
        if action.assigned_to != current_user_id and current_user.role != 'Admin':
            return jsonify({"error": "Unauthorized: Only the assigned user or an Admin can modify this directive."}), 403

        data = request.json
        if 'status' in data:
            action.status = data['status']
        if 'project_id' in data:
            pid = data.get('project_id')
            action.project_id = int(pid) if (pid and pid != "") else None
        if 'priority' in data:
            action.priority = data['priority']
        if 'assigned_to' in data and data['assigned_to'] and current_user.role == 'Admin':
            new_assignee = int(data['assigned_to'])
            if new_assignee != action.assigned_to:
                action.assigned_to = new_assignee
                try:
                    from models import Notification
                    notif = Notification(
                        user_id=new_assignee,
                        message=f"Task re-assigned to you: {action.title}",
                        link="/actions"
                    )
                    db.session.add(notif)
                except Exception as e:
                    pass
        if 'document_id' in data:
            doc_id = data['document_id']
            action.document_id = int(doc_id) if doc_id not in ("", None) else None
            
        db.session.commit()
        return jsonify({"message": "Action updated successfully"}), 200


    @app.route('/api/notifications', methods=['GET'])
    @jwt_required()
    def get_notifications():
        from models import Notification
        current_user_id = int(get_jwt_identity())
        notifs = Notification.query.filter_by(user_id=current_user_id).order_by(Notification.created_at.desc()).limit(20).all()
        return jsonify([{
            "id": n.id,
            "message": n.message,
            "is_read": n.is_read,
            "link": n.link,
            "created_at": n.created_at.isoformat()
        } for n in notifs]), 200

    @app.route('/api/notifications/<int:notif_id>/read', methods=['PUT'])
    @jwt_required()
    def mark_notification_read(notif_id):
        from models import Notification
        current_user_id = int(get_jwt_identity())
        notif = db.session.get(Notification, notif_id)
        if not notif or notif.user_id != current_user_id:
            return jsonify({"error": "Not found or unauthorized"}), 404
            
        notif.is_read = True
        db.session.commit()
        return jsonify({"message": "Marked as read"}), 200

    @app.route('/api/actions/<int:action_id>', methods=['DELETE'])
    @jwt_required()
    @role_required('Admin')
    def delete_action(action_id):
        action = db.session.get(Action, action_id)
        if not action:
            return jsonify({"error": "Action not found"}), 404
        db.session.delete(action)
        db.session.commit()
        return jsonify({"message": "Action deleted successfully"}), 200


    @app.route('/api/documents', methods=['GET'])
    @jwt_required()
    def get_documents():
        current_user_id = int(get_jwt_identity())
        user = db.session.get(User, current_user_id)
        
        # Use outerjoin to include documents even if uploader user is missing
        query = db.session.query(Document, User.username).outerjoin(User, Document.uploaded_by == User.id)
        
        if user.role != 'Admin':
            query = query.filter(Document.category != 'Restricted')
            
        # Ensure newest documents appear first
        query = query.order_by(Document.created_at.desc())
        docs = query.all()
        return jsonify([{
            "id": d.Document.id, 
            "title": d.Document.title, 
            "file_path": d.Document.file_path,
            "status": d.Document.status, 
            "category": d.Document.category, 
            "uploaded_by": d.Document.uploaded_by,
            "uploader_name": d.username or "Unknown",
            "doc_type": d.Document.doc_type,
            "content": d.Document.content,
            "upload_date": d.Document.created_at.isoformat()
        } for d in docs]), 200

    @app.route('/api/documents/<int:doc_id>/audit', methods=['GET'])
    @jwt_required()
    def get_document_audit(doc_id):
        from models import DocumentAudit, User
        current_user_id = int(get_jwt_identity())
        current_user = db.session.get(User, current_user_id)
        
        # Only admins or document creators can view audit logs
        doc = db.session.get(Document, doc_id)
        if not doc or (current_user.role != 'Admin' and doc.uploaded_by != current_user_id):
            return jsonify({"error": "Unauthorized"}), 403
            
        audits = DocumentAudit.query.filter_by(document_id=doc_id).order_by(DocumentAudit.created_at.desc()).all()
        return jsonify([{
            "id": a.id,
            "action": a.action,
            "user_id": a.user_id,
            "username": User.query.get(a.user_id).username if User.query.get(a.user_id) else "Unknown",
            "created_at": a.created_at.isoformat()
        } for a in audits]), 200

    @app.route('/api/documents/<int:doc_id>/audit', methods=['POST'])
    @jwt_required()
    def create_document_audit(doc_id):
        from models import DocumentAudit
        current_user_id = int(get_jwt_identity())
        data = request.json
        
        audit = DocumentAudit(
            document_id=doc_id,
            user_id=current_user_id,
            action=data.get('action', 'viewed')
        )
        db.session.add(audit)
        db.session.commit()
        return jsonify({"message": "Audit log created"}), 201

    # Serve frontend
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_frontend(path):
        if path != "" and os.path.exists(app.static_folder + '/' + path):
            return send_from_directory(app.static_folder, path)
        else:
            return send_from_directory(app.static_folder, 'index.html')

    return app

# Create app instance for deployment
app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
