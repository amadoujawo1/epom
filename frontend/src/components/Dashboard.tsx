import { useState, useEffect } from 'react';
import axios from 'axios';
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts';
import type { User } from '../App';

interface DashboardProps {
  user: User | null;
  lang: 'en' | 'fr';
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  translations: Record<string, any>;
  token: string | null;
}

const COLORS = ['#8b5cf6', '#10b981', '#f59e0b', '#ef4444']; // Indigo, Emerald, Amber, Red

const Dashboard = ({ token, lang, translations }: DashboardProps) => {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const t = translations?.[lang]?.dashboard || translations?.['en']?.dashboard || {} as any;
  const [stats, setStats] = useState({ events: 0, pending: 0, completed: 0, in_progress: 0, docs: 0, employees: 0, attendance: 0, projects: 0 });
  const [insight, setInsight] = useState('');
  const [conflicts, setConflicts] = useState<{e1: string, e2: string}[]>([]);
  const [loading, setLoading] = useState(true);
  const [taskData, setTaskData] = useState<{name: string, value: number}[]>([]);
  const [eventData, setEventData] = useState<{name: string, count: number}[]>([]);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true);
        const [calRes, docRes, actRes, userRes, projRes] = await Promise.all([
          axios.get('/api/calendar', { headers: { Authorization: `Bearer ${token}` } }),
          axios.get('/api/documents', { headers: { Authorization: `Bearer ${token}` } }),
          axios.get('/api/actions', { headers: { Authorization: `Bearer ${token}` } }),
          axios.get('/api/users', { headers: { Authorization: `Bearer ${token}` } }),
          axios.get('/api/projects', { headers: { Authorization: `Bearer ${token}` } })
        ]);

        const events = calRes.data;
        const actions = actRes.data;
        const users = userRes.data;

        // Detect Conflicts
        const detectedConflicts: {e1: string, e2: string}[] = [];
        for (let i = 0; i < events.length; i++) {
          for (let j = i + 1; j < events.length; j++) {
            const e1 = events[i];
            const e2 = events[j];
            const start1 = new Date(e1.start_time);
            const end1 = new Date(e1.end_time);
            const start2 = new Date(e2.start_time);
            const end2 = new Date(e2.end_time);

            if (start1 < end2 && start2 < end1) {
              detectedConflicts.push({ e1: e1.title, e2: e2.title });
            }
          }
        }
        setConflicts(detectedConflicts);

        // Calculate Insight: Today's load
        const now = new Date();
        const startOfToday = new Date(now.setHours(0, 0, 0, 0));
        const endOfToday = new Date(now.setHours(23, 59, 59, 999));

        const todayEvents = events.filter((e: {start_time: string}) => {
          const start = new Date(e.start_time);
          return start >= startOfToday && start <= endOfToday;
        });

        let totalMinutes = 0;
        todayEvents.forEach((e: {priority: string, start_time: string, end_time: string}) => {
          const start = new Date(e.start_time);
          const end = new Date(e.end_time);
          totalMinutes += (end.getTime() - start.getTime()) / (1000 * 60);
        });

        const loadPercentage = Math.min(100, Math.round((totalMinutes / 480) * 100)); // 100% = 8 hours

        let insightMsg = '';
        if (lang === 'fr') {
          if (loadPercentage === 0) insightMsg = "Votre calendrier pour aujourd'hui est vide. Optimisez ce temps pour la réflexion stratégique.";
          else if (loadPercentage < 50) insightMsg = `Votre calendrier pour aujourd'hui est rempli à ${loadPercentage}%. Vous avez une marge de manœuvre opérationnelle.`;
          else if (loadPercentage < 80) insightMsg = `Votre calendrier pour aujourd'hui est rempli à ${loadPercentage}%. Maintenez la priorité sur les directives critiques.`;
          else insightMsg = `Votre calendrier pour aujourd'hui est rempli à ${loadPercentage}%. Programmer plus de réunions pourrait affecter la productivité.`;
        } else {
          if (loadPercentage === 0) insightMsg = "Your calendar for today is empty. Optimize this time for deep strategic reflection.";
          else if (loadPercentage < 50) insightMsg = `Your calendar for today is ${loadPercentage}% full. You have healthy operational headroom.`;
          else if (loadPercentage < 80) insightMsg = `Your calendar for today is ${loadPercentage}% full. Maintain focus on top-tier directives.`;
          else insightMsg = `Your calendar for today is ${loadPercentage}% full. Scheduling more meetings may impact productivity.`;
        }
        setInsight(insightMsg);

        // Calculate stats
        const pending = actions.filter((a: {status: string}) => a.status === 'Pending').length;
        const inProgress = actions.filter((a: {status: string}) => a.status === 'In Progress').length;
        const completed = actions.filter((a: {status: string}) => a.status === 'Completed').length;
        const activeUsersCount = users.filter((u: {is_active: boolean}) => u.is_active).length;

        setStats({
          events: events.length,
          pending: pending,
          in_progress: inProgress,
          completed: completed,
          docs: docRes.data.length,
          employees: users.length,
          attendance: Math.round((activeUsersCount / (users.length || 1)) * 100),
          projects: projRes.data.length
        });

        // Setup chart data
        setTaskData([
          { name: lang === 'fr' ? 'À faire' : 'Pending', value: pending },
          { name: lang === 'fr' ? 'En Cours' : 'In Progress', value: inProgress },
          { name: lang === 'fr' ? 'Terminé' : 'Completed', value: completed }
        ]);

        const eventCounts: Record<string, number> = { Low: 0, Medium: 0, High: 0, Critical: 0 };
        events.forEach((e: {priority: string}) => {
          if (eventCounts[e.priority] !== undefined) {
             eventCounts[e.priority]++;
          }
        });
        setEventData([
          { name: lang === 'fr' ? 'Faible' : 'Low', count: eventCounts.Low },
          { name: lang === 'fr' ? 'Moyenne' : 'Medium', count: eventCounts.Medium },
          { name: 'High', count: eventCounts.High },
          { name: 'Critical', count: eventCounts.Critical },
        ]);

      } catch (err) {
        console.error("Failed to fetch dashboard stats", err);
      } finally {
        setLoading(false);
      }
    };
    if (token) fetchStats();
  }, [token, lang]);

  return (
    <div className="w-full max-w-7xl space-y-6">
      {/* Stats Row */}
      <div className="bg-white rounded-[24px] shadow-sm grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-6 divide-y sm:divide-y-0 lg:divide-x divide-slate-100 py-3 overflow-hidden">

        {/* Projects */}
        <div className="px-6 py-4 flex items-center justify-start gap-4">
          <div className="text-2xl flex items-center justify-center w-10 h-10 bg-indigo-50 text-indigo-600 rounded-xl shadow-sm border border-indigo-100/50">📁</div>
          <div className="flex flex-col">
            <span className="text-[10px] font-bold text-slate-400 tracking-widest uppercase mb-1">{lang === 'fr' ? 'Projets' : 'Projects'}</span>
            <span className="text-xl font-black text-indigo-700 leading-none">{loading ? '...' : stats.projects}</span>
          </div>
        </div>

        {/* Personnel */}
        <div className="px-6 py-4 flex items-center justify-start gap-4">
          <div className="text-2xl flex items-center justify-center w-10 h-10 bg-slate-50 rounded-xl shadow-sm border border-slate-100">👥</div>
          <div className="flex flex-col">
            <span className="text-[10px] font-bold text-slate-400 tracking-widest uppercase mb-1">{lang === 'fr' ? 'Personnel' : 'Personnel'}</span>
            <span className="text-xl font-black text-slate-700 leading-none">{loading ? '...' : stats.employees}</span>
          </div>
        </div>

        {/* Pending */}
        <div className="px-6 py-4 flex items-center justify-start gap-4">
          <div className="text-2xl flex items-center justify-center w-10 h-10 bg-indigo-50 rounded-xl shadow-sm border border-indigo-100/50">⚡</div>
          <div className="flex flex-col">
            <span className="text-[10px] font-bold text-slate-400 tracking-widest uppercase mb-1">{t.pending || 'Pending'}</span>
            <span className="text-xl font-black text-indigo-600 leading-none">{loading ? '...' : stats.pending}</span>
          </div>
        </div>

        {/* Completed */}
        <div className="px-6 py-4 flex items-center justify-start gap-4">
          <div className="text-2xl flex items-center justify-center w-10 h-10 bg-slate-50 rounded-xl shadow-sm border border-slate-100">🏆</div>
          <div className="flex flex-col">
            <span className="text-[10px] font-bold text-slate-400 tracking-widest uppercase mb-1">{t.completed || 'Completed'}</span>
            <span className="text-xl font-black text-emerald-500 leading-none">{loading ? '...' : stats.completed}</span>
          </div>
        </div>

        {/* Events */}
        <div className="px-6 py-4 flex items-center justify-start gap-4">
          <div className="text-2xl flex items-center justify-center w-10 h-10 bg-slate-50 rounded-xl shadow-sm border border-slate-100">📅</div>
          <div className="flex flex-col">
            <span className="text-[10px] font-bold text-slate-400 tracking-widest uppercase mb-1">{t.events || 'Events'}</span>
            <span className="text-xl font-black text-blue-600 leading-none">{loading ? '...' : stats.events}</span>
          </div>
        </div>

        {/* Docs */}
        <div className="px-6 py-4 flex items-center justify-start gap-4">
          <div className="text-2xl flex items-center justify-center w-10 h-10 bg-slate-50 rounded-xl shadow-sm border border-slate-100">📄</div>
          <div className="flex flex-col">
            <span className="text-[10px] font-bold text-slate-400 tracking-widest uppercase mb-1">{t.docs || 'Docs'}</span>
            <span className="text-xl font-black text-purple-600 leading-none">{loading ? '...' : stats.docs}</span>
          </div>
        </div>

      </div>

      {/* Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

        {/* Intelligence Hub */}
        <div className="bg-[#111424] rounded-[24px] shadow-sm p-8 text-white relative h-full">
          <div className="absolute top-8 right-8 w-1.5 h-1.5 rounded-full bg-emerald-400"></div>

          <div className="flex items-center gap-3 mb-10">
            <span className="text-xl">✨</span>
            <h3 className="text-xl font-bold tracking-tight">{t.intelligence_hub || 'Intelligence Hub'}</h3>
          </div>

          <div className="space-y-6">
            <div>
              <h4 className="text-[11px] font-black text-slate-400 tracking-[0.2em] mb-4">{t.strategic_insights || 'STRATEGIC INSIGHTS'}</h4>
              <div className="bg-[#1e233b] rounded-2xl p-5 border border-white/5">
                <p className="text-sm font-medium text-slate-300 leading-relaxed min-h-[40px]">
                  {loading ? (t.processing || '...') : (insight || t.insight_text || '...')}
                </p>
              </div>
            </div>

            {conflicts.length > 0 && (
              <div className="bg-red-500/10 border border-red-500/20 rounded-2xl p-5 animate-pulse">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-red-400">⚠️</span>
                  <h4 className="text-[11px] font-black text-red-400 tracking-[0.2em] uppercase">{t.conflicts || 'Conflicts Detected'}</h4>
                </div>
                <div className="space-y-2">
                  {conflicts.slice(0, 2).map((c, i) => (
                    <p key={i} className="text-xs font-bold text-slate-300">
                      Overlap: <span className="text-white">{c.e1}</span> / <span className="text-white">{c.e2}</span>
                    </p>
                  ))}
                  <p className="text-[10px] italic text-slate-400 mt-2">{t.self_correct || 'Smart self-correction in Progress...'}</p>
                </div>
              </div>
            )}

            <div className="bg-emerald-500/10 border border-emerald-500/20 rounded-2xl p-5">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-emerald-400">🛡️</span>
                <h4 className="text-[11px] font-black text-emerald-400 tracking-[0.2em] uppercase">{t.ai_filtering || 'AI-Filtering Active'}</h4>
              </div>
              <p className="text-xs font-medium text-slate-300">{t.ai_desc || 'Proactively filtering schedules based on Presidential Priorities.'}</p>
            </div>
          </div>
        </div>

        {/* Charts and Operational Flow */}
        <div className="space-y-6">
          {/* Charts Row */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
            <div className="bg-white rounded-[24px] shadow-sm p-6 flex flex-col">
              <h4 className="text-[11px] font-black text-slate-400 tracking-[0.2em] uppercase mb-4">{lang === 'fr' ? 'Avancement des Tâches' : 'Task Progress'}</h4>
              <div className="flex-1 min-h-[160px] flex items-center justify-center">
                {loading ? <p className="text-slate-300 text-sm">...</p> : (
                  <ResponsiveContainer width="100%" height={160}>
                    <PieChart>
                      <Pie
                        data={taskData}
                        cx="50%"
                        cy="50%"
                        innerRadius={45}
                        outerRadius={70}
                        paddingAngle={5}
                        dataKey="value"
                      >
                        {taskData.map((_entry, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip 
                        contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                        itemStyle={{ fontSize: '13px', fontWeight: 'bold' }}
                      />
                    </PieChart>
                  </ResponsiveContainer>
                )}
              </div>
            </div>

            <div className="bg-white rounded-[24px] shadow-sm p-6 flex flex-col">
              <h4 className="text-[11px] font-black text-slate-400 tracking-[0.2em] uppercase mb-4">{lang === 'fr' ? 'Événements par Priorité' : 'Events By Priority'}</h4>
              <div className="flex-1 min-h-[160px] flex flex-col justify-end gap-2 pb-2">
                {loading ? <p className="text-slate-300 text-sm">...</p> : (
                  <>
                    {eventData.map((item, idx) => {
                      const barColors = ['#94a3b8', '#8b5cf6', '#f59e0b', '#ef4444'];
                      const maxVal = Math.max(...eventData.map(d => d.count), 1);
                      const pct = Math.max(8, Math.round((item.count / maxVal) * 100));
                      return (
                        <div key={idx} className="flex items-center gap-2 group">
                          <span className="text-[9px] font-black text-slate-400 uppercase tracking-wide w-14 text-right shrink-0">{item.name}</span>
                          <div className="flex-1 bg-slate-100 rounded-full h-5 overflow-hidden">
                            <div
                              className="h-full rounded-full flex items-center justify-end pr-2 transition-all duration-700"
                              style={{ width: `${pct}%`, backgroundColor: barColors[idx] }}
                            >
                              {item.count > 0 && <span className="text-[9px] font-black text-white">{item.count}</span>}
                            </div>
                          </div>
                          {item.count === 0 && <span className="text-[9px] font-black text-slate-300">0</span>}
                        </div>
                      );
                    })}
                  </>
                )}
              </div>
            </div>
          </div>

          <div className="bg-white rounded-[24px] shadow-sm p-8">
            <div className="flex justify-between items-start mb-10">
              <div>
                <h3 className="text-xl font-bold tracking-tight text-slate-900 mb-1">{t.op_flow || 'Operational Flow'}</h3>
                <h4 className="text-[11px] font-black text-slate-400 tracking-[0.2em]">{t.real_time || 'REAL-TIME DIRECTIVES'}</h4>
              </div>
              <div className="bg-indigo-50 text-indigo-600 text-[10px] font-black px-3 py-1.5 rounded-full tracking-wider border border-indigo-100">
                {stats.pending} {t.total || 'TOTAL'}
              </div>
            </div>

            {stats.pending === 0 ? (
              <div className="border border-dashed border-slate-200 rounded-2xl p-8 text-center bg-slate-50/50">
                <span className="text-2xl mb-2 block">✅</span>
                <p className="text-sm font-bold text-slate-500 uppercase tracking-widest">{t.all_clear || 'All Systems Clear'}</p>
                <p className="text-xs text-slate-400 mt-1">{t.no_pending || 'No critical directives pending at this time.'}</p>
              </div>
            ) : (
              <div className="border border-slate-100 rounded-2xl p-6 shadow-sm bg-indigo-50/30">
                <h4 className="font-extrabold text-slate-800 text-base mb-1">{t.active_directives || 'Active Directives'}</h4>
                <p className="text-xs text-slate-500 mb-4">{t.review_msg || 'Please review the e-Action register for details.'}</p>
                <div className="flex items-center gap-2">
                  <span className="px-3 py-1 rounded border border-indigo-200 bg-indigo-50 text-[10px] font-extrabold text-indigo-500 tracking-wide uppercase">
                    {stats.pending} {t.pending_badge || 'PENDING'}
                  </span>
                </div>
              </div>
            )}
          </div>
        </div>

      </div>

    </div>
  );
};

export default Dashboard;
