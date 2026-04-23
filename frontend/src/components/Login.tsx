import { useState, useEffect } from 'react';
import axios from 'axios';

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const Login = ({ onLogin, authMessage, lang, setLang, translations }: { onLogin: (u: string, p: string) => Promise<any>, authMessage: string | null, lang: 'en' | 'fr', setLang: (l: 'en' | 'fr') => void, translations: Record<string, any> }) => {
  const t = translations?.[lang]?.auth || translations?.['en']?.auth || {};
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  // MFA States
  const [showMfa, setShowMfa] = useState(false);
  const [mfaCode, setMfaCode] = useState('');
  const [mfaUserId, setMfaUserId] = useState<number | null>(null);
  const [mfaChallenge, setMfaChallenge] = useState('');
  const [internalError, setInternalError] = useState('');
  const [mfaTimer, setMfaTimer] = useState(300); // 5 minutes
  const [mfaTimerActive, setMfaTimerActive] = useState(false);

  const [isRegistering, setIsRegistering] = useState(false);
  const [regData, setRegData] = useState({ username: '', email: '', password: '', first_name: '', last_name: '', department: '' });

  // Clear form on every mount (e.g. after logout)
  useEffect(() => {
    setUsername('');
    setPassword('');
    setShowPassword(false);
    setShowMfa(false);
    setMfaCode('');
    setMfaUserId(null);
    setMfaChallenge('');
    setInternalError('');
    setMfaTimer(300);
    setMfaTimerActive(false);
  }, []);

  // MFA Timer countdown effect
  useEffect(() => {
    let interval: number;
    if (mfaTimerActive && mfaTimer > 0) {
      interval = window.setInterval(() => {
        setMfaTimer((prev) => {
          if (prev <= 1) {
            setMfaTimerActive(false);
            setInternalError('Verification code expired. Please request a new code.');
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    }
    return () => window.clearInterval(interval);
  }, [mfaTimerActive, mfaTimer]);

  // Start MFA timer when MFA is shown
  useEffect(() => {
    if (showMfa) {
      setMfaTimer(300);
      setMfaTimerActive(true);
    } else {
      setMfaTimerActive(false);
    }
  }, [showMfa]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setInternalError('');

    const result = await onLogin(username, password);

    if (result?.mfa_required) {
      setMfaUserId(result.user_id);
      setMfaChallenge(result.message);
      setShowMfa(true);
    } else if (result?.success === false) {
      // Login failed - show error message
      setInternalError(result.error || 'Login failed');
    }
    // If login succeeds, the onLogin function in App.tsx handles navigation

    setIsLoading(false);
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setInternalError('');
    try {
      await axios.post('/api/auth/register', regData);
      setIsRegistering(false);
      setUsername(regData.username);
      alert(lang === 'fr' ? 'Compte créé avec succès ! Connectez-vous maintenant.' : 'Account created successfully! Please login now.');
    } catch (err: any) {
      setInternalError(err.response?.data?.error || 'Registration failed');
    } finally {
      setIsLoading(false);
    }
  };

  const handleMfaSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setInternalError('');

    try {
      const response = await axios.post('/api/auth/mfa/verify', {
        user_id: mfaUserId,
        code: mfaCode
      });

      const { token, user } = response.data;

      // Manually trigger the app state update since we bypassed handleLogin redirection
      localStorage.setItem('token', token);
      localStorage.setItem('user', JSON.stringify(user));
      window.location.href = '/dashboard';
    } catch (error: unknown) {
      if (axios.isAxiosError(error) && error.response?.data?.error) {
        setInternalError(error.response.data.error);
      } else {
        setInternalError(t.error_generic || "Authentication failed. Please verify credentials.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleResendCode = async () => {
    setIsLoading(true);
    setInternalError('');
    
    try {
      // Request new MFA code by logging in again
      const result = await onLogin(username, password);
      
      if (result?.mfa_required) {
        setMfaTimer(300);
        setMfaTimerActive(true);
        setMfaCode('');
        setInternalError('New verification code sent to your device');
      } else {
        setInternalError('Failed to generate new verification code');
      }
    } catch (error: unknown) {
      setInternalError('Failed to resend verification code');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="glass premium-card w-full max-w-md p-8 md:p-10 fade-in-up animate-float relative overflow-hidden">
        {/* Decorative glowing orb in the card */}
        <div className="absolute -top-20 -right-20 w-40 h-40 bg-indigo-400/20 rounded-full blur-3xl"></div>
        <div className="absolute -bottom-20 -left-20 w-40 h-40 bg-purple-400/20 rounded-full blur-3xl"></div>

        <div className="relative z-10">
          <div className="flex justify-end mb-4">
            <div className="flex rounded-lg border border-slate-200 bg-white/40 overflow-hidden p-0.5 shadow-sm text-[10px] font-bold shrink-0">
              <button
                type="button"
                onClick={() => setLang('en')}
                className={`px-3 py-1 rounded shadow-sm transition-all ${lang === 'en' ? 'bg-white text-indigo-600' : 'text-slate-500 hover:text-slate-700 bg-transparent'}`}
              >EN</button>
              <button
                type="button"
                onClick={() => setLang('fr')}
                className={`px-3 py-1 rounded shadow-sm transition-all ${lang === 'fr' ? 'bg-white text-indigo-600' : 'text-slate-500 hover:text-slate-700 bg-transparent'}`}
              >FR</button>
            </div>
          </div>
          <div className="text-center mb-10">
            <div className="w-24 h-24 bg-white/80 rounded-[32px] mx-auto mb-8 flex items-center justify-center p-3 shadow-2xl border border-white/50 backdrop-blur-2xl transform hover:scale-105 transition-all duration-500 group">
              <img src="/logo.png" alt="ePOM Strategic Logo" className="w-full h-full object-contain mix-blend-multiply group-hover:scale-110 transition-transform duration-500" />
            </div>
            <h1 className="text-4xl font-black text-slate-800 tracking-tight mb-2">ePOM</h1>
            <p className="text-slate-500 font-bold text-xs uppercase tracking-[0.2em] opacity-60">
              {isRegistering ? (lang === 'fr' ? 'CRÉER UN COMPTE' : 'CREATE ACCOUNT') : (t.subtitle || 'Operational Management Interface')}
            </p>
          </div>

          {(authMessage || internalError) && (
            <div className="mb-6 p-4 bg-red-500/10 border border-red-500/20 rounded-xl text-red-600 text-sm font-semibold text-center shimmer">
              {authMessage || internalError}
            </div>
          )}

          {showMfa ? (
            <div className="fade-in">
              {/* MFA Header */}
              <div className="text-center mb-8">
                <div className="w-16 h-16 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-2xl mx-auto mb-4 flex items-center justify-center shadow-lg">
                  <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                  </svg>
                </div>
                <h2 className="text-2xl font-bold text-slate-800 mb-2">Two-Factor Authentication</h2>
                <p className="text-slate-500 text-sm">Enter the verification code to secure your access</p>
              </div>

              {/* MFA Challenge Message */}
              <div className="bg-gradient-to-r from-indigo-50 to-purple-50 border border-indigo-200 rounded-xl p-4 mb-6">
                <div className="flex items-start gap-3">
                  <div className="w-6 h-6 bg-indigo-500 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                    <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-indigo-800 mb-1">Security Challenge</p>
                    <p className="text-xs text-indigo-700 leading-relaxed">
                      {mfaChallenge}
                    </p>
                  </div>
                </div>
              </div>

              <form onSubmit={handleMfaSubmit} className="space-y-6">
                {/* MFA Code Input */}
                <div>
                  <label className="block text-sm font-bold text-slate-700 mb-3 flex items-center gap-2">
                    <svg className="w-4 h-4 text-indigo-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    Verification Code
                  </label>
                  <div className="relative">
                    <input
                      type="text"
                      maxLength={6}
                      placeholder="000000"
                      value={mfaCode}
                      onChange={(e) => setMfaCode(e.target.value.replace(/\D/g, ''))}
                      className="w-full px-6 py-4 rounded-2xl border-2 border-indigo-200 bg-white text-center text-3xl font-black tracking-[0.5em] text-slate-800 focus:bg-white focus:outline-none focus:ring-4 focus:ring-indigo-400/20 focus:border-indigo-400 transition-all shadow-lg"
                      required
                      autoFocus
                    />
                    {mfaCode.length === 6 && (
                      <div className="absolute right-4 top-1/2 -translate-y-1/2">
                        <div className="w-6 h-6 bg-green-500 rounded-full flex items-center justify-center">
                          <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                          </svg>
                        </div>
                      </div>
                    )}
                  </div>
                  <p className="text-xs text-slate-500 mt-2 text-center">Enter the 6-digit code sent to your device</p>
                </div>

                {/* Timer and Security Info */}
                <div className="space-y-3">
                  {/* Countdown Timer */}
                  <div className={`rounded-xl p-4 border ${mfaTimer <= 60 ? 'bg-red-50 border-red-200' : 'bg-slate-50 border-slate-200'}`}>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center ${mfaTimer <= 60 ? 'bg-red-500' : 'bg-indigo-500'}`}>
                          <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                        </div>
                        <div>
                          <p className="text-xs font-semibold text-slate-700">Code expires in</p>
                          <p className={`text-lg font-bold ${mfaTimer <= 60 ? 'text-red-600' : 'text-indigo-600'}`}>
                            {Math.floor(mfaTimer / 60)}:{(mfaTimer % 60).toString().padStart(2, '0')}
                          </p>
                        </div>
                      </div>
                      {mfaTimer <= 60 && (
                        <div className="text-xs text-red-600 font-semibold animate-pulse">
                          Expiring Soon!
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Demo Code Info */}
                  <div className="bg-slate-50 rounded-xl p-4 border border-slate-200">
                    <div className="flex items-center gap-3 text-xs text-slate-600">
                      <svg className="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <span>For demo purposes, use code: <strong className="text-indigo-600">123456</strong></span>
                    </div>
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="space-y-3">
                  <button
                    type="submit"
                    disabled={isLoading || mfaCode.length !== 6}
                    className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-bold py-4 px-6 rounded-2xl shadow-lg hover:from-indigo-700 hover:to-purple-700 hover:-translate-y-1 transition-all active:scale-95 disabled:opacity-70 disabled:cursor-not-allowed flex justify-center items-center gap-2"
                  >
                    {isLoading ? (
                      <>
                        <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                        Verifying...
                      </>
                    ) : (
                      <>
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        Verify & Access System
                      </>
                    )}
                  </button>

                  <div className="flex gap-3">
                    <button
                      type="button"
                      onClick={() => {
                        setShowMfa(false);
                        setMfaCode('');
                        setInternalError('');
                      }}
                      className="flex-1 text-slate-400 text-xs font-bold uppercase tracking-widest hover:text-indigo-600 transition-colors py-2"
                    >
                      ← Back to Login
                    </button>
                    <button
                      type="button"
                      onClick={handleResendCode}
                      disabled={isLoading}
                      className="flex-1 text-indigo-600 text-xs font-bold uppercase tracking-widest hover:text-indigo-700 transition-colors py-2 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {isLoading ? 'Sending...' : 'Resend Code'}
                    </button>
                  </div>
                </div>
              </form>
            </div>
          ) : isRegistering ? (
            <form onSubmit={handleRegister} className="space-y-4 fade-in">
              <div className="grid grid-cols-2 gap-3">
                <input
                  placeholder={lang === 'fr' ? 'Prénom' : 'First Name'}
                  value={regData.first_name}
                  onChange={(e) => setRegData({ ...regData, first_name: e.target.value })}
                  className="w-full px-4 py-3 rounded-xl border border-white/40 bg-white/40 text-slate-800 focus:bg-white/70 outline-none transition-all"
                />
                <input
                  placeholder={lang === 'fr' ? 'Nom' : 'Last Name'}
                  value={regData.last_name}
                  onChange={(e) => setRegData({ ...regData, last_name: e.target.value })}
                  className="w-full px-4 py-3 rounded-xl border border-white/40 bg-white/40 text-slate-800 focus:bg-white/70 outline-none transition-all"
                />
              </div>
              <input
                required
                placeholder={t.username || 'Username'}
                value={regData.username}
                onChange={(e) => setRegData({ ...regData, username: e.target.value })}
                className="w-full px-4 py-3 rounded-xl border border-white/40 bg-white/40 text-slate-800 focus:bg-white/70 outline-none transition-all"
              />
              <input
                required
                type="email"
                placeholder={t.email || 'Email'}
                value={regData.email}
                onChange={(e) => setRegData({ ...regData, email: e.target.value })}
                className="w-full px-4 py-3 rounded-xl border border-white/40 bg-white/40 text-slate-800 focus:bg-white/70 outline-none transition-all"
              />
              <input
                required
                type="password"
                placeholder={t.password || 'Password'}
                value={regData.password}
                onChange={(e) => setRegData({ ...regData, password: e.target.value })}
                className="w-full px-4 py-3 rounded-xl border border-white/40 bg-white/40 text-slate-800 focus:bg-white/70 outline-none transition-all"
              />
              <button
                type="submit"
                disabled={isLoading}
                className="w-full bg-indigo-600 text-white font-bold py-3 px-6 rounded-xl shadow-lg hover:bg-indigo-700 transition-all disabled:opacity-70"
              >
                {isLoading ? '...' : (lang === 'fr' ? "S'inscrire" : 'Register Account')}
              </button>
              <button
                type="button"
                onClick={() => setIsRegistering(false)}
                className="w-full text-slate-400 text-xs font-bold uppercase tracking-widest hover:text-indigo-600 transition-colors pt-2"
              >
                Already have an account? Login
              </button>
            </form>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-2 ml-1" htmlFor="username">
                  {t.username || 'Username'}
                </label>
                <input
                  id="username"
                  type="text"
                  placeholder={t.user_ph || "Enter your username"}
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="w-full px-5 py-4 rounded-2xl border border-white/40 bg-white/40 text-slate-800 placeholder:text-slate-400 focus:bg-white/70 focus:outline-none focus:ring-4 focus:ring-indigo-400/20 backdrop-blur-md transition-all shadow-sm"
                  required
                  autoComplete="username"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-2 ml-1" htmlFor="password">
                  {t.password || 'Password'}
                </label>
                <div className="relative">
                  <input
                    id="password"
                    type={showPassword ? "text" : "password"}
                    placeholder="••••••••"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full px-5 py-4 rounded-2xl border border-white/40 bg-white/40 text-slate-800 placeholder:text-slate-400 focus:bg-white/70 focus:outline-none focus:ring-4 focus:ring-indigo-400/20 backdrop-blur-md transition-all shadow-sm"
                    required
                    autoComplete="current-password"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-400 hover:text-indigo-600 transition-colors p-2"
                  >
                    {showPassword ? (
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l18 18"></path></svg>
                    ) : (
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path></svg>
                    )}
                  </button>
                </div>
              </div>

              <button
                type="submit"
                disabled={isLoading}
                className="w-full mt-8 bg-gradient-to-r from-indigo-500 to-purple-600 text-white font-bold py-4 px-6 rounded-2xl shadow-lg shadow-indigo-500/30 hover:shadow-indigo-500/50 hover:-translate-y-1 transition-all active:scale-95 disabled:opacity-70 flex justify-center items-center"
              >
                {isLoading ? (
                  <div className="w-6 h-6 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                ) : (
                  t.auth_btn || "Authenticate"
                )}
              </button>
            </form>
          )}

          <div className="mt-8 text-center">
            <p className="text-xs text-slate-400 font-medium tracking-wider uppercase">{t.secure || 'Secure Gateway'}</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
