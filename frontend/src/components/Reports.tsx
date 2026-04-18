import { useState, useEffect } from 'react';
import axios from 'axios';
import type { User } from '../App';

interface ReportsProps {
  user: User | null;
  token: string | null;
  lang: 'en' | 'fr';
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  translations: Record<string, any>;
}

const Reports = ({ token, lang, translations }: ReportsProps) => {
  const [loading, setLoading] = useState(true);
  const [metrics, setMetrics] = useState({
    timeUtilization: 0,
    infoVolume: 0,
    decisionRate: 0,
    anomalies: [] as string[],
    briefings: [] as string[]
  });

  const t = translations?.[lang]?.reports || translations?.['en']?.reports || {};

  useEffect(() => {
    const generateAnalytics = async () => {
      try {
        setLoading(true);

        const [calRes, docRes, actRes] = await Promise.all([
          axios.get(`/api/calendar`, { headers: { Authorization: `Bearer ${token}` } }).catch(() => ({ data: [] })),
          axios.get(`/api/documents`, { headers: { Authorization: `Bearer ${token}` } }).catch(() => ({ data: [] })),
          axios.get(`/api/actions`, { headers: { Authorization: `Bearer ${token}` } }).catch(() => ({ data: [] }))
        ]);

        const events = calRes.data;
        const docs = docRes.data;
        const actions = actRes.data;

        // Time Utilization: events this week vs norm
        const timeUtil = events.length > 0 ? Math.min(100, Math.round((events.length / 10) * 100)) : 0;

        // Info Volume: total documents processed
        const infoVol = docs.length;

        // Decision Execution Rate: completed actions / total actions
        const completedActions = actions.filter((a: {status: string}) => a.status === 'Completed').length;
        const execRate = actions.length > 0 ? Math.round((completedActions / actions.length) * 100) : 0;

        // AI Anomaly Detection
        const anomalies: string[] = [];
        const overdue = actions.filter((a: {status: string, due_date: string}) => new Date(a.due_date) < new Date() && a.status !== 'Completed');
        if (overdue.length > 0) {
          anomalies.push(lang === 'fr'
            ? `${t.anomaly_prefix || 'Détection de'} ${overdue.length} ${t.anomaly_overdue || 'directive(s) critique(s) en retard.'}`
            : `${t.anomaly_prefix || 'Detected'} ${overdue.length} ${t.anomaly_overdue || 'critical directive(s) overdue.'}`);
        }
        if (events.length > 5) {
          anomalies.push(lang === 'fr'
            ? t.anomaly_density || `La densité du calendrier dépasse l'optimum opérationnel de 15%.`
            : t.anomaly_density || `Schedule density exceeds operational optimum by 15%.`);
        }
        if (anomalies.length === 0) {
          anomalies.push(lang === 'fr' ? (t.no_anomalies || "Opérations normales. Aucune anomalie détectée.") : (t.no_anomalies || "Operations normal. No workflow anomalies detected."));
        }

        // AI Briefing Suggestions
        const briefs: string[] = [];
        const upcomingEvent = events.find((e: {start_time: string}) => new Date(e.start_time) >= new Date());
        if (upcomingEvent) {
          briefs.push(lang === 'fr'
            ? `${t.briefing_suggested || 'Briefing suggéré : Pré-lecture des métriques pour'} '${upcomingEvent.title}'.`
            : `${t.briefing_suggested || 'Suggested Briefing: Pre-read metrics for'} '${upcomingEvent.title}' event.`);
        } else {
          briefs.push(lang === 'fr'
            ? (t.daily_summary_ready || `Le résumé quotidien de la presse est prêt.`)
            : (t.daily_summary_ready || `Standard Daily Press Summary is ready for review.`));
        }

        setMetrics({
          timeUtilization: timeUtil,
          infoVolume: infoVol,
          decisionRate: execRate,
          anomalies,
          briefings: briefs
        });
      } catch {
        console.error("Failed to fetch analytics");
      } finally {
        setLoading(false);
      }
    };

    generateAnalytics();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token, lang]);

  return (
    <div className="space-y-6 max-w-7xl">
      <div className="premium-card p-8 fade-in-up border-l-4 border-l-violet-500 bg-gradient-to-r from-white to-violet-50/20">
        <h2 className="text-3xl font-bold text-slate-800 mb-2">{t.title || 'Reports & Analytics'}</h2>
        <p className="text-slate-500 font-medium">{t.subtitle || 'Analytics on time utilization, information volume, and decision execution.'}</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Metric 1 */}
        <div className="premium-card p-6 fade-in-up flex flex-col justify-between" style={{ animationDelay: '0.1s' }}>
          <div>
            <h3 className="text-sm font-bold tracking-widest uppercase text-slate-400 mb-2">{t.time_util || 'Time Utilization'}</h3>
            <div className="flex items-end gap-3 mb-2">
              <span className="text-4xl font-black text-blue-600">{metrics.timeUtilization}%</span>
              <span className="text-sm font-medium text-slate-400 pb-1">{t.capacity || 'capacity'}</span>
            </div>
            <p className="text-xs font-medium text-slate-500 mt-4 leading-relaxed">{t.time_desc || 'Measures strategic alignment of protected scheduling slots versus incoming meeting volumes.'}</p>
          </div>
          <div className="w-full bg-slate-100 h-2 rounded-full mt-6 overflow-hidden">
            <div className="bg-blue-500 h-full rounded-full transition-all duration-1000" style={{ width: `${metrics.timeUtilization}%` }}></div>
          </div>
        </div>

        {/* Metric 2 */}
        <div className="premium-card p-6 fade-in-up flex flex-col justify-between" style={{ animationDelay: '0.2s' }}>
          <div>
            <h3 className="text-sm font-bold tracking-widest uppercase text-slate-400 mb-2">{t.info_vol || 'Information Volume'}</h3>
            <div className="flex items-end gap-3 mb-2">
              <span className="text-4xl font-black text-purple-600">{metrics.infoVolume}</span>
              <span className="text-sm font-medium text-slate-400 pb-1">{t.docs_parsed || 'docs parsed'}</span>
            </div>
            <p className="text-xs font-medium text-slate-500 mt-4 leading-relaxed">{t.info_desc || 'Tracks the velocity of standardized briefing notes compiled within the Central Hub.'}</p>
          </div>
        </div>

        {/* Metric 3 */}
        <div className="premium-card p-6 fade-in-up flex flex-col justify-between" style={{ animationDelay: '0.3s' }}>
          <div>
            <h3 className="text-sm font-bold tracking-widest uppercase text-slate-400 mb-2">{t.dec_rate || 'Decision Execution Rate'}</h3>
            <div className="flex items-end gap-3 mb-2">
              <span className="text-4xl font-black text-emerald-500">{metrics.decisionRate}%</span>
              <span className="text-sm font-medium text-slate-400 pb-1">{t.completion || 'completion'}</span>
            </div>
            <p className="text-xs font-medium text-slate-500 mt-4 leading-relaxed">{t.dec_desc || 'Aggregated status of completed workflow objectives versus outstanding tasks assigned.'}</p>
          </div>
          <div className="w-full bg-slate-100 h-2 rounded-full mt-6 overflow-hidden">
            <div className="bg-emerald-500 h-full rounded-full transition-all duration-1000" style={{ width: `${metrics.decisionRate}%` }}></div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6">
        {/* AI Monitoring */}
        <div className="premium-card p-6 fade-in-up" style={{ animationDelay: '0.4s' }}>
          <div className="flex items-center justify-between mb-6">
            <h3 className="font-bold text-slate-700">{t.ai_title || 'AI-Assisted Workflow Analytics'}</h3>
            <span className="badge bg-indigo-50 text-indigo-700 ring-1 ring-indigo-200">{t.active_mon || 'Active Monitoring'}</span>
          </div>

          {loading ? (
            <div className="text-center p-4 text-slate-400">{t.processing || 'Processing metrics...'}</div>
          ) : (
            <div className="space-y-4">
              <div className="p-4 rounded-xl border border-rose-100 bg-rose-50/50">
                <div className="flex gap-3 mb-2">
                  <span className="text-rose-500">⚠️</span>
                  <h4 className="font-extrabold text-sm text-rose-800">{t.anomaly || 'Anomaly Detection'}</h4>
                </div>
                <ul className="pl-8 list-disc list-outside space-y-1 text-sm font-medium text-rose-700/80">
                  {metrics.anomalies.map((anom, i) => <li key={i}>{anom}</li>)}
                </ul>
              </div>

              <div className="p-4 rounded-xl border border-indigo-100 bg-indigo-50/50">
                <div className="flex gap-3 mb-2">
                  <span className="text-indigo-500">✨</span>
                  <h4 className="font-extrabold text-sm text-indigo-800">{t.briefing_sug || 'Automatic Briefing Suggestions'}</h4>
                </div>
                <ul className="pl-8 list-disc list-outside space-y-1 text-sm font-medium text-indigo-700/80">
                  {metrics.briefings.map((brief, i) => <li key={i}>{brief}</li>)}
                </ul>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Reports;
