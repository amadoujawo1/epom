import { useState, useEffect } from 'react';
import axios from 'axios';
import type { User } from '../App';

interface UserRecord {
  id: number;
  username: string;
  first_name?: string;
  last_name?: string;
  email: string;
  role: string;
  is_active: boolean;
  department?: string;
}


interface UsersProps {
  lang: 'en' | 'fr';
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  translations: Record<string, any>;
  user: User | null;
  token: string | null;
}

const Users = ({ lang, translations, user, token }: UsersProps) => {
  const t = translations?.[lang]?.users || translations?.['en']?.users || {};
  const [users, setUsers] = useState<UserRecord[]>([]);
  const [loading, setLoading] = useState(true);

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

  useEffect(() => {
    console.log("Users component - useEffect called");
    console.log("Token available:", !!token);
    console.log("Current users count:", users.length);
    
    fetchUsers();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token, lang]);

  
  
  const handleToggleStatus = async (userId: number, isCurrentlyActive: boolean) => {
    const action = isCurrentlyActive
      ? (t.disable_prompt || (lang === 'fr' ? 'désactiver' : 'disable'))
      : (t.enable_prompt || (lang === 'fr' ? 'activer' : 'enable'));
    if (!window.confirm(`${t.confirm_action || (lang === 'fr' ? 'Voulez-vous' : 'Are you sure you want to')} ${action} ${lang === 'fr' ? 'cet utilisateur' : 'this user'}?`)) return;
    try {
      await axios.put(`/api/users/${userId}/status`, { is_active: !isCurrentlyActive }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      fetchUsers();
    } catch (err: unknown) {
      const axiosError = err as { response?: { data?: { error?: string } } };
      alert(axiosError.response?.data?.error || 'Failed to update user status');
    }
  };

  const handleDelete = async (userId: number) => {
    if (!window.confirm(lang === 'fr' ? 'Supprimer définitivement cet utilisateur ?' : 'Permanently delete this user? This cannot be undone.')) return;
    try {
      await axios.delete(`/api/users/${userId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      fetchUsers();
    } catch (err: unknown) {
      const axiosError = err as { response?: { data?: { error?: string } } };
      alert(axiosError.response?.data?.error || 'Failed to delete user');
    }
  };

  console.log("Users component render - users count:", users.length, "loading:", loading);
  return (
    <div className="space-y-6 max-w-7xl">
      <div className="premium-card p-8 fade-in-up flex flex-col md:flex-row justify-between md:items-center gap-4">
        <div>
          <h2 className="text-3xl font-bold text-slate-800 mb-2">{t.title || 'Personnel Management'}</h2>
          <p className="text-slate-500 font-medium">{t.subtitle || 'Administrative control over user roles, access, and organization hierarchy.'}</p>
        </div>
        
              </div>

      
      {/* Employee Registry */}
      <div className="premium-card overflow-hidden fade-in-up" style={{ animationDelay: '0.1s' }}>
        <div className="overflow-x-auto custom-scrollbar">
          <table className="w-full min-w-[900px] text-left border-collapse">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-100 text-xs uppercase tracking-widest text-slate-400">
                <th className="px-6 py-4 font-black">{lang === 'fr' ? 'Employé(e)' : 'Employee'}</th>
                <th className="px-6 py-4 font-black">{lang === 'fr' ? 'Département' : 'Department'}</th>
                <th className="px-6 py-4 font-black">{t.th_role || 'Role'}</th>
                <th className="px-6 py-4 font-black">{t.th_status || 'Status'}</th>
                {user?.role === 'Admin' && <th className="px-6 py-4 font-black">{t.th_options || 'Options'}</th>}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? (
                <tr><td colSpan={user?.role === 'Admin' ? 6 : 5} className="px-6 py-8 text-center text-slate-500">{t.loading || 'Loading directory...'}</td></tr>
              ) : users.length === 0 ? (
                <tr><td colSpan={user?.role === 'Admin' ? 6 : 5} className="px-6 py-8 text-center text-slate-500">{t.no_users || 'No profiles found.'}</td></tr>
              ) : (
                users.map((u: UserRecord) => (
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
                          u.role === 'minister' ? 'bg-purple-100 text-purple-700' :
                          u.role === 'chief_of_staff' ? 'bg-blue-100 text-blue-700' :
                          u.role === 'advisor' ? 'bg-green-100 text-green-700' :
                          u.role === 'protocol' ? 'bg-orange-100 text-orange-700' :
                          u.role === 'assistant' ? 'bg-cyan-100 text-cyan-700' :
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
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
};

export default Users;
