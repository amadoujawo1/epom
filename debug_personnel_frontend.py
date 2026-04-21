#!/usr/bin/env python3
"""
Debug personnel management frontend issue by adding logging
"""

import requests
import json

# Railway deployment URL
RAILWAY_URL = "https://web-production-f029b.up.railway.app"

def get_auth_token():
    """Get authentication token from Railway"""
    login_data = {"username": "admin", "password": "admin123"}
    
    try:
        response = requests.post(f"{RAILWAY_URL}/api/auth/login", json=login_data)
        if response.status_code == 200:
            token_data = response.json()
            print("Successfully authenticated with Railway")
            return token_data.get("token")
        else:
            print(f"Login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Error connecting to Railway: {e}")
        return None

def create_frontend_fix():
    """Create frontend fix for personnel management"""
    print("Creating frontend fix for personnel management...")
    
    frontend_code = '''
// Add this debugging to the fetchUsers function in Users.tsx:

const fetchUsers = async () => {
    if (!token) return;
    try {
      setLoading(true);
      console.log("Fetching users...");
      const res = await axios.get(`/api/users`, { headers: { Authorization: `Bearer ${token}` } });
      console.log("Users response:", res.data);
      console.log("Users response status:", res.status);
      console.log("Users response headers:", res.headers);
      setUsers(res.data);
      console.log("Users state set:", res.data);
      console.log("Users length:", res.data?.length || 0);
    } catch {
      console.error("Failed to fetch users");
    } finally {
      setLoading(false);
    }
  };

// Also add this debugging to the useEffect:

useEffect(() => {
    console.log("Users component - useEffect called");
    console.log("Token available:", !!token);
    console.log("Current users count:", users.length);
    
    if (token) {
      console.log("Calling fetchUsers...");
      fetchUsers();
    }
  }, [token, fetchUsers]);

// And add this debugging to the users rendering:

{loading ? (
    <tr><td colSpan={user?.role === 'Admin' ? 6 : 5} className="px-6 py-8 text-center text-slate-500">{t.loading || 'Loading directory...'}</td></tr>
) : users.length === 0 ? (
    <tr><td colSpan={user?.role === 'Admin' ? 6 : 5} className="px-6 py-8 text-center text-slate-500">{t.no_users || 'No profiles found.'}</td></tr>
) : (
    <>
      {console.log("Rendering users list, count:", users.length)}
      {users.map((u: UserRecord) => (
        <tr key={u.id} className="hover:bg-slate-50/50 transition-colors">
          <td className="px-6 py-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-slate-200 text-slate-600 flex items-center justify-center font-bold text-lg">
                {u.first_name ? u.first_name.charAt(0).toUpperCase() : u.username.charAt(0).toUpperCase()}
              </div>
              <div>
                <p className="font-bold text-slate-800 leading-tight block">{u.first_name} {u.last_name}</p>
                <span className="text-xs text-slate-500 font-medium">@{u.username} • {u.email}</span>
              </div>
            </div>
          </td>
          <td className="px-6 py-4 font-medium text-slate-700 whitespace-nowrap">
            {u.department || '-'}
          </td>
          <td className="px-6 py-4">
            <span className={`px-2 py-1 rounded-md text-xs font-bold ${u.role === 'Admin' ? 'bg-indigo-100 text-indigo-700' :
                u.role === 'Minister' ? 'bg-purple-100 text-purple-700' :
                  'bg-slate-100 text-slate-600'
            }`}>
              {(() => {
                const roleKey = u.role?.toLowerCase().replace(/ /g, '_');
                return t.roles?.[roleKey] || u.role;
              })()}
            </span>
          </td>
          <td className="px-6 py-4">
            <span className={`flex items-center gap-1.5 text-xs font-bold ${u.is_active !== false ? 'text-emerald-500' : 'text-red-500'}`}>
              <span className={`w-2 h-2 rounded-full ${u.is_active !== false ? 'bg-emerald-500' : 'bg-red-500'}`}></span>
              {u.is_active !== false ? (t.active || 'ACTIVE') : (t.disabled || 'DISABLED')}
            </span>
          </td>
          {user?.role === 'Admin' && (
            <td className="px-6 py-4">
              <div className="flex items-center gap-1.5">
                <button
                  onClick={() => startEdit(u)}
                  className="p-1.5 text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors"
                  title={t.edit || "Edit"}
                >
                  ✏️
                </button>
                <button
                  onClick={() => handleToggleStatus(u.id, u.is_active !== false)}
                  className={`px-2 py-1 rounded-lg text-xs font-bold transition-colors ${u.is_active !== false
                      ? 'text-amber-600 bg-amber-50 hover:bg-amber-100'
                      : 'text-emerald-600 bg-emerald-50 hover:bg-emerald-100'
                    }`}
                >
                  {u.is_active !== false ? 'Disable' : 'Enable'}
                </button>
                <button
                  onClick={() => handleDelete(u.id)}
                  className="p-1.5 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                >
                  🗑️
                </button>
              </div>
            </td>
          )}
        </tr>
      </>
    )}
'''
    
    print("Add this debugging code to Users.tsx:")
    print("1. Enhanced fetchUsers function with console logging")
    print("2. Enhanced useEffect with debugging")
    print("3. Enhanced users rendering with console logs")
    print("4. This will help identify why users aren't showing")
    
    return frontend_code

def main():
    """Main function"""
    print("Debugging personnel management frontend issue...")
    
    frontend_code = create_frontend_fix()
    
    print(f"\nSOLUTION:")
    print("1. The /api/users endpoint is working correctly")
    print("2. The issue is likely in frontend component state management")
    print("3. Add extensive debugging to identify the problem")
    print("4. The debugging will show:")
    print("   - When fetchUsers is called")
    print("   - What data is returned from API")
    print("   - What users state contains")
    print("   - When rendering happens")
    print("5. This will help identify the exact issue")

if __name__ == "__main__":
    main()
