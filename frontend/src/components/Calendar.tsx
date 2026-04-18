import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import type { User } from '../App';

interface Resource {
  id: number;
  name: string;
  type: string;
  capacity?: number;
  is_available: boolean;
}

interface CalendarEvent {
  id: number;
  title: string;
  description: string;
  start_time: string;
  end_time: string;
  priority: string;
  user_id: number;
  location?: string;
  meeting_link?: string;
  resource_id?: number;
  mandatory_attendees: string;
}

interface CalendarProps {
  user: User | null;
  lang: 'en' | 'fr';
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  translations: Record<string, any>;
  token: string | null;
}

const PRIORITY_STYLES: Record<string, string> = {
  Critical: 'bg-red-50 text-red-600 border-red-400',
  High:     'bg-amber-50 text-amber-600 border-amber-400',
  Medium:   'bg-indigo-50 text-indigo-600 border-indigo-400',
  Low:      'bg-slate-50 text-slate-500 border-slate-300',
};

const Calendar = ({ lang, translations, token }: CalendarProps) => {
  const t = translations?.[lang]?.calendar || translations?.['en']?.calendar || {};
  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [users, setUsers] = useState<{id: number, username: string, first_name?: string, last_name?: string, role: string}[]>([]);
  const [resources, setResources] = useState<Resource[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);
  const [currentMonth, setCurrentMonth] = useState(new Date().getMonth());
  const [currentYear, setCurrentYear] = useState(new Date().getFullYear());
  const [error, setError] = useState('');
  const [selectedDay, setSelectedDay] = useState<number | null>(null);
  // mobile vs grid view
  const [view, setView] = useState<'grid' | 'list'>('grid');

  const [formData, setFormData] = useState({
    title: '',
    description: '',
    start_time: '',
    end_time: '',
    priority: 'Medium',
    location: '',
    meeting_link: '',
    resource_id: '',
    mandatory_attendees: [] as string[],
    optional_attendees: [] as string[],
  });

  const fetchData = useCallback(async () => {
    if (!token) return;
    try {
      setLoading(true);
      const [eventsRes, usersRes, resourcesRes] = await Promise.all([
        axios.get(`/api/calendar`, { headers: { Authorization: `Bearer ${token}` } }),
        axios.get(`/api/users`,    { headers: { Authorization: `Bearer ${token}` } }),
        axios.get(`/api/resources`,{ headers: { Authorization: `Bearer ${token}` } }),
      ]);
      setEvents(eventsRes.data);
      setUsers(usersRes.data);
      setResources(resourcesRes.data);
    } catch (err) {
      console.error('Failed to fetch calendar data', err);
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => { fetchData(); }, [fetchData]);

  const toggleAttendee = (type: 'mandatory' | 'optional', userId: string) => {
    const key  = type === 'mandatory' ? 'mandatory_attendees' : 'optional_attendees';
    const other = type === 'mandatory' ? 'optional_attendees' : 'mandatory_attendees';
    const current = formData[key];
    const isSelected = current.includes(userId);
    setFormData(prev => ({
      ...prev,
      [key]:  isSelected ? current.filter(id => id !== userId) : [...current, userId],
      [other]: prev[other].filter(id => id !== userId),
    }));
  };

  const resetForm = () => {
    setFormData({ title: '', description: '', start_time: '', end_time: '', priority: 'Medium',
      location: '', meeting_link: '', resource_id: '', mandatory_attendees: [], optional_attendees: [] });
    setError('');
  };

  const handleAddEvent = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token) return;
    setError('');
    const start_iso = new Date(formData.start_time);
    const end_iso   = new Date(formData.end_time);
    if (end_iso <= start_iso) {
      setError(lang === 'fr' ? "L'heure de fin doit être après l'heure de début" : 'End time must be after start time');
      return;
    }
    try {
      await axios.post(`/api/calendar`, { ...formData, start_time: start_iso.toISOString(), end_time: end_iso.toISOString() },
        { headers: { Authorization: `Bearer ${token}` } });
      resetForm();
      setShowAddForm(false);
      fetchData();
    } catch (err: unknown) {
      const axiosError = err as { response?: { data?: { error?: string } } };
      setError(axiosError.response?.data?.error || (lang === 'fr' ? 'Conflit détecté.' : 'Smart scheduling detected a conflict.'));
    }
  };

  const downloadICS = (event: CalendarEvent) => {
    const start = new Date(event.start_time).toISOString().replace(/-|:|\.\d+/g, '');
    const end   = new Date(event.end_time).toISOString().replace(/-|:|\.\d+/g, '');
    const ics = [
      'BEGIN:VCALENDAR','VERSION:2.0','BEGIN:VEVENT',
      `SUMMARY:${event.title}`,
      `DESCRIPTION:${event.description || ''}`,
      `DTSTART:${start}`,`DTEND:${end}`,
      `LOCATION:${event.location || ''}`,`URL:${event.meeting_link || ''}`,
      'END:VEVENT','END:VCALENDAR',
    ].join('\n');
    const blob = new Blob([ics], { type: 'text/calendar;charset=utf-8' });
    const link = document.createElement('a');
    link.href = window.URL.createObjectURL(blob);
    link.setAttribute('download', `${event.title.replace(/\s+/g, '_')}.ics`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const goToPrev = () => {
    if (currentMonth === 0) { setCurrentMonth(11); setCurrentYear(y => y - 1); }
    else setCurrentMonth(m => m - 1);
  };
  const goToNext = () => {
    if (currentMonth === 11) { setCurrentMonth(0); setCurrentYear(y => y + 1); }
    else setCurrentMonth(m => m + 1);
  };
  const goToToday = () => { setCurrentMonth(new Date().getMonth()); setCurrentYear(new Date().getFullYear()); };

  // Month events sorted for list view
  const monthEvents = events
    .filter(ev => {
      const d = new Date(ev.start_time);
      return d.getMonth() === currentMonth && d.getFullYear() === currentYear;
    })
    .sort((a, b) => new Date(a.start_time).getTime() - new Date(b.start_time).getTime());

  const dayNames = lang === 'fr'
    ? ['LUN', 'MAR', 'MER', 'JEU', 'VEN', 'SAM', 'DIM']
    : ['SUN', 'MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT'];

  const startOnMonday = lang === 'fr';
  let firstDay = new Date(currentYear, currentMonth, 1).getDay();
  if (startOnMonday) firstDay = firstDay === 0 ? 6 : firstDay - 1;
  const daysInMonth = new Date(currentYear, currentMonth + 1, 0).getDate();

  // selected-day events
  const selectedDayEvents = selectedDay !== null
    ? events.filter(ev => new Date(ev.start_time).toDateString() === new Date(currentYear, currentMonth, selectedDay).toDateString())
    : [];

  return (
    <div className="space-y-4">

      {/* ─── Add Event Modal ─────────────────────────────────── */}
      {showAddForm && (
        <div className="fixed inset-0 z-[100] flex items-end sm:items-center justify-center p-0 sm:p-4">
          <div className="absolute inset-0 bg-slate-950/70 backdrop-blur-md" onClick={() => { setShowAddForm(false); resetForm(); }} />
          <div className="relative w-full sm:max-w-2xl bg-white sm:rounded-[32px] rounded-t-[32px] shadow-2xl flex flex-col max-h-[92vh] overflow-hidden scale-in-center">

            {/* Modal Header */}
            <div className="bg-slate-900 px-6 py-5 text-white flex items-center justify-between shrink-0">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-white/10 rounded-2xl flex items-center justify-center text-xl border border-white/10">📅</div>
                <div>
                  <h3 className="font-black text-base tracking-tight uppercase">{t.form_title || 'Schedule Meeting'}</h3>
                  <p className="text-[10px] text-blue-400 font-bold uppercase tracking-widest flex items-center gap-1">
                    <span className="w-1.5 h-1.5 rounded-full bg-blue-500 animate-pulse inline-block" />
                    Conflict Engine Active
                  </p>
                </div>
              </div>
              <button onClick={() => { setShowAddForm(false); resetForm(); }}
                className="w-9 h-9 flex items-center justify-center rounded-xl hover:bg-white/10 text-slate-400 hover:text-white transition-all">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {error && (
              <div className="mx-4 mt-3 text-xs text-red-500 bg-red-50 px-4 py-3 rounded-2xl font-bold border border-red-100 shrink-0">
                ⚠️ {error}
              </div>
            )}

            {/* Scrollable form body */}
            <form onSubmit={handleAddEvent} className="flex-1 overflow-y-auto custom-scrollbar">
              <div className="p-5 space-y-4">
                <div className="space-y-1.5">
                  <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Subject</label>
                  <input required type="text" value={formData.title}
                    onChange={e => setFormData({ ...formData, title: e.target.value })}
                    className="w-full px-4 py-3 bg-slate-50 border-0 rounded-2xl focus:ring-2 focus:ring-indigo-500 outline-none font-bold text-slate-800"
                    placeholder="e.g. Team Briefing" />
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div className="space-y-1.5">
                    <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Start</label>
                    <input required type="datetime-local" value={formData.start_time}
                      onChange={e => setFormData({ ...formData, start_time: e.target.value })}
                      className="w-full px-4 py-3 bg-slate-50 border-0 rounded-2xl focus:ring-2 focus:ring-indigo-500 outline-none font-bold" />
                  </div>
                  <div className="space-y-1.5">
                    <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest">End</label>
                    <input required type="datetime-local" value={formData.end_time}
                      onChange={e => setFormData({ ...formData, end_time: e.target.value })}
                      className="w-full px-4 py-3 bg-slate-50 border-0 rounded-2xl focus:ring-2 focus:ring-indigo-500 outline-none font-bold" />
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div className="space-y-1.5">
                    <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Room / Resource</label>
                    <select value={formData.resource_id}
                      onChange={e => setFormData({ ...formData, resource_id: e.target.value })}
                      className="w-full px-4 py-3 bg-slate-50 border-0 rounded-2xl focus:ring-2 focus:ring-indigo-500 outline-none font-bold">
                      <option value="">{lang === 'fr' ? 'Aucune salle' : 'No Room'}</option>
                      {resources.map(r => <option key={r.id} value={r.id}>{r.name} ({r.capacity} pax)</option>)}
                    </select>
                  </div>
                  <div className="space-y-1.5">
                    <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Location</label>
                    <input type="text" value={formData.location}
                      onChange={e => setFormData({ ...formData, location: e.target.value })}
                      className="w-full px-4 py-3 bg-slate-50 border-0 rounded-2xl focus:ring-2 focus:ring-indigo-500 outline-none font-bold"
                      placeholder="Remote / Zoom" />
                  </div>
                </div>

                <div className="space-y-1.5">
                  <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest">
                    {lang === 'fr' ? 'Priorité' : 'Priority'}
                  </label>
                  <div className="grid grid-cols-4 gap-2">
                    {(['Low', 'Medium', 'High', 'Critical'] as const).map(p => {
                      const styles: Record<string, string> = {
                        Low:      'border-slate-300 text-slate-500 bg-slate-50',
                        Medium:   'border-indigo-400 text-indigo-600 bg-indigo-50',
                        High:     'border-amber-400 text-amber-600 bg-amber-50',
                        Critical: 'border-red-400 text-red-600 bg-red-50',
                      };
                      const activeRing: Record<string, string> = {
                        Low: 'ring-2 ring-slate-400', Medium: 'ring-2 ring-indigo-500',
                        High: 'ring-2 ring-amber-500', Critical: 'ring-2 ring-red-500',
                      };
                      const isSelected = formData.priority === p;
                      const label = lang === 'fr' ? { Low: 'Faible', Medium: 'Moyen', High: 'Haut', Critical: 'Critique' }[p] : p;
                      return (
                        <button key={p} type="button"
                          onClick={() => setFormData({ ...formData, priority: p })}
                          className={`py-2.5 rounded-xl border text-[10px] font-black uppercase tracking-wide transition-all ${styles[p]} ${isSelected ? activeRing[p] + ' scale-105 shadow-md' : 'opacity-60 hover:opacity-100'}`}>
                          {label}
                        </button>
                      );
                    })}
                  </div>
                </div>

                <div className="space-y-1.5">
                  <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Meeting Link</label>
                  <input type="url" value={formData.meeting_link}
                    onChange={e => setFormData({ ...formData, meeting_link: e.target.value })}
                    className="w-full px-4 py-3 bg-slate-50 border-0 rounded-2xl focus:ring-2 focus:ring-indigo-500 outline-none font-bold"
                    placeholder="https://zoom.us/j/..." />
                </div>

                <div className="space-y-1.5">
                  <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Agenda</label>
                  <textarea rows={3} value={formData.description}
                    onChange={e => setFormData({ ...formData, description: e.target.value })}
                    className="w-full px-4 py-3 bg-slate-50 border-0 rounded-2xl focus:ring-2 focus:ring-indigo-500 outline-none font-medium resize-none" />
                </div>

                {/* Attendees */}
                <div className="space-y-2">
                  <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Attendees</label>
                  <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 max-h-40 overflow-y-auto custom-scrollbar pr-1">
                    {users.map(u => {
                      const uid = String(u.id);
                      const isMandatory = formData.mandatory_attendees.includes(uid);
                      return (
                        <div key={u.id}
                          className={`flex items-center gap-2 p-3 rounded-2xl border transition-all cursor-pointer ${isMandatory ? 'bg-indigo-600 border-transparent' : 'bg-white border-slate-100 hover:border-slate-300'}`}
                          onClick={() => toggleAttendee('mandatory', uid)}>
                          <div className={`w-7 h-7 rounded-lg flex items-center justify-center text-[10px] font-black shrink-0 ${isMandatory ? 'bg-white/20 text-white' : 'bg-slate-100 text-slate-400'}`}>
                            {(u.first_name?.[0] || u.username[0] || '?').toUpperCase()}
                          </div>
                          <div className="flex-1 min-w-0">
                            <p className={`text-[10px] font-black truncate ${isMandatory ? 'text-white' : 'text-slate-800'}`}>
                              {u.first_name ? `${u.first_name}` : u.username}
                            </p>
                            <p className={`text-[9px] font-bold uppercase truncate ${isMandatory ? 'text-indigo-200' : 'text-slate-400'}`}>{u.role}</p>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>

              {/* Footer */}
              <div className="sticky bottom-0 bg-white border-t border-slate-100 px-5 py-4 flex gap-3">
                <button type="button" onClick={() => { setShowAddForm(false); resetForm(); }}
                  className="flex-1 py-3 text-slate-500 font-black uppercase tracking-widest text-xs border border-slate-200 rounded-2xl hover:bg-slate-50 transition-all">
                  {lang === 'fr' ? 'Annuler' : 'Cancel'}
                </button>
                <button type="submit"
                  className="flex-1 py-3 bg-slate-900 text-white rounded-2xl font-black uppercase tracking-widest text-xs shadow-xl active:scale-95 transition-all">
                  {lang === 'fr' ? 'Confirmer' : 'Commit'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ─── Selected Day Events Drawer ─────────────────────────── */}
      {selectedDay !== null && selectedDayEvents.length > 0 && (
        <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-0 sm:p-4">
          <div className="absolute inset-0 bg-slate-950/50 backdrop-blur-sm" onClick={() => setSelectedDay(null)} />
          <div className="relative w-full sm:max-w-sm bg-white rounded-t-[28px] sm:rounded-[28px] shadow-2xl p-5 max-h-[60vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h4 className="font-black text-slate-800 text-sm uppercase tracking-wide">
                {new Date(currentYear, currentMonth, selectedDay).toLocaleDateString(lang === 'fr' ? 'fr-FR' : 'en-US', { weekday: 'long', day: 'numeric', month: 'long' })}
              </h4>
              <button onClick={() => setSelectedDay(null)} className="w-7 h-7 rounded-full bg-slate-100 text-slate-400 flex items-center justify-center text-xs hover:bg-slate-200 transition-all">✕</button>
            </div>
            <div className="space-y-2">
              {selectedDayEvents.map(ev => (
                <div key={ev.id} className={`p-3 rounded-2xl border-l-2 ${PRIORITY_STYLES[ev.priority] || PRIORITY_STYLES.Medium}`}>
                  <p className="font-black text-xs uppercase tracking-tight">{ev.title}</p>
                  <p className="text-[10px] font-bold mt-0.5 opacity-70">
                    {new Date(ev.start_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} – {new Date(ev.end_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </p>
                  {ev.location && <p className="text-[10px] opacity-60 mt-0.5">📍 {ev.location}</p>}
                  <div className="flex gap-2 mt-2">
                    {ev.meeting_link && (
                      <button onClick={() => window.open(ev.meeting_link, '_blank')}
                        className="text-[9px] font-black uppercase tracking-widest px-3 py-1.5 bg-white/60 rounded-lg border border-current hover:opacity-80 transition-all">
                        {lang === 'fr' ? 'Rejoindre' : 'Join'}
                      </button>
                    )}
                    <button onClick={() => downloadICS(ev)}
                      className="text-[9px] font-black uppercase tracking-widest px-3 py-1.5 bg-white/60 rounded-lg border border-current hover:opacity-80 transition-all">
                      .ICS
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* ─── Calendar Card ───────────────────────────────────── */}
      <div className="bg-white rounded-[28px] shadow-xl overflow-hidden">

        {/* Header bar */}
        <div className="bg-slate-900 text-white px-4 sm:px-8 py-5 sm:py-8">
          <div className="flex items-center justify-between gap-3 flex-wrap">
            {/* Month/Year */}
            <div>
              <h3 className="text-2xl sm:text-4xl font-black tracking-tighter uppercase leading-none">
                {new Date(currentYear, currentMonth).toLocaleDateString(lang === 'fr' ? 'fr-FR' : 'en-US', { month: 'long' })}
              </h3>
              <p className="text-slate-500 font-black text-[10px] tracking-[0.4em] uppercase mt-0.5">{currentYear}</p>
            </div>

            {/* Controls */}
            <div className="flex items-center gap-2 flex-wrap">
              {/* View toggle */}
              <div className="flex bg-white/10 rounded-xl p-0.5 border border-white/10">
                <button onClick={() => setView('grid')}
                  className={`px-3 py-1.5 rounded-lg text-[10px] font-black uppercase tracking-widest transition-all ${view === 'grid' ? 'bg-white text-slate-900' : 'text-slate-400 hover:text-white'}`}>
                  {lang === 'fr' ? 'Grille' : 'Grid'}
                </button>
                <button onClick={() => setView('list')}
                  className={`px-3 py-1.5 rounded-lg text-[10px] font-black uppercase tracking-widest transition-all ${view === 'list' ? 'bg-white text-slate-900' : 'text-slate-400 hover:text-white'}`}>
                  {lang === 'fr' ? 'Liste' : 'List'}
                </button>
              </div>

              {/* Month nav */}
              <div className="flex items-center gap-1 bg-white/5 p-1 rounded-xl border border-white/10">
                <button onClick={goToPrev} className="w-9 h-9 rounded-lg hover:bg-white/10 flex items-center justify-center transition-all text-lg">←</button>
                <button onClick={goToToday} className="px-3 py-1.5 bg-white text-slate-900 rounded-lg font-black text-[10px] uppercase tracking-widest hover:bg-indigo-50 transition-all">
                  {lang === 'fr' ? "Auj." : "Today"}
                </button>
                <button onClick={goToNext} className="w-9 h-9 rounded-lg hover:bg-white/10 flex items-center justify-center transition-all text-lg">→</button>
              </div>

              {/* Add button */}
              <button onClick={() => setShowAddForm(true)}
                className="flex items-center gap-2 px-4 py-2.5 bg-indigo-600 text-white rounded-xl font-black text-[10px] uppercase tracking-widest hover:bg-indigo-500 transition-all shadow-lg active:scale-95">
                <span>📅</span>
                <span className="hidden sm:inline">{t.establish_btn || 'Schedule'}</span>
                <span className="sm:hidden">+</span>
              </button>
            </div>
          </div>
        </div>

        {loading ? (
          <div className="p-16 flex flex-col items-center justify-center gap-4">
            <div className="w-12 h-12 border-4 border-slate-900 border-t-indigo-600 rounded-full animate-spin" />
            <p className="font-black text-slate-400 uppercase tracking-[0.25em] text-[10px]">Syncing...</p>
          </div>
        ) : view === 'list' ? (
          /* ─── LIST VIEW ─── */
          <div className="divide-y divide-slate-50">
            {monthEvents.length === 0 ? (
              <div className="p-12 text-center">
                <div className="text-4xl mb-3">📅</div>
                <p className="font-black text-slate-400 uppercase tracking-widest text-[11px]">{lang === 'fr' ? 'Aucun événement ce mois-ci' : 'No events this month'}</p>
              </div>
            ) : monthEvents.map(ev => (
              <div key={ev.id} className="px-4 sm:px-6 py-4 hover:bg-slate-50 transition-colors">
                <div className="flex items-start gap-3">
                  <div className="shrink-0 text-center w-10 sm:w-12">
                    <p className="text-xl sm:text-2xl font-black text-slate-800 leading-none">{new Date(ev.start_time).getDate()}</p>
                    <p className="text-[9px] font-black text-slate-400 uppercase tracking-widest">
                      {new Date(ev.start_time).toLocaleDateString(lang === 'fr' ? 'fr-FR' : 'en-US', { weekday: 'short' })}
                    </p>
                  </div>
                  <div className={`w-0.5 self-stretch rounded-full shrink-0 ${ev.priority === 'Critical' ? 'bg-red-400' : ev.priority === 'High' ? 'bg-amber-400' : 'bg-indigo-400'}`} />
                  <div className="flex-1 min-w-0">
                    <p className="font-black text-slate-800 text-sm truncate">{ev.title}</p>
                    <p className="text-[10px] text-slate-500 font-bold mt-0.5">
                      {new Date(ev.start_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} – {new Date(ev.end_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      {ev.location && ` · 📍 ${ev.location}`}
                    </p>
                    {ev.description && <p className="text-[10px] text-slate-400 mt-1 line-clamp-2">{ev.description}</p>}
                  </div>
                  <div className="shrink-0 flex flex-col gap-1">
                    <span className={`text-[9px] font-black uppercase px-2 py-0.5 rounded-full border ${PRIORITY_STYLES[ev.priority] || PRIORITY_STYLES.Medium}`}>{ev.priority}</span>
                    {ev.meeting_link && (
                      <button onClick={() => window.open(ev.meeting_link, '_blank')}
                        className="text-[9px] font-black text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded-full border border-indigo-200 hover:bg-indigo-100 transition-all">
                        {lang === 'fr' ? 'Rejoindre' : 'Join'}
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          /* ─── GRID VIEW ─── */
          <>
            {/* Day headers */}
            <div className="grid grid-cols-7 bg-slate-50 border-b border-slate-100">
              {dayNames.map(d => (
                <div key={d} className="py-2 sm:py-3 text-center text-[8px] sm:text-[10px] font-black text-slate-400 tracking-widest uppercase">{d}</div>
              ))}
            </div>

            {/* Day cells */}
            <div className="grid grid-cols-7 border-l border-t border-slate-100">
              {Array.from({ length: firstDay }).map((_, i) => (
                <div key={`pad-${i}`} className="h-14 sm:h-28 border-r border-b border-slate-100 bg-slate-50/40" />
              ))}

              {Array.from({ length: daysInMonth }, (_, i) => i + 1).map(d => {
                const dateStr = new Date(currentYear, currentMonth, d).toDateString();
                const isToday = new Date().toDateString() === dateStr;
                const dayEvents = events.filter(ev => new Date(ev.start_time).toDateString() === dateStr);
                // Debug: Log events for current day
                if (dayEvents.length > 0) {
                  console.log(`Day ${d} has ${dayEvents.length} events:`, dayEvents.map(ev => ({ title: ev.title, start: ev.start_time, end: ev.end_time })));
                }

                return (
                  <div key={d}
                    onClick={() => { if (dayEvents.length > 0) setSelectedDay(d); }}
                    className={`h-14 sm:h-28 border-r border-b border-slate-100 p-1 sm:p-2 group relative transition-colors cursor-pointer
                      ${isToday ? 'bg-indigo-50/40' : 'bg-white hover:bg-slate-50/60'}
                      ${dayEvents.length > 0 ? 'cursor-pointer' : 'cursor-default'}`}>

                    {/* Date number */}
                    <div className={`w-5 h-5 sm:w-7 sm:h-7 flex items-center justify-center rounded-lg sm:rounded-xl text-[9px] sm:text-[10px] font-black mb-0.5 sm:mb-1.5 transition-all
                      ${isToday ? 'bg-indigo-600 text-white shadow-md' : 'text-slate-400 group-hover:text-slate-800 group-hover:bg-slate-100'}`}>
                      {d}
                    </div>

                    {/* Events – hidden on very small screens, dot indicator instead */}
                    <div className="hidden sm:block space-y-0.5">
                      {dayEvents.slice(0, 2).map(ev => {
                        const startTime = new Date(ev.start_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
                        const endTime = new Date(ev.end_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
                        console.log(`Rendering event: ${ev.title}, start: ${startTime}, end: ${endTime}`);
                        return (
                          <div key={ev.id}
                            onClick={e => { e.stopPropagation(); if (ev.meeting_link) window.open(ev.meeting_link, '_blank'); else downloadICS(ev); }}
                            className={`text-[11px] font-black px-1.5 py-1 rounded-md border-l-2 truncate cursor-pointer hover:shadow-md transition-all
                              ${ev.priority === 'Critical' ? 'bg-red-50 text-red-600 border-red-500' :
                                ev.priority === 'High'     ? 'bg-amber-50 text-amber-600 border-amber-500' :
                                'bg-slate-50 text-slate-600 border-slate-300'}`}>
                            <div className="flex items-center gap-1">
                              <span className="shrink-0 font-mono text-[10px] opacity-80">{startTime}-{endTime}</span>
                              <span className="truncate">{ev.title}</span>
                            </div>
                          </div>
                        );
                      })}
                      {dayEvents.length > 2 && (
                        <div className="text-[10px] font-black text-slate-400 pl-1">+{dayEvents.length - 2}</div>
                      )}
                    </div>

                    {/* Mobile: compact time display */}
                    {dayEvents.length > 0 && (
                      <div className="sm:hidden space-y-0.5 mt-0.5">
                        {dayEvents.slice(0, 2).map(ev => {
                          const startTime = new Date(ev.start_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
                          const endTime = new Date(ev.end_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
                          return (
                            <div key={ev.id} className="flex items-center gap-1">
                              <span className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${ev.priority === 'Critical' ? 'bg-red-500' : ev.priority === 'High' ? 'bg-amber-500' : 'bg-indigo-500'}`} />
                              <span className="text-[10px] font-black text-slate-600 truncate font-mono">{startTime}-{endTime}</span>
                            </div>
                          );
                        })}
                        {dayEvents.length > 2 && (
                          <div className="text-[10px] font-black text-slate-400">+{dayEvents.length - 2}</div>
                        )}
                      </div>
                    )}

                    {/* Desktop add button on hover */}
                    <button
                      onClick={e => {
                        e.stopPropagation();
                        const date = `${currentYear}-${String(currentMonth + 1).padStart(2, '0')}-${String(d).padStart(2, '0')}T09:00`;
                        setFormData({ ...formData, start_time: date, end_time: date });
                        setShowAddForm(true);
                      }}
                      className="hidden sm:flex absolute bottom-2 right-2 w-6 h-6 bg-slate-900 text-white rounded-lg items-center justify-center opacity-0 group-hover:opacity-100 transition-all shadow-xl text-xs">
                      +
                    </button>
                  </div>
                );
              })}
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default Calendar;
