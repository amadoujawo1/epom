import { useState, useEffect, useCallback } from 'react';
import { Routes, Route, Navigate, NavLink, useLocation, useNavigate } from 'react-router-dom';
import axios from 'axios';

const API_BASE = '/api';

// Import your components (you'll need to create these)
import Dashboard from './components/Dashboard.tsx';
import Login from './components/Login.tsx';
import Calendar from './components/Calendar.tsx';
import Documents from './components/Documents.tsx';
import Actions from './components/Actions.tsx';
import Users from './components/Users.tsx';
import Reports from './components/Reports.tsx';
import Settings from './components/Settings.tsx';

// Import translations
import { translations } from './translations';

export interface User {
  id: number;
  username: string;
  email: string;
  role: string;
  first_name?: string;
  last_name?: string;
  is_active?: boolean;
  mfa_enabled?: boolean;
  mfa_code?: string;
  department?: string;
  must_change_password?: boolean;
}

interface Notification {
  id: number;
  message: string;
  is_read: boolean;
  link?: string;
  created_at: string;
}

// ProtectedRoute: redirects to /login if not authenticated
function ProtectedRoute({ token, children }: { token: string | null; children: React.ReactNode }) {
  const location = useLocation();
  if (!token) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }
  return <>{children}</>;
}

