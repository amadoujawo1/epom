import { useState } from 'react';
import axios from 'axios';
import type { User } from '../App';

interface SettingsProps {
  user: User | null;
  token: string | null;
  setUser: (user: User | null) => void;
  lang: 'en' | 'fr';
  setLang: (lang: 'en' | 'fr') => void;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  translations: Record<string, any>;
  theme: 'light' | 'dark';
  setTheme: (theme: 'light' | 'dark') => void;
}

const Settings = ({ user: _user, token, setUser, lang, setLang, translations, theme, setTheme }: SettingsProps) => {
  const t = translations?.[lang]?.nav || translations?.['en']?.nav || {};
  const s = translations?.[lang]?.settings || translations?.['en']?.settings || {};

  const [showEditProfile, setShowEditProfile] = useState(false);
  const [isUpdating, setIsUpdating] = useState(false);
  const [profileData, setProfileData] = useState({
    first_name: _user?.first_name || '',
    last_name: _user?.last_name || '',
    email: _user?.email || '',
    username: _user?.username || ''
  });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleUpdateProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!_user || !token) return;
    setIsUpdating(true);
    setError('');
    setSuccess('');

    try {
      await axios.put(`/api/users/${_user.id}`, profileData, {
        headers: { Authorization: `Bearer ${token}` }
      });

      const updatedUser = { ..._user, ...profileData };
      setUser(updatedUser);
      localStorage.setItem('user', JSON.stringify(updatedUser));

      setSuccess(lang === 'fr' ? 'Profil mis à jour !' : 'Profile updated successfully!');
      setTimeout(() => {
        setShowEditProfile(false);
        setSuccess('');
      }, 1500);
    } catch (err: unknown) {
      const axiosError = err as { response?: { data?: { error?: string } } };
      setError(axiosError.response?.data?.error || 'Failed to update profile');
    } finally {
      setIsUpdating(false);
    }
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <div className="premium-card p-8 fade-in-up">
        <h2 className="text-3xl font-black text-slate-800 mb-2">{t.settings || 'Settings'}</h2>
        <p className="text-slate-500 font-medium">{lang === 'fr' ? 'Préférences et configuration de l\'application.' : 'Application preferences and system configuration.'}</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Language Preferences */}
        <div className="premium-card p-8 fade-in-up" style={{ animationDelay: '0.1s' }}>
          <div className="flex items-center gap-4 mb-6">
            <div className="w-12 h-12 rounded-2xl bg-indigo-50 text-indigo-600 flex items-center justify-center text-2xl shadow-sm">🌍</div>
            <div>
              <h3 className="text-lg font-bold text-slate-800">{s.language || 'Language Preference'}</h3>
              <p className="text-xs text-slate-400 font-bold uppercase tracking-widest">{s.display_lang || 'Display Language'}</p>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <button
              onClick={() => setLang('en')}
              className={`p-4 rounded-2xl border-2 transition-all flex flex-col items-center gap-2 ${lang === 'en' ? 'border-indigo-500 bg-indigo-50 shadow-md' : 'border-slate-100 hover:border-slate-200 bg-white'}`}
            >
              <span className="text-2xl">🇬🇧</span>
              <span className={`font-bold text-sm ${lang === 'en' ? 'text-indigo-600' : 'text-slate-600'}`}>English</span>
            </button>
            <button
              onClick={() => setLang('fr')}
              className={`p-4 rounded-2xl border-2 transition-all flex flex-col items-center gap-2 ${lang === 'fr' ? 'border-indigo-500 bg-indigo-50 shadow-md' : 'border-slate-100 hover:border-slate-200 bg-white'}`}
            >
              <span className="text-2xl">🇫🇷</span>
              <span className={`font-bold text-sm ${lang === 'fr' ? 'text-indigo-600' : 'text-slate-600'}`}>Français</span>
            </button>
          </div>
        </div>

        {/* System Theme */}
        <div className="premium-card p-8 fade-in-up" style={{ animationDelay: '0.2s' }}>
          <div className="flex items-center gap-4 mb-6">
            <div className="w-12 h-12 rounded-2xl bg-amber-50 text-amber-600 flex items-center justify-center text-2xl shadow-sm">✨</div>
            <div>
              <h3 className="text-lg font-bold text-slate-800">{lang === 'fr' ? 'Apparence' : 'Appearance'}</h3>
              <p className="text-xs text-slate-400 font-bold uppercase tracking-widest">{lang === 'fr' ? 'Thème du système' : 'System Theme'}</p>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <button
              onClick={() => setTheme('light')}
              className={`p-4 rounded-2xl border-2 transition-all flex flex-col items-center gap-2 ${theme === 'light' ? 'border-amber-500 bg-amber-50 shadow-md' : 'border-slate-100 hover:border-slate-200 bg-white'}`}
            >
              <span className="text-2xl">☀️</span>
              <span className={`font-bold text-sm ${theme === 'light' ? 'text-amber-700' : 'text-slate-600'}`}>{lang === 'fr' ? 'Clair' : 'Light'}</span>
            </button>
            <button
              onClick={() => setTheme('dark')}
              className={`p-4 rounded-2xl border-2 transition-all flex flex-col items-center gap-2 ${theme === 'dark' ? 'border-indigo-500 bg-indigo-900 shadow-md' : 'border-slate-100 hover:border-slate-200 bg-white'}`}
            >
              <span className="text-2xl">🌙</span>
              <span className={`font-bold text-sm ${theme === 'dark' ? 'text-indigo-400' : 'text-slate-600'}`}>{lang === 'fr' ? 'Sombre' : 'Dark'}</span>
            </button>
          </div>
        </div>

        {/* Security Section */}
        <div className="premium-card p-8 md:col-span-2 fade-in-up" style={{ animationDelay: '0.2s' }}>
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-black text-slate-800 text-xl mb-1">{lang === 'fr' ? 'Sécurité & MFA' : 'Security & MFA'}</h3>
              <p className="text-slate-400 text-sm font-medium">{lang === 'fr' ? 'Authentification à deux facteurs' : 'Multi-factor authentication for sensitive access'}</p>
            </div>
            <div className="flex items-center gap-4">
              <div
                onClick={async () => {
                  if (!_user || !token) return;
                  const newState = !_user.mfa_enabled;
                  try {
                    await axios.put(`/api/users/${_user.id}`, { mfa_enabled: newState }, {
                      headers: { Authorization: `Bearer ${token}` }
                    });
                    const updatedUser = { ..._user, mfa_enabled: newState };
                    setUser(updatedUser);
                    localStorage.setItem('user', JSON.stringify(updatedUser));
                  } catch {
                    console.error("Failed to toggle MFA state");
                  }
                }}
                className={`w-14 h-8 rounded-full p-1 cursor-pointer transition-all duration-300 ${(_user?.mfa_enabled) ? 'bg-indigo-600' : 'bg-slate-200'}`}
              >
                <div className={`w-6 h-6 bg-white rounded-full shadow-md transform transition-transform duration-300 ${(_user?.mfa_enabled) ? 'translate-x-6' : 'translate-x-0'}`}></div>
              </div>
            </div>
          </div>
        </div>

        {/* Account Info */}
        <div className="premium-card p-8 md:col-span-2 fade-in-up" style={{ animationDelay: '0.3s' }}>
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
            <div className="flex items-center gap-6">
              <div className="w-20 h-20 rounded-[28px] bg-slate-800 text-white flex items-center justify-center text-3xl font-black shadow-xl shrink-0">
                {_user?.username?.charAt(0).toUpperCase()}
              </div>
              <div>
                <h3 className="text-2xl font-black text-slate-800">{_user?.username}</h3>
                <p className="text-slate-400 font-bold text-xs uppercase tracking-[0.2em] mt-1">{_user?.role} • EPOM OFFICIAL ACCOUNT</p>
                <p className="text-slate-500 font-medium mt-2">{_user?.email}</p>
              </div>
            </div>
            <div className="flex gap-3">
              <button
                onClick={() => setShowEditProfile(true)}
                className="px-6 py-3 rounded-xl bg-slate-100 text-slate-600 font-bold text-sm hover:bg-slate-200 transition-all">
                {lang === 'fr' ? 'Modifier le profil' : 'Edit Profile'}
              </button>
            </div>
          </div>
        </div>
      </div>

      {showEditProfile && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm shadow-2xl transition-opacity">
          <div className="bg-white rounded-[32px] shadow-2xl w-full max-w-lg overflow-hidden border border-slate-100 scale-in-center">
            <div className="p-8 border-b border-slate-50 flex justify-between items-center bg-slate-50/50">
              <h3 className="font-black text-slate-800 text-2xl">
                {lang === 'fr' ? 'Modifier le profil' : 'Edit Profile'}
              </h3>
              <button
                onClick={() => setShowEditProfile(false)}
                className="w-10 h-10 flex items-center justify-center rounded-full text-slate-400 hover:text-slate-700 hover:bg-slate-200 transition-all"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleUpdateProfile} className="p-8 space-y-6">
              {error && <div className="p-4 bg-red-50 text-red-600 rounded-2xl text-xs font-bold border border-red-100">{error}</div>}
              {success && <div className="p-4 bg-emerald-50 text-emerald-600 rounded-2xl text-xs font-bold border border-emerald-100">{success}</div>}

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1.5">
                  <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">{lang === 'fr' ? 'Prénom' : 'First Name'}</label>
                  <input
                    type="text"
                    value={profileData.first_name}
                    onChange={e => setProfileData({ ...profileData, first_name: e.target.value })}
                    className="w-full px-5 py-3.5 bg-slate-50 border-0 rounded-2xl focus:ring-2 focus:ring-indigo-500 outline-none font-bold text-slate-700"
                  />
                </div>
                <div className="space-y-1.5">
                  <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">{lang === 'fr' ? 'Nom' : 'Last Name'}</label>
                  <input
                    type="text"
                    value={profileData.last_name}
                    onChange={e => setProfileData({ ...profileData, last_name: e.target.value })}
                    className="w-full px-5 py-3.5 bg-slate-50 border-0 rounded-2xl focus:ring-2 focus:ring-indigo-500 outline-none font-bold text-slate-700"
                  />
                </div>
              </div>

              <div className="space-y-1.5">
                <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">{lang === 'fr' ? 'Email' : 'Email Address'}</label>
                <input
                  type="email"
                  value={profileData.email}
                  onChange={e => setProfileData({ ...profileData, email: e.target.value })}
                  className="w-full px-5 py-3.5 bg-slate-50 border-0 rounded-2xl focus:ring-2 focus:ring-indigo-500 outline-none font-bold text-slate-700"
                />
              </div>

              <div className="pt-4 flex gap-3">
                <button
                  type="button"
                  onClick={() => setShowEditProfile(false)}
                  className="flex-1 py-4.5 rounded-2xl font-black text-xs uppercase tracking-widest text-slate-400 hover:bg-slate-100 transition-all"
                >
                  {lang === 'fr' ? 'Annuler' : 'Cancel'}
                </button>
                <button
                  type="submit"
                  disabled={isUpdating}
                  className="flex-1 bg-slate-900 text-white font-black text-xs uppercase tracking-widest py-4.5 rounded-2xl shadow-xl hover:bg-indigo-600 transition-all active:scale-95 disabled:opacity-50"
                >
                  {isUpdating ? '...' : (lang === 'fr' ? 'Enregistrer' : 'Save Changes')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Settings;
