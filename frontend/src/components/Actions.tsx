import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import type { User } from '../App';

interface Project {
  id: number;
  name: string;
  description?: string;
  status: string;
}

interface Action {
  id: number;
  title: string;
  description?: string;
  status: string;
  priority: string;
  due_date: string;
  assigned_to: number;
  assigned_username: string;
  assigned_first_name?: string;
  assigned_last_name?: string;
  project_id?: number | null;
  project_name?: string | null;
}

interface ActionsProps {
  lang: 'en' | 'fr';
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  translations: Record<string, any>;
  token: string | null;
  user: User | null;
}

const Actions = ({ lang, translations, token, user }: ActionsProps) => {
  const t = translations?.[lang]?.actions || translations?.['en']?.actions || {};
  const [actions, setActions] = useState<Action[]>([]);
  const [personnel, setPersonnel] = useState<{id: number, username: string, role: string}[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);
  const [showProjectForm, setShowProjectForm] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  
  const [formData, setFormData] = useState({
    title: '',
    assigned_to: '',
    due_date: '',
    priority: 'Medium',
    status: 'Pending',
    project_id: ''
  });

  const [projectFormData, setProjectFormData] = useState({
    name: '',
    description: ''
  });

  const fetchData = useCallback(async () => {
    if (!token) return;
    try {
      setLoading(true);

      const [actionsRes, usersRes, projectsRes] = await Promise.all([
        axios.get(`/api/actions`, { headers: { Authorization: `Bearer ${token}` } }),
        axios.get(`/api/personnel`, { headers: { Authorization: `Bearer ${token}` } }),
        axios.get(`/api/projects`, { headers: { Authorization: `Bearer ${token}` } })
      ]);

      setActions(actionsRes.data);
      setPersonnel(usersRes.data);
      setProjects(projectsRes.data);
      
      // Debug: Log personnel data
      console.log('Personnel data loaded:', usersRes.data);
      console.log('Number of personnel:', usersRes.data?.length || 0);
    } catch (err: unknown) {
      console.error("Failed to fetch action data", err);
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleAddAction = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token) return;
    setIsSubmitting(true);
    try {
      const payload = {
        ...formData,
        due_date: formData.due_date ? new Date(formData.due_date).toISOString() : null,
        project_id: formData.project_id || null
      };

      await axios.post(`/api/actions`, payload, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setFormData({ title: '', assigned_to: '', due_date: '', priority: 'Medium', status: 'Pending', project_id: '' });
      setShowAddForm(false);
      fetchData();
    } catch (err) {
      console.error("Failed to create action", err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCreateProject = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token) return;
    setIsSubmitting(true);
    try {
      await axios.post(`/api/projects`, projectFormData, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setProjectFormData({ name: '', description: '' });
      setShowProjectForm(false);
      fetchData();
    } catch (err) {
      console.error("Failed to create project", err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDeleteAction = async (actionId: number) => {
    if (!window.confirm(lang === 'fr' ? 'Supprimer définitivement cette directive ?' : 'Permanently delete this directive?')) return;
    try {
      await axios.delete(`/api/actions/${actionId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      fetchData();
    } catch (err: unknown) {
      const axiosError = err as { response?: { data?: { error?: string } } };
      alert(axiosError.response?.data?.error || 'Delete failed');
    }
  };

  const handleUpdateStatus = async (actionId: number, newStatus: string) => {
    try {
      await axios.put(`/api/actions/${actionId}`, { status: newStatus }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      fetchData();
    } catch (err: unknown) {
      const axiosError = err as { response?: { data?: { error?: string } } };
      alert(axiosError.response?.data?.error || "Update failed");
    }
  };

  const handleGenerateReport = async () => {
    try {
      const res = await axios.post(`/api/reports/weekly`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      alert(res.data.message);
    } catch (err: unknown) {
      const axiosError = err as { response?: { data?: { error?: string } } };
      console.error("Report generation failed", err);
      alert(axiosError.response?.data?.error || (lang === 'fr' ? "Échec de la génération du rapport." : "Report generation failed. Only Administrators can trigger strategic reports."));
    }
  };

  // Metrics
  const now = new Date();
  const overdueCount = actions.filter(a => new Date(a.due_date) < now && a.status !== 'Completed').length;
  const completedCount = actions.filter(a => a.status === 'Completed').length;
  const inProgressCount = actions.filter(a => a.status === 'In Progress').length;

  const inNext7Days = new Date();
  inNext7Days.setDate(inNext7Days.getDate() + 7);
  const dueThisWeekCount = actions.filter(a => {
    const d = new Date(a.due_date);
    return d >= now && d <= inNext7Days && a.status !== 'Completed';
  }).length;

  const filteredActions = actions.filter(a =>
    (a.title || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
    (a.assigned_username || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
    (a.project_name || '').toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* Add Project Modal */}
      {showProjectForm && (
        <div className="fixed inset-0 z-[110] flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-slate-900/60 backdrop-blur-sm" onClick={() => setShowProjectForm(false)}></div>
          <div className="relative w-full max-w-md bg-white rounded-3xl shadow-2xl p-8 scale-in-center">
            <h3 className="text-xl font-black text-slate-800 mb-6 uppercase tracking-tight">New Strategic Project</h3>
            <form onSubmit={handleCreateProject} className="space-y-4">
              <div>
                <label className="block text-[10px] font-black text-slate-400 uppercase mb-2 tracking-widest">Project Name</label>
                <input 
                  required type="text" 
                  value={projectFormData.name}
                  onChange={e => setProjectFormData({...projectFormData, name: e.target.value})}
                  className="w-full px-5 py-3 bg-slate-50 border-0 rounded-xl focus:ring-2 focus:ring-indigo-500 outline-none font-bold"
                  placeholder="e.g. Health Sector Reform"
                />
              </div>
              <div>
                <label className="block text-[10px] font-black text-slate-400 uppercase mb-2 tracking-widest">Brief Description</label>
                <textarea 
                  value={projectFormData.description}
                  onChange={e => setProjectFormData({...projectFormData, description: e.target.value})}
                  className="w-full px-5 py-3 bg-slate-50 border-0 rounded-xl focus:ring-2 focus:ring-indigo-500 outline-none min-h-[100px]"
                />
              </div>
              <div className="pt-4 flex gap-3">
                <button type="button" onClick={() => setShowProjectForm(false)} className="flex-1 py-3 text-slate-400 font-bold uppercase tracking-widest text-xs">Cancel</button>
                <button type="submit" disabled={isSubmitting} className="flex-1 py-3 bg-indigo-600 text-white rounded-xl font-black uppercase tracking-widest text-xs shadow-lg shadow-indigo-200">Create</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Add Action Modal */}
      {showAddForm && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 sm:p-6 lg:p-10">
          <div
            className="absolute inset-0 bg-slate-900/70 backdrop-blur-md transition-opacity"
            onClick={() => !isSubmitting && setShowAddForm(false)}
          ></div>

          <div className="relative w-full max-w-5xl bg-white rounded-[40px] shadow-2xl overflow-hidden scale-in-center max-h-[90vh] flex flex-col">
            <div className="bg-slate-800 p-8 text-white flex justify-between items-center border-b border-white/5">
              <div className="flex items-center gap-5">
                <div className="w-14 h-14 bg-slate-700 rounded-[22px] flex items-center justify-center text-3xl shadow-xl shadow-black/20">⚖️</div>
                <div>
                  <h3 className="font-black text-2xl tracking-tight">{t.form_title || 'Register New Directive / Decision'}</h3>
                  <div className="flex items-center gap-3 mt-1.5 text-xs font-bold text-slate-400">
                    <span className="flex items-center gap-1.5 text-blue-400">
                      <span className="w-1.5 h-1.5 rounded-full bg-blue-400 animate-pulse"></span>
                      OFFICIAL COMMITMENT ACTIVE
                    </span>
                    <span className="opacity-40">•</span>
                    <span className="uppercase tracking-widest">{lang === 'fr' ? 'Suivi stratégique' : 'Strategic Monitoring'}</span>
                  </div>
                </div>
              </div>
              <button
                onClick={() => !isSubmitting && setShowAddForm(false)}
                className="w-10 h-10 flex items-center justify-center rounded-full hover:bg-white/10 transition-colors"
                title="ESC"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path></svg>
              </button>
            </div>

            <div className="p-6 sm:p-10 bg-white overflow-y-auto custom-scrollbar flex-1">
              <form onSubmit={handleAddAction} className="space-y-8">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                  <div className="md:col-span-2 space-y-3">
                    <label className="block text-[11px] font-black text-slate-400 uppercase tracking-[0.2em]">{t.act_title || 'Action Title'}</label>
                    <input
                      required type="text"
                      value={formData.title}
                      onChange={e => setFormData({ ...formData, title: e.target.value })}
                      className="w-full px-6 py-4.5 bg-slate-50 border-0 rounded-2xl focus:ring-2 focus:ring-indigo-500 outline-none text-slate-800 font-bold placeholder:font-normal placeholder:text-slate-400 transition-all focus:bg-white"
                      placeholder={lang === 'fr' ? 'Décrivez la directive...' : 'Describe the directive instance...'}
                    />
                  </div>

                  <div className="space-y-3">
                    <label className="block text-[11px] font-black text-slate-400 uppercase tracking-[0.2em]">{t.assign || 'Assign To Owner'}</label>
                    <div className="relative">
                      <select
                        required
                        value={formData.assigned_to}
                        onChange={e => setFormData({ ...formData, assigned_to: e.target.value })}
                        className="w-full px-6 py-4.5 bg-slate-50 border-0 rounded-2xl focus:ring-2 focus:ring-indigo-500 outline-none text-slate-800 font-bold appearance-none cursor-pointer transition-all focus:bg-white pr-10"
                      >
                        <option value="" disabled>{lang === 'fr' ? 'Sélectionner le personnel...' : 'Select personnel...'}</option>
                        {personnel.length === 0 ? (
                          <option value="" disabled>No personnel available - Check console for debug info</option>
                        ) : (
                          personnel.map(p => (
                            <option key={p.id} value={p.id}>{p.username} ({p.role})</option>
                          ))
                        )}
                      </select>
                    </div>
                  </div>

                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                        <label className="block text-[11px] font-black text-slate-400 uppercase tracking-[0.2em]">Strategic Project Grouping</label>
                        <button type="button" onClick={() => setShowProjectForm(true)} className="text-[10px] font-black text-indigo-600 uppercase tracking-widest hover:underline">+ New Project</button>
                    </div>
                    <select
                      value={formData.project_id}
                      onChange={e => setFormData({ ...formData, project_id: e.target.value })}
                      className="w-full px-6 py-4.5 bg-slate-50 border-0 rounded-2xl focus:ring-2 focus:ring-indigo-500 outline-none text-slate-800 font-bold appearance-none cursor-pointer transition-all focus:bg-white"
                    >
                      <option value="">{lang === 'fr' ? 'Aucun projet (Tâche isolée)' : 'No Project (Isolated Task)'}</option>
                      {projects.map(p => (
                        <option key={p.id} value={p.id}>{p.name}</option>
                      ))}
                    </select>
                  </div>

                  <div className="space-y-3">
                    <label className="block text-[11px] font-black text-slate-400 uppercase tracking-[0.2em]">{t.due || 'Due Date'}</label>
                    <input
                      required type="datetime-local"
                      value={formData.due_date}
                      onChange={e => setFormData({ ...formData, due_date: e.target.value })}
                      className="w-full px-6 py-4.5 bg-slate-50 border-0 rounded-2xl focus:ring-2 focus:ring-indigo-500 outline-none text-slate-800 font-bold transition-all focus:bg-white"
                    />
                  </div>

                  <div className="space-y-3">
                    <label className="block text-[11px] font-black text-slate-400 uppercase tracking-[0.2em]">Initial Status</label>
                    <select
                      value={formData.status}
                      onChange={e => setFormData({ ...formData, status: e.target.value })}
                      className="w-full px-6 py-4.5 bg-slate-50 border-0 rounded-2xl focus:ring-2 focus:ring-indigo-500 outline-none text-slate-800 font-bold transition-all focus:bg-white"
                    >
                      <option value="Pending">Pending</option>
                      <option value="In Progress">In Progress</option>
                      <option value="Completed">Completed</option>
                    </select>
                  </div>
                </div>

                <div className="space-y-4">
                  <label className="block text-[11px] font-black text-slate-400 uppercase tracking-[0.2em]">{t.priority || 'Strategic Priority'}</label>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    {[
                      { val: 'Low', label: t.priorities?.low || 'Low', color: 'bg-slate-100 text-slate-600', active: 'ring-slate-500 bg-slate-900 text-white' },
                      { val: 'Medium', label: t.priorities?.medium || 'Medium', color: 'bg-blue-100 text-blue-600', active: 'ring-blue-500 bg-blue-600 text-white' },
                      { val: 'High', label: t.priorities?.high || 'High', color: 'bg-amber-100 text-amber-600', active: 'ring-amber-500 bg-amber-500 text-white' },
                      { val: 'Critical', label: t.priorities?.critical || 'Critical', color: 'bg-red-100 text-red-600', active: 'ring-red-500 bg-red-600 text-white' }
                    ].map((p) => (
                      <button
                        key={p.val}
                        type="button"
                        onClick={() => setFormData({ ...formData, priority: p.val })}
                        className={`p-5 rounded-[24px] text-center transition-all duration-300 border ${formData.priority === p.val
                            ? p.active + ' shadow-xl scale-[1.02] border-transparent'
                            : 'bg-slate-50 text-slate-400 border-slate-100 hover:bg-white hover:shadow-md'
                          }`}
                      >
                        <div className="text-[10px] font-black uppercase tracking-[0.2em] opacity-80 mb-1">{p.val}</div>
                        <div className="text-xs font-bold leading-tight">{p.label}</div>
                      </button>
                    ))}
                  </div>
                </div>

                <div className="pt-8 flex flex-col sm:flex-row justify-between items-center bg-slate-900 -mx-10 -mb-10 p-10 gap-6">
                  <div className="flex items-center gap-4 text-slate-400">
                    <div className="w-12 h-12 rounded-[18px] bg-white/5 text-white flex items-center justify-center text-xl border border-white/5 font-black italic">!</div>
                    <div>
                      <p className="text-[11px] font-black tracking-widest text-white uppercase">Binding Decision</p>
                      <p className="text-[11px] font-medium leading-tight text-slate-500 mt-0.5 max-w-[280px]">
                        {t.binding_desc || (lang === 'fr' ? 'La directive sera inscrite au registre officiel de la présidence.' : 'Directive will be inscribed in the Official Presidency Register.')}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-4 w-full sm:w-auto">
                    <button type="button" onClick={() => !isSubmitting && setShowAddForm(false)} className="flex-1 sm:flex-none px-12 py-4.5 text-slate-400 font-extrabold text-sm uppercase tracking-widest rounded-2xl hover:bg-white/5">Cancel</button>
                    <button type="submit" disabled={isSubmitting} className="flex-1 sm:flex-none bg-white text-slate-900 font-black text-sm uppercase tracking-widest py-4.5 px-14 rounded-2xl shadow-2xl hover:bg-indigo-50">Commit</button>
                  </div>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <div className="lg:col-span-4 grid grid-cols-1 sm:grid-cols-4 gap-6 fade-in-up">
          <div className="premium-card p-5 bg-white border-l-4 border-l-slate-400 flex items-center gap-4">
            <div className="text-2xl">⏳</div>
            <div>
              <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest">In Progress</p>
              <h3 className="text-2xl font-black text-slate-800">{inProgressCount}</h3>
            </div>
          </div>
          <div className="premium-card p-5 bg-white border-l-4 border-l-red-500 flex items-center gap-4">
            <div className="text-2xl text-red-500">🔥</div>
            <div>
              <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest">{t.overdue || 'Overdue'}</p>
              <h3 className="text-2xl font-black text-slate-800">{overdueCount}</h3>
            </div>
          </div>
          <div className="premium-card p-5 bg-white border-l-4 border-l-amber-500 flex items-center gap-4">
            <div className="text-2xl text-amber-500">📅</div>
            <div>
              <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest">{t.due_week || 'Due 7 Days'}</p>
              <h3 className="text-2xl font-black text-slate-800">{dueThisWeekCount}</h3>
            </div>
          </div>
          <div className="premium-card p-5 bg-white border-l-4 border-l-emerald-500 flex items-center gap-4">
            <div className="text-2xl text-emerald-500">✅</div>
            <div>
              <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest">{t.completed || 'Completed'}</p>
              <h3 className="text-2xl font-black text-slate-800">{completedCount}</h3>
            </div>
          </div>
        </div>

        <div className="lg:col-span-4 premium-card fade-in-up overflow-hidden">
          <div className="p-6 border-b border-slate-100 flex flex-col xl:flex-row justify-between xl:items-center bg-slate-50 gap-4">
            <div className="flex items-center gap-4">
                <h3 className="font-black text-slate-800 uppercase tracking-tighter text-lg">{t.active_decisions || 'Strategic Registry'}</h3>
                <div className="px-2 py-0.5 bg-slate-800 text-white text-[9px] font-black rounded uppercase tracking-widest">Total: {actions.length}</div>
            </div>
            <div className="flex flex-wrap items-center gap-3">
              <input
                type="text"
                placeholder={lang === 'fr' ? 'Rechercher tâches, projets...' : 'Search tasks, projects...'}
                value={searchTerm}
                onChange={e => setSearchTerm(e.target.value)}
                className="px-5 py-2.5 border border-slate-200 bg-white rounded-xl text-sm outline-none focus:ring-2 focus:ring-indigo-500/20 w-full sm:w-64 font-bold"
              />
              <button onClick={() => setShowAddForm(true)} className="bg-indigo-600 text-white px-6 py-2.5 rounded-xl text-xs font-black shadow-lg shadow-indigo-100 uppercase tracking-widest">+ New Directive</button>
              <button onClick={handleGenerateReport} className="bg-white text-slate-700 border border-slate-200 px-5 py-2.5 rounded-xl text-xs font-black uppercase tracking-widest shadow-sm">Audit Report</button>
            </div>
          </div>
          <div className="overflow-x-auto custom-scrollbar">
            <table className="w-full min-w-[1000px] text-left border-collapse">
              <thead>
                <tr className="bg-white border-b border-slate-100 text-[10px] uppercase tracking-[0.2em] text-slate-400 font-black">
                  <th className="px-8 py-5">{t.th_item || 'Directives / Projects'}</th>
                  <th className="px-8 py-5">{t.th_owner || 'Ownership'}</th>
                  <th className="px-8 py-5">{t.th_timeline || 'Timeline'}</th>
                  <th className="px-8 py-5">{t.th_status || 'Current Status'}</th>
                  <th className="px-8 py-5 text-right">{t.th_admin || 'Administrative'}</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {loading ? (
                  <tr><td colSpan={5} className="px-6 py-12 text-center text-slate-400 font-bold uppercase tracking-widest text-xs animate-pulse">Synchronizing Data...</td></tr>
                ) : filteredActions.length === 0 ? (
                  <tr><td colSpan={5} className="px-6 py-12 text-center text-slate-400 font-bold uppercase tracking-widest text-xs">No active directives found.</td></tr>
                ) : (
                  filteredActions.map(act => {
                    const isOverdue = new Date(act.due_date) < now && act.status !== 'Completed';
                    return (
                      <tr key={act.id} className={`${isOverdue ? "bg-red-50/20" : "hover:bg-slate-50/50"} transition-all duration-200 group`}>
                        <td className="px-8 py-6">
                          <p className="text-sm font-black text-slate-800 group-hover:text-indigo-600 transition-colors uppercase tracking-tight">{act.title}</p>
                          <div className="flex items-center gap-2 mt-1.5">
                            {act.project_name ? (
                                <span className="text-[9px] font-black bg-indigo-50 text-indigo-600 px-2 py-0.5 rounded border border-indigo-100 uppercase tracking-widest">📁 Project: {act.project_name}</span>
                            ) : (
                                <span className="text-[9px] font-black bg-slate-50 text-slate-400 px-2 py-0.5 rounded border border-slate-100 uppercase tracking-widest">Isolated Task</span>
                            )}
                            <span className={`text-[9px] font-black px-2 py-0.5 rounded border uppercase tracking-widest ${
                                act.priority === 'Critical' ? 'bg-red-50 text-red-600 border-red-100' :
                                act.priority === 'High' ? 'bg-amber-50 text-amber-600 border-amber-100' :
                                'bg-slate-50 text-slate-500 border-slate-100'
                            }`}>{act.priority}</span>
                          </div>
                        </td>
                        <td className="px-8 py-6">
                          <div className="flex items-center gap-3">
                            <div className="w-9 h-9 rounded-xl bg-slate-100 text-slate-600 flex items-center justify-center text-[10px] font-black border border-slate-200 shadow-sm">
                              {(act.assigned_first_name?.[0] || act.assigned_username?.[0] || '?').toUpperCase()}
                            </div>
                            <div className="flex flex-col">
                              <span className="text-xs font-black text-slate-700">
                                {act.assigned_first_name || act.assigned_last_name
                                  ? `${act.assigned_first_name || ''} ${act.assigned_last_name || ''}`.trim()
                                  : act.assigned_username}
                              </span>
                              <span className="text-[9px] text-slate-400 font-bold uppercase tracking-widest">@{act.assigned_username}</span>
                            </div>
                          </div>
                        </td>
                        <td className="px-8 py-6">
                            <div className="flex flex-col">
                                <span className={`text-xs font-black ${isOverdue ? 'text-red-500' : 'text-slate-700'}`}>
                                    {new Date(act.due_date).toLocaleDateString(undefined, { day: '2-digit', month: 'short', year: 'numeric' })}
                                </span>
                                <span className="text-[9px] text-slate-400 font-bold uppercase tracking-widest">{new Date(act.due_date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                            </div>
                        </td>
                        <td className="px-8 py-6">
                          <div className="flex flex-col gap-2">
                            <span className={`w-fit text-[9px] font-black px-2.5 py-1 rounded-full border uppercase tracking-[0.15em] ${
                                act.status === 'Completed' ? 'bg-emerald-50 text-emerald-600 border-emerald-100' :
                                act.status === 'In Progress' ? 'bg-indigo-50 text-indigo-600 border-indigo-100' :
                                isOverdue ? 'bg-red-50 text-red-600 border-red-100 animate-pulse' :
                                'bg-slate-50 text-slate-500 border-slate-100'
                            }`}>
                                {act.status}
                            </span>
                            
                            {act.status !== 'Completed' && (
                                <div className="flex gap-1">
                                    {act.status === 'Pending' && (
                                        <button onClick={() => handleUpdateStatus(act.id, 'In Progress')} className="text-[8px] font-black text-indigo-600 uppercase border border-indigo-100 px-1.5 py-0.5 rounded hover:bg-indigo-600 hover:text-white transition-colors tracking-tighter">Start Work</button>
                                    )}
                                    <button onClick={() => handleUpdateStatus(act.id, 'Completed')} className="text-[8px] font-black text-emerald-600 uppercase border border-emerald-100 px-1.5 py-0.5 rounded hover:bg-emerald-600 hover:text-white transition-colors tracking-tighter">Finalize</button>
                                </div>
                            )}
                          </div>
                        </td>
                        <td className="px-8 py-6 text-right">
                           {user?.role === 'Admin' && (
                                <button onClick={() => handleDeleteAction(act.id)} className="w-8 h-8 rounded-lg text-slate-300 hover:text-red-500 hover:bg-red-50 transition-all">🗑️</button>
                           )}
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Actions;