function App() {
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'));
  const [user, setUser] = useState<User | null>(JSON.parse(localStorage.getItem('user') || 'null'));
  const [lang, setLang] = useState<'en' | 'fr'>(localStorage.getItem('lang') as 'en' | 'fr' || 'en');
  const [authMessage, setAuthMessage] = useState<string | null>(null);
  const [logoutCounter, setLogoutCounter] = useState(0);
  const location = useLocation();
  const navigate = useNavigate();

  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [showNotifications, setShowNotifications] = useState(false);
  const [theme, setTheme] = useState<'light' | 'dark'>(localStorage.getItem('theme') as 'light' | 'dark' || 'light');
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [showResetPassword, setShowResetPassword] = useState(false);

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }, [theme]);

  useEffect(() => {
    if (token) {
      axios.get(`${API_BASE}/notifications`, { headers: { Authorization: `Bearer ${token}` } })
        .then(async (res) => {
          const fetchedNotifs: Notification[] = res.data;

          // Identify unread notifications for the current page
          const unreadOnCurrentPage = fetchedNotifs.filter(n => !n.is_read && n.link === location.pathname);

          if (unreadOnCurrentPage.length > 0) {
            // Mark all on-page notifications as read in parallel
            try {
              await Promise.all(unreadOnCurrentPage.map(n =>
                axios.put(`${API_BASE}/notifications/${n.id}/read`, {}, {
                  headers: { Authorization: `Bearer ${token}` }
                })
              ));
              // Update local state for all marked notifications at once
              const readIds = unreadOnCurrentPage.map(n => n.id);
              setNotifications(fetchedNotifs.map(n =>
                readIds.includes(n.id) ? { ...n, is_read: true } : n
              ));
            } catch (err: unknown) {
              console.error("Failed to mark notifications as read", err);
              setNotifications(fetchedNotifs);
            }
          } else {
            setNotifications(fetchedNotifs);
          }
        })
        .catch(() => console.error("Failed to fetch notifications"));
    }
  }, [token, location.pathname]);

  const unreadCount = notifications.filter(n => !n.is_read).length;

  const handleNotificationClick = async (notif: Notification) => {
    if (!notif.is_read) {
      try {
        await axios.put(`${API_BASE}/notifications/${notif.id}/read`, {}, {
          headers: { Authorization: `Bearer ${token}` }
        });
        setNotifications(prev => prev.map(n => n.id === notif.id ? { ...n, is_read: true } : n));
      } catch (err: unknown) {
        console.error("Failed to mark individual notification as read", err);
      }
    }
    setShowNotifications(false);
    if (notif.link) {
      navigate(notif.link);
    }
  };

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const t = translations[lang] as any;

  useEffect(() => {
    localStorage.setItem('lang', lang);
  }, [lang]);

  const handleLogin = async (username: string, password: string) => {
    try {
      const response = await axios.post(`${API_BASE}/auth/login`, { username, password });

      if (response.data.mfa_required) {
        return { mfa_required: true, user_id: response.data.user_id, message: response.data.message };
      }

      const { token: newToken, user: userData } = response.data;

      localStorage.setItem('token', newToken);
      localStorage.setItem('user', JSON.stringify(userData));
      setToken(newToken);
      setUser(userData);
      setAuthMessage(null);

      // Redirect to the originally requested page or dashboard
      const from = (location.state as {from?: {pathname?: string}})?.from?.pathname || '/dashboard';
      navigate(from, { replace: true });

      return { success: true };
    } catch (error: unknown) {
      const axiosError = error as { response?: { data?: { error?: string } } };
      setAuthMessage(axiosError.response?.data?.error || 'Login failed');
      return { success: false, error: axiosError.response?.data?.error };
    }
  };

  const handlePasswordResetComplete = () => {
    if (user) {
      const updatedUser = { ...user, must_change_password: false };
      setUser(updatedUser);
      localStorage.setItem('user', JSON.stringify(updatedUser));
    }
  };

  const handleLogout = useCallback(() => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setToken(null);
    setUser(null);
    setAuthMessage(null);
    setLogoutCounter(prev => prev + 1);
    navigate('/login', { replace: true });
  }, [navigate]);

  useEffect(() => {
    const interceptor = axios.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          handleLogout();
        }
        return Promise.reject(error);
      }
    );
    return () => axios.interceptors.response.eject(interceptor);
  }, [handleLogout]);

  return (
    <Routes>
      {/* Public route: login */}
      <Route
        path="/login"
        element={
          token ? (
            <Navigate to="/dashboard" replace />
          ) : (
            <Login
              key={`login-${logoutCounter}`}
              onLogin={handleLogin}
              authMessage={authMessage}
              lang={lang}
              setLang={setLang}
              translations={translations}
            />
          )
        }
      />

      {/* Protected shell */}
      <Route
        path="/*"
        element={
          <ProtectedRoute token={token}>
            <div className={`flex h-screen h-[100dvh] w-full overflow-hidden text-slate-800 font-sans transition-colors duration-300 relative`}>
              {/* Sidebar */}
              <aside className={`fixed inset-y-0 left-0 z-[60] w-64 bg-[#111424] text-slate-400 flex flex-col transition-transform duration-300 transform lg:relative lg:translate-x-0 ${mobileMenuOpen ? 'translate-x-0 shadow-2xl' : '-translate-x-full'}`}>
                {/* Mobile Close Button */}
                <button 
                  onClick={() => setMobileMenuOpen(false)}
                  className="lg:hidden absolute top-4 right-4 w-8 h-8 flex items-center justify-center rounded-full bg-slate-800 text-white hover:bg-slate-700 transition-colors"
                >
                  ✕
                </button>
                <div className="p-6 flex flex-col items-center">
                  <div className="flex items-center gap-3 mb-4 w-full justify-center">
                    <div className="w-14 h-14 bg-white rounded-xl flex items-center justify-center p-1 shadow-md border border-slate-100">
                      <img src="/logo.png" alt="Africa Logo" className="w-full h-full object-contain mix-blend-multiply" />
                    </div>
                    <h1 className="text-2xl font-extrabold tracking-tight text-white shadow-sm">ePOM</h1>
                  </div>
                  <div className="bg-[#1e233b] border border-indigo-500/30 text-indigo-200 text-[10px] p-2 rounded-lg text-center font-bold tracking-wider leading-tight w-full uppercase whitespace-pre-line">
                    {t?.nav?.institute || 'Digi\nDelivery'}
                  </div>
                </div>

                <nav className="flex-1 px-3 space-y-1 mt-4 relative">
                  <NavLink onClick={() => setMobileMenuOpen(false)} to="/dashboard" className={({ isActive }) => `flex items-center gap-3 px-4 py-3 rounded-r-2xl transition-all font-medium border-l-4 ${isActive ? 'text-white border-indigo-500 bg-[#1e233b]' : 'border-transparent text-slate-400 hover:text-white hover:bg-slate-800'}`}>
                    <span className="text-lg">📊</span> {t?.nav?.dashboard || 'Dashboard'}
                  </NavLink>
                  <NavLink onClick={() => setMobileMenuOpen(false)} to="/personnel" className={({ isActive }) => `flex items-center gap-3 px-4 py-3 rounded-r-2xl transition-all font-medium border-l-4 ${isActive ? 'text-white border-indigo-500 bg-[#1e233b]' : 'border-transparent text-slate-400 hover:text-white hover:bg-slate-800'}`}>
                    <span className="text-lg">👥</span> {t?.nav?.personnel || 'Personnel'}
                  </NavLink>
                  <NavLink onClick={() => setMobileMenuOpen(false)} to="/calendar" className={({ isActive }) => `flex items-center gap-3 px-4 py-3 rounded-r-2xl transition-all font-medium border-l-4 ${isActive ? 'text-white border-indigo-500 bg-[#1e233b]' : 'border-transparent text-slate-400 hover:text-white hover:bg-slate-800'}`}>
                    <span className="text-lg">📅</span> {t?.nav?.calendar || 'e-time'}
                  </NavLink>
                  <NavLink onClick={() => setMobileMenuOpen(false)} to="/documents" className={({ isActive }) => `flex items-center gap-3 px-4 py-3 rounded-r-2xl transition-all font-medium border-l-4 ${isActive ? 'text-white border-indigo-500 bg-[#1e233b]' : 'border-transparent text-slate-400 hover:text-white hover:bg-slate-800'}`}>
                    <span className="text-lg">📄</span> {t?.nav?.documents || 'e-info'}
                  </NavLink>
                  <NavLink onClick={() => setMobileMenuOpen(false)} to="/actions" className={({ isActive }) => `flex items-center gap-3 px-4 py-3 rounded-r-2xl transition-all font-medium border-l-4 ${isActive ? 'text-white border-indigo-500 bg-[#1e233b]' : 'border-transparent text-slate-400 hover:text-white hover:bg-slate-800'}`}>
                    <span className="text-lg">✅</span> {t?.nav?.actions || 'e-action'}
                  </NavLink>
                  <NavLink onClick={() => setMobileMenuOpen(false)} to="/reports" className={({ isActive }) => `flex items-center gap-3 px-4 py-3 rounded-r-2xl transition-all font-medium border-l-4 ${isActive ? 'text-white border-indigo-500 bg-[#1e233b]' : 'border-transparent text-slate-400 hover:text-white hover:bg-slate-800'}`}>
                    <span className="text-lg">📈</span> {t?.nav?.reports || 'Reports'}
                  </NavLink>
                </nav>

                <div className="p-4 mt-auto">
                  <div className="bg-[#1e233b] rounded-2xl p-3 flex justify-between items-center cursor-pointer hover:bg-[#252b47] transition-colors" onClick={handleLogout}>
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-lg bg-indigo-500 text-white flex items-center justify-center font-bold text-sm">
                        {user?.username?.charAt(0).toUpperCase() || 'A'}
                      </div>
                      <div className="flex flex-col">
                        <span className="text-sm font-bold text-white leading-tight">{user?.username || 'admin'}</span>
                        <span className="text-[10px] text-slate-400 font-bold tracking-wider">{user?.role?.toUpperCase() || 'ADMIN'}</span>
                      </div>
                    </div>
                    <span className="text-orange-400 text-lg">🚪</span>
                  </div>
                </div>
              </aside>

              <div className="flex-1 flex flex-col overflow-hidden">
                {/* Mobile Backdrop */}
                {mobileMenuOpen && (
                  <div
                    className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm z-40 lg:hidden"
                    onClick={() => setMobileMenuOpen(false)}
                  ></div>
                )}

                {/* Top Header */}
                <header className="h-16 px-4 md:px-6 py-4 flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <button
                      onClick={() => setMobileMenuOpen(true)}
                      className="lg:hidden w-9 h-9 flex items-center justify-center rounded-lg bg-white border border-slate-200 text-slate-500 shadow-sm"
                    >
                      ☰
                    </button>
                    <div className="flex items-center gap-2">
                      <span className="w-1.5 h-1.5 rounded-full bg-indigo-600"></span>
                      <h2 className="text-lg font-black text-slate-800 tracking-tight">
                        {(() => {
                          const path = location.pathname;
                          if (path === '/calendar') return t?.nav?.calendar || 'e-time';
                          if (path === '/documents') return t?.nav?.documents || 'e-info';
                          if (path === '/actions') return t?.nav?.actions || 'e-action';
                          if (path === '/personnel') return t?.nav?.personnel || 'Personnel';
                          if (path === '/reports') return t?.nav?.reports || 'Reports';
                          if (path === '/settings') return t?.nav?.settings || 'Settings';
                          if (path === '/reports') return t?.nav?.reports || 'Reports';
                          return t?.nav?.dashboard || 'Dashboard';
                        })()}
                      </h2>
                    </div>
                  </div>

                  <div className="flex-1 max-w-lg mx-4 hidden md:block">
                    <div className="relative flex items-center w-full h-10 rounded-full focus-within:shadow-lg bg-slate-100 overflow-hidden px-4">
                      <div className="grid place-items-center h-full w-6 text-slate-400">
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                        </svg>
                      </div>
                      <input
                        className="peer h-full w-full outline-none text-sm text-slate-700 pr-2 bg-transparent ml-2"
                        type="text"
                        id="search"
                        placeholder={t?.nav?.search || "Search tasks, docs, or personnel.."} />
                    </div>
                  </div>

                  <div className="flex items-center gap-3">
                    <div className="flex rounded-lg border border-slate-200 bg-white overflow-hidden p-0.5 shadow-sm text-xs font-bold shrink-0 items-center">
                      <div className="flex h-full">
                        <button
                          onClick={() => setLang('en')}
                          className={`px-3 py-1 rounded shadow-sm ${lang === 'en' ? 'bg-white text-indigo-600' : 'text-slate-400 hover:text-slate-600 bg-transparent'}`}
                        >EN</button>
                        <button
                          onClick={() => setLang('fr')}
                          className={`px-3 py-1 rounded shadow-sm ${lang === 'fr' ? 'bg-white text-indigo-600' : 'text-slate-400 hover:text-slate-600 bg-transparent'}`}
                        >FR</button>
                      </div>
                      <div className="w-[1px] h-4 bg-slate-200 mx-1"></div>
                      <button
                        onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}
                        className="px-2 py-1 text-base hover:bg-slate-50 transition-colors"
                        title={theme === 'light' ? 'Dark Mode' : 'Light Mode'}
                      >
                        {theme === 'light' ? '🌙' : '☀️'}
                      </button>
                    </div>
                    <div className="relative">
                      <button
                        onClick={() => setShowNotifications(!showNotifications)}
                        className="w-9 h-9 rounded-lg bg-white border border-slate-200 shadow-sm flex items-center justify-center text-amber-500 hover:bg-slate-50 transition-colors relative"
                      >
                        🔔
                        {unreadCount > 0 && (
                          <span className="absolute -top-1 -right-1 bg-red-500 text-white text-[9px] font-bold px-1.5 py-0.5 rounded-full border border-white">
                            {unreadCount}
                          </span>
                        )}
                      </button>

                      {showNotifications && (
                        <div className="absolute right-0 mt-2 w-80 bg-white rounded-2xl shadow-xl border border-slate-100 z-50 overflow-hidden fade-in-up">
                          <div className="p-4 border-b border-slate-100 bg-slate-50/50 flex justify-between items-center">
                            <h3 className="font-bold text-slate-800 text-sm">Notifications</h3>
                            <div className="flex items-center gap-3">
                              {unreadCount > 0 && (
                                <button
                                  onClick={async (e) => {
                                    e.stopPropagation();
                                    const unread = notifications.filter(n => !n.is_read);
                                    try {
                                      await Promise.all(unread.map(n =>
                                        axios.put(`${API_BASE}/notifications/${n.id}/read`, {}, {
                                          headers: { Authorization: `Bearer ${token}` }
                                        })
                                      ));
                                      setNotifications(notifications.map(n => ({ ...n, is_read: true })));
                                    } catch (err: unknown) {
                                      console.error("Failed to bulk mark notifications as read", err);
                                    }
                                  }}
                                  className="text-[10px] font-black uppercase tracking-widest text-indigo-600 hover:text-indigo-800 transition-colors"
                                >
                                  Mark all as read
                                </button>
                              )}
                              {unreadCount > 0 && <span className="text-xs text-indigo-600 font-bold bg-indigo-50 px-2 py-0.5 rounded-full">{unreadCount}</span>}
                            </div>
                          </div>
                          <div className="max-h-80 overflow-y-auto">
                            {notifications.length === 0 ? (
                              <div className="p-6 text-center text-slate-400 text-sm font-medium">No notifications</div>
                            ) : (
                              <div className="divide-y divide-slate-50">
                                {notifications.map(notif => (
                                  <div
                                    key={notif.id}
                                    onClick={() => handleNotificationClick(notif)}
                                    className={`p-4 cursor-pointer hover:bg-slate-50 transition-colors ${!notif.is_read ? 'bg-indigo-50/30' : ''}`}
                                  >
                                    <div className="flex gap-3">
                                      <div className="text-xl mt-0.5">{!notif.is_read ? '🔹' : '🔸'}</div>
                                      <div>
                                        <p className={`text-sm ${!notif.is_read ? 'font-bold text-slate-800' : 'text-slate-600 font-medium'}`}>
                                          {notif.message}
                                        </p>
                                        <p className="text-[10px] text-slate-400 mt-1 uppercase tracking-widest font-bold">
                                          {new Date(notif.created_at).toLocaleString()}
                                        </p>
                                      </div>
                                    </div>
                                  </div>
                                ))}
                              </div>
                            )}
                          </div>
                        </div>
                      )}
                    </div>
                    {user?.role === 'Admin' && (
                      <button
                        onClick={() => navigate('/settings')}
                        className="w-9 h-9 rounded-lg bg-white border border-slate-200 shadow-sm flex items-center justify-center text-slate-500 hover:bg-slate-50 transition-colors"
                        title={t?.nav?.settings || 'Settings'}
                      >
                        ⚙️
                      </button>
                    )}
                  </div>
                </header>

                {/* Mandatory Password Change Overlay */}
                {user?.must_change_password && (
                  <div className="fixed inset-0 z-[1000] bg-slate-950/80 backdrop-blur-xl flex items-center justify-center p-6">
                    <div className="w-full max-w-md bg-white rounded-[32px] shadow-2xl p-10 scale-in-center">
                      <div className="w-16 h-16 bg-red-100 text-red-600 rounded-2xl flex items-center justify-center text-3xl mb-6 mx-auto">🔐</div>
                      <h3 className="text-2xl font-black text-slate-800 text-center tracking-tight mb-2 uppercase">Initial Entry Protocol</h3>
                      <p className="text-slate-500 text-center text-xs font-medium mb-8 leading-relaxed uppercase tracking-wider">
                        {lang === 'fr' ? 'Directive : Veuillez modifier votre mot de passe pour des raisons de sécurité avant de continuer.' : 'Directive: You must update your access credentials for security compliance before proceeding.'}
                      </p>
                      
                      <form onSubmit={async (e) => {
                          e.preventDefault();
                          const formData = new FormData(e.currentTarget);
                          const newPassword = formData.get('new_password') as string;
                          const confirmPassword = formData.get('confirm_password') as string;
                          
                          if (!newPassword || newPassword.length < 6) {
                            alert(lang === 'fr' ? 'Le mot de passe doit faire au moins 6 caractères.' : 'Password must be at least 6 characters.');
                            return;
                          }
                          if (newPassword !== confirmPassword) {
                            alert(lang === 'fr' ? 'Les mots de passe ne correspondent pas.' : 'Passwords do not match.');
                            return;
                          }
                          
                          try {
                            await axios.put(`${API_BASE}/users/${user.id}`, { password: newPassword }, {
                              headers: { Authorization: `Bearer ${token}` }
                            });
                            handlePasswordResetComplete();
                          } catch (err: any) {
                            alert(err.response?.data?.error || "Update failure");
                          }
                        }} className="space-y-4">
                        <div className="relative">
                          <input 
                            required name="new_password" type={showResetPassword ? "text" : "password"}
                            placeholder={lang === 'fr' ? 'Nouveau mot de passe' : 'New Password'}
                            className="w-full px-6 py-4 bg-slate-50 border-0 rounded-2xl focus:ring-2 focus:ring-indigo-500 outline-none font-bold pr-14"
                          />
                          <button 
                            type="button" 
                            onClick={() => setShowResetPassword(!showResetPassword)}
                            className="absolute right-5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 transition-colors"
                          >
                            {showResetPassword ? (
                              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l18 18" /></svg>
                            ) : (
                              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" /></svg>
                            )}
                          </button>
                        </div>
                        <div className="relative">
                          <input 
                            required name="confirm_password" type={showResetPassword ? "text" : "password"}
                            placeholder={lang === 'fr' ? 'Confirmer le mot de passe' : 'Confirm Password'}
                            className="w-full px-6 py-4 bg-slate-50 border-0 rounded-2xl focus:ring-2 focus:ring-indigo-500 outline-none font-bold pr-14"
                          />
                        </div>
                        <button type="submit" className="w-full py-4.5 bg-indigo-600 text-white rounded-2xl font-black uppercase tracking-widest text-xs shadow-xl shadow-indigo-100 mt-4 active:scale-95 transition-all">
                          Update Credentials
                        </button>
                      </form>
                    </div>
                  </div>
                )}

                {/* Main scrollable view */}
                <main className="flex-1 overflow-y-auto p-4 md:p-6 lg:px-8 lg:py-4 space-y-6">
                  <Routes>
                    <Route path="/" element={<Navigate to="/dashboard" replace />} />
                    <Route path="/dashboard" element={
                      <Dashboard
                        user={user}
                        token={token}
                        lang={lang}
                        translations={translations}
                      />
                    } />
                    <Route path="/calendar" element={
                      <Calendar
                        user={user}
                        token={token}
                        lang={lang}
                        translations={translations}
                      />
                    } />
                    <Route path="/documents" element={
                      <Documents
                        user={user}
                        token={token}
                        lang={lang}
                        translations={translations}
                      />
                    } />
                    <Route path="/actions" element={
                      <Actions
                        user={user}
                        token={token}
                        lang={lang}
                        translations={translations}
                      />
                    } />
                    <Route path="/personnel" element={
                      <Users
                        user={user}
                        token={token}
                        lang={lang}
                        translations={translations}
                      />
                    } />
                    <Route path="/reports" element={
                      <Reports
                        user={user}
                        token={token}
                        lang={lang}
                        translations={translations}
                      />
                    } />
                    <Route path="/settings" element={
                      user?.role === 'Admin' ? (
                        <Settings
                          user={user}
                          token={token}
                          setUser={setUser}
                          lang={lang}
                          setLang={setLang}
                          translations={translations}
                          theme={theme}
                          setTheme={setTheme}
                        />
                      ) : <Navigate to="/" />
                    } />
                  </Routes>
                </main>
              </div>
            </div>
          </ProtectedRoute>
        }
      />
    </Routes>
  );
}

export default App;