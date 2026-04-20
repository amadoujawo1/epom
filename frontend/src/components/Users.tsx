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
  const [showAddForm, setShowAddForm] = useState(false);
  const [formData, setFormData] = useState({ first_name: '', last_name: '', username: '', email: '', password: '', confirmPassword: '', role: 'Assistant', department: '' });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [error, setError] = useState('');
  const [editingUser, setEditingUser] = useState<UserRecord | null>(null);
  const [success, setSuccess] = useState('');

  const fetchUsers = async () => {
    if (!token) return;
    try {
      setLoading(true);
      const res = await axios.get(`/api/users`, { headers: { Authorization: `Bearer ${token}` } });
      setUsers(res.data);
    } catch {
      console.error("Failed to fetch users");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token, lang]);

  const handleAddUser = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (!editingUser && formData.password !== formData.confirmPassword) {
      setError(lang === 'fr' ? 'Les mots de passe ne correspondent pas.' : 'Passwords do not match.');
      return;
    }

    try {
      if (editingUser) {
        // Update existing user
        const updateData: Record<string, string | undefined> = {
          first_name: formData.first_name,
          last_name: formData.last_name,
          username: formData.username,
          email: formData.email,
          role: formData.role,
          department: formData.department
        };
        if (formData.password) updateData.password = formData.password;

        await axios.put(`/api/users/${editingUser.id}`, updateData, {
          headers: { Authorization: `Bearer ${token}` }
        });
        setSuccess(lang === 'fr' ? 'Personnel mis à jour !' : 'Personnel updated successfully!');
      } else {
        // Create new user
        // eslint-disable-next-line @typescript-eslint/no-unused-vars
        const { confirmPassword: _confirmPassword, ...registerData } = formData;
        await axios.post(`/api/auth/register`, registerData);
        setSuccess(lang === 'fr' ? 'Personnel ajouté avec succès !' : 'Personnel added successfully!');
      }

      setFormData({ first_name: '', last_name: '', username: '', email: '', password: '', confirmPassword: '', role: 'Assistant', department: '' });
      setShowAddForm(false);
      setEditingUser(null);
      fetchUsers();
    } catch (err: unknown) {
      const axiosError = err as { response?: { data?: { error?: string } } };
      setError(axiosError.response?.data?.error || (lang === 'fr' ? "Échec de l'action" : 'Failed to process personnel action'));
    }
  };

  const startEdit = (targetUser: UserRecord) => {
    setEditingUser(targetUser);
    setFormData({
      first_name: targetUser.first_name || '',
      last_name: targetUser.last_name || '',
      username: targetUser.username,
      email: targetUser.email,
      department: targetUser.department || '',
      password: '',
      confirmPassword: '',
      role: targetUser.role
    });
    setShowAddForm(true);
  };

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

  return (
    <div className="space-y-6 max-w-7xl">
      <div className="premium-card p-8 fade-in-up flex flex-col md:flex-row justify-between md:items-center gap-4">
        <div>
          <h2 className="text-3xl font-bold text-slate-800 mb-2">{t.title || 'Personnel Management'}</h2>
          <p className="text-slate-500 font-medium">{t.subtitle || 'Administrative control over user roles, access, and organization hierarchy.'}</p>
        </div>
        
        <div className="flex gap-3 items-center">
          {user?.role === 'Admin' && (
            <button
              onClick={() => {
                setEditingUser(null);
                setFormData({ first_name: '', last_name: '', username: '', email: '', password: '', confirmPassword: '', role: 'Assistant', department: '' });
                setError('');
                setSuccess('');
                setShowAddForm(true);
              }}
              className="bg-indigo-600 hover:bg-indigo-700 text-white px-5 py-2.5 rounded-xl font-bold flex items-center gap-2 shadow-lg shadow-indigo-200 transition-all active:scale-95 whitespace-nowrap"
            >
              <span className="text-xl leading-none font-medium mb-0.5">+</span> {t.add_btn || 'Add Personnel'}
            </button>
          )}
        </div>
      </div>

      {showAddForm && user?.role === 'Admin' && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm shadow-2xl fade-in-up" style={{ animationDuration: '0.2s' }}>
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl overflow-hidden border border-slate-100 flex flex-col max-h-[90vh]">
            <div className="p-6 border-b border-slate-100 flex justify-between items-center bg-slate-50/50">
              <h3 className="font-bold text-slate-800 text-xl">
                {editingUser ? (t.edit || 'Edit Personnel Profile') : (t.form_title || 'Register Employee Profile')}
              </h3>
              <button
                onClick={() => {
                  setShowAddForm(false);
                  setEditingUser(null);
                }}
                className="w-8 h-8 flex items-center justify-center rounded-full text-slate-400 hover:text-slate-700 hover:bg-slate-200 transition-colors"
                title={t.close_btn || 'Close'}
              >
                ✕
              </button>
            </div>

            <div className="p-6 overflow-y-auto custom-scrollbar">
              {error && <div className="mb-5 text-sm text-red-600 bg-red-50 p-4 rounded-xl font-semibold border border-red-100 flex items-center gap-3"><span className="text-base text-red-500">✕</span> {error}</div>}
              {success && <div className="mb-5 text-sm text-emerald-600 bg-emerald-50 p-4 rounded-xl font-semibold border border-emerald-100 flex items-center gap-3"><span className="text-base text-emerald-500">✓</span> {success}</div>}

              <form onSubmit={handleAddUser} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-1.5">{t.first_name || (lang === 'fr' ? 'Prénom' : 'First Name')}</label>
                    <input
                      type="text"
                      value={formData.first_name}
                      onChange={e => setFormData({ ...formData, first_name: e.target.value })}
                      className="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:ring-2 focus:ring-indigo-500 outline-none"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-1.5">{t.last_name || (lang === 'fr' ? 'Nom' : 'Last Name')}</label>
                    <input
                      type="text"
                      value={formData.last_name}
                      onChange={e => setFormData({ ...formData, last_name: e.target.value })}
                      className="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:ring-2 focus:ring-indigo-500 outline-none"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-1.5">{t.username || 'System Username'}</label>
                    <input
                      required type="text"
                      value={formData.username}
                      onChange={e => setFormData({ ...formData, username: e.target.value })}
                      className="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:ring-2 focus:ring-indigo-500 outline-none"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-1.5">{t.email || 'Email Address'}</label>
                    <input
                      required type="email"
                      value={formData.email}
                      onChange={e => setFormData({ ...formData, email: e.target.value })}
                      className="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:ring-2 focus:ring-indigo-500 outline-none"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-1.5">{lang === 'fr' ? 'Département' : 'Department/Branch'}</label>
                    <input
                      type="text"
                      value={formData.department}
                      onChange={e => setFormData({ ...formData, department: e.target.value })}
                      className="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:ring-2 focus:ring-indigo-500 outline-none"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-1.5">{t.temp_pass || 'Password'}</label>
                    <div className="relative">
                      <input
                        required={!editingUser} type={showPassword ? 'text' : 'password'}
                        placeholder={editingUser ? (lang === 'fr' ? '(Inchangé)' : '(Unchanged)') : ''}
                        value={formData.password}
                        onChange={e => setFormData({ ...formData, password: e.target.value })}
                        className="w-full px-4 py-2.5 pr-10 bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:ring-2 focus:ring-indigo-500 outline-none"
                      />
                      <button
                        type="button"
                        onClick={() => setShowPassword(!showPassword)}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-indigo-600 p-2"
                      >
                        {showPassword ? "Hide" : "Show"}
                      </button>
                    </div>
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-1.5">{t.confirm_pass || 'Confirm Password'}</label>
                    <div className="relative">
                      <input
                        required={!!formData.password} type={showConfirmPassword ? 'text' : 'password'}
                        value={formData.confirmPassword}
                        onChange={e => setFormData({ ...formData, confirmPassword: e.target.value })}
                        className="w-full px-4 py-2.5 pr-10 bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:ring-2 focus:ring-indigo-500 outline-none"
                      />
                      <button
                        type="button"
                        onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-indigo-600 p-2"
                      >
                        {showConfirmPassword ? "Hide" : "Show"}
                      </button>
                    </div>
                  </div>

                  <div className="md:col-span-2">
                    <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-1.5">{t.role || 'System Role'}</label>
                    <div className="relative">
                      <select
                        value={formData.role}
                        onChange={e => setFormData({ ...formData, role: e.target.value })}
                        className="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:ring-2 focus:ring-indigo-500 outline-none appearance-none"
                      >
                        <option value="Minister">{t.roles?.minister || 'Minister'}</option>
                        <option value="Chief of staff">{t.roles?.chief_of_staff || 'Chief of staff'}</option>
                        <option value="Advisor">{t.roles?.advisor || 'Advisor'}</option>
                        <option value="Protocol">{t.roles?.protocol || 'Protocol'}</option>
                        <option value="Assistant">{t.roles?.assistant || 'Assistant'}</option>
                        <option value="Admin">{t.roles?.admin || 'Administrator'}</option>
                      </select>
                      <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-4 text-slate-500 text-xs">▼</div>
                    </div>
                  </div>
                </div>

                <div className="pt-4 flex justify-end gap-3 border-t border-slate-100 mt-2">
                  <button
                    type="button"
                    onClick={() => {
                      setShowAddForm(false);
                      setEditingUser(null);
                    }}
                    className="px-5 py-2.5 rounded-xl font-bold text-slate-600 hover:bg-slate-100"
                  >
                    {t.close_btn || 'Cancel'}
                  </button>
                  <button type="submit" className="bg-indigo-600 text-white font-bold py-2.5 px-6 rounded-xl hover:bg-indigo-700 shadow-md">
                    {editingUser ? (t.save_btn || 'Save Changes') : (t.create_btn || 'Create Profile')}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

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
                          u.role === 'Minister' ? 'bg-purple-100 text-purple-700' :
                          u.role === 'Chief of staff' ? 'bg-blue-100 text-blue-700' :
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
