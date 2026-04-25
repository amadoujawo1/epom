#!/usr/bin/env python3
"""
Debug Flask route registration
"""

import sys
import os
sys.path.append('backend')

def check_flask_app():
    """Check Flask app structure and route registration"""
    try:
        # Import the app
        from app import create_app
        
        print("🔍 Debugging Flask App Structure")
        print("=" * 50)
        
        # Create app instance
        app = create_app()
        
        print(f"✅ Flask app created successfully")
        print(f"📊 Total routes: {len(list(app.url_map.iter_rules()))}")
        
        # Check for roles endpoint
        roles_found = False
        for rule in app.url_map.iter_rules():
            if 'roles' in rule.rule.lower():
                print(f"✅ Found roles route: {rule.methods} {rule.rule}")
                roles_found = True
        
        if not roles_found:
            print("❌ No roles route found!")
            
            # Check if the function exists
            try:
                from app import get_roles
                print("✅ get_roles function exists but route not registered")
            except ImportError:
                print("❌ get_roles function not found")
                
            # Check the app.py file structure
            print("\n🔍 Checking app.py structure...")
            app_py_path = os.path.join('backend', 'app.py')
            if os.path.exists(app_py_path):
                with open(app_py_path, 'r') as f:
                    content = f.read()
                    if '@app.route(\'/api/roles\'' in content:
                        print("✅ @app.route('/api/roles') found in app.py")
                    else:
                        print("❌ @app.route('/api/roles') NOT found in app.py")
                        
                    if 'def get_roles():' in content:
                        print("✅ def get_roles(): found in app.py")
                    else:
                        print("❌ def get_roles(): NOT found in app.py")
            else:
                print("❌ app.py file not found")
        
        return roles_found
        
    except Exception as e:
        print(f"❌ Error checking Flask app: {e}")
        return False

def main():
    success = check_flask_app()
    
    print(f"\n📊 DEBUG RESULT")
    print("=" * 50)
    
    if success:
        print("✅ /api/roles endpoint is properly registered")
    else:
        print("❌ /api/roles endpoint has registration issues")
        print("🔧 Need to fix Flask route registration")

if __name__ == "__main__":
    main()
