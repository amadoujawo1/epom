import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import type { User } from '../App';

interface Document {
  id: number;
  title: string;
  file_path: string;
  status: string;
  category: string;
  uploader_name: string;
  doc_type: string;
  content: string;
  upload_date: string;
}

interface DocumentsProps {
  user: User | null;
  lang: 'en' | 'fr';
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  translations: Record<string, any>;
  token: string | null;
}

const Documents = ({ user, lang, translations, token }: DocumentsProps) => {
  const t = translations?.[lang]?.documents || translations?.['en']?.documents || {};
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);
  const [formMode, setFormMode] = useState<'note' | 'upload'>('note');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const [filter, setFilter] = useState('All');
  const [searchTerm, setSearchTerm] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [processingId, setProcessingId] = useState<number | null>(null);
  const [viewDoc, setViewDoc] = useState<Document | null>(null);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const [formData, setFormData] = useState({
    title: '',
    category: 'Minister Briefings',
    doc_type: 'Briefing Note',
    content: ''
  });

  const fetchDocuments = useCallback(async () => {
    if (!token) return;
    try {
      setLoading(true);
      const response = await axios.get(`/api/documents`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setDocuments(response.data);
    } catch {
      console.error("Failed to fetch documents");
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    fetchDocuments();
  }, [fetchDocuments]);

  const filteredDocuments = documents.filter((doc: Document) => {
    const matchesSearch = doc.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      doc.category.toLowerCase().includes(searchTerm.toLowerCase());
    if (!matchesSearch) return false;

    if (filter === 'All') return doc.status !== 'Archived';
    if (filter === 'Draft') return doc.status === 'Draft';
    if (filter === 'Pending Approval') return doc.status === 'Pending Approval' || doc.status === 'Pending Leader Clearance';
    if (filter === 'Archive') return doc.status === 'Archived';
    return true;
  });

  const handleView = (doc: Document) => {
    if (doc.file_path === 'digitized_note' || doc.doc_type === 'Official Report') {
      setViewDoc(doc);
    } else {
      window.open(`/api/documents/download/${doc.file_path}?token=${encodeURIComponent(token || '')}`, '_blank');
    }
  };

  const handleDownload = (doc: Document) => {
    if (doc.file_path === 'digitized_note') {
      const element = document.createElement("a");
      const file = new Blob([doc.content], { type: 'text/plain' });
      element.href = URL.createObjectURL(file);
      element.download = `${doc.title}.txt`;
      document.body.appendChild(element);
      element.click();
    } else {
      window.open(`/api/documents/download/${doc.file_path}?token=${encodeURIComponent(token || '')}&download=true`, '_blank');
    }
  };

  const handleDelete = async (docId: number) => {
    if (!window.confirm(lang === 'fr' ? 'Êtes-vous sûr de vouloir supprimer ce document ?' : 'Are you sure you want to delete this document?')) {
      return;
    }
    try {
      setProcessingId(docId);
      await axios.delete(`/api/documents/${docId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      fetchDocuments();
    } catch (err) {
      console.error("Delete failed", err);
    } finally {
      setProcessingId(null);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    if (!token) return;

    setIsSubmitting(true);
    try {
      if (formMode === 'upload' && selectedFile) {
        const data = new FormData();
        data.append('file', selectedFile);
        data.append('title', formData.title);
        data.append('category', formData.category);
        data.append('doc_type', formData.doc_type);

        await axios.post(`/api/documents/upload`, data, {
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'multipart/form-data'
          }
        });
      } else {
        await axios.post(`/api/documents/template`, formData, {
          headers: { Authorization: `Bearer ${token}` }
        });
      }

      setSuccess(lang === 'fr' ? 'Document enregistré avec succès !' : 'Document registered successfully!');
      setFormData({ title: '', category: 'Minister Briefings', doc_type: 'Briefing Note', content: '' });
      setSelectedFile(null);

      setTimeout(() => {
        setIsSubmitting(false);
        setShowAddForm(false);
        setSuccess('');
        fetchDocuments();
      }, 1500);
    } catch (err: unknown) {
      const axiosError = err as { response?: { data?: { error?: string } } };
      console.error("Submission failed", err);
      setError(axiosError.response?.data?.error || (lang === 'fr' ? "Échec de l'enregistrement" : 'Submission failed'));
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      {showAddForm && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 sm:p-6">
          {/* Glassmorphism backdrop */}
          <div
            className="absolute inset-0 bg-gradient-to-br from-slate-900/70 via-indigo-950/60 to-slate-900/70 backdrop-blur-md"
            onClick={() => !isSubmitting && setShowAddForm(false)}
          />

          <div className="relative w-full max-w-3xl rounded-[32px] overflow-hidden shadow-2xl shadow-indigo-900/30 scale-in-center flex flex-col" style={{ maxHeight: '92vh' }}>

            {/* ── HERO HEADER ── */}
            <div className="relative bg-gradient-to-r from-[#0f1225] via-[#1a1f3c] to-[#0f1225] px-8 pt-8 pb-6 shrink-0 overflow-hidden">
              {/* Decorative orbs */}
              <div className="absolute -top-10 -right-10 w-48 h-48 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />
              <div className="absolute -bottom-8 -left-8 w-40 h-40 bg-purple-500/10 rounded-full blur-3xl pointer-events-none" />

              <div className="relative flex items-start justify-between gap-4">
                <div className="flex items-center gap-4">
                  {/* Mode icon */}
                  <div className={`w-14 h-14 rounded-[20px] flex items-center justify-center text-2xl shadow-lg transition-all duration-300 ${formMode === 'upload' ? 'bg-gradient-to-br from-violet-500 to-purple-600 shadow-purple-500/30' : 'bg-gradient-to-br from-indigo-500 to-blue-600 shadow-indigo-500/30'}`}>
                    {formMode === 'upload' ? '📤' : '📝'}
                  </div>
                  <div>
                    <h3 className="text-xl font-black text-white tracking-tight leading-tight">
                      {formMode === 'upload'
                        ? (lang === 'fr' ? 'Ingestion de Document' : 'Document Ingestion')
                        : (t.form_title || 'Digitized Briefing Note')}
                    </h3>
                    <div className="flex items-center gap-2 mt-1.5 flex-wrap">
                      <span className="flex items-center gap-1.5 text-[10px] font-black text-emerald-400 uppercase tracking-widest">
                        <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse inline-block" />
                        Secure Workflow
                      </span>
                      <span className="text-slate-600 text-[10px]">•</span>
                      <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest bg-white/5 px-2 py-0.5 rounded border border-white/10">e-Info Vault</span>
                    </div>
                  </div>
                </div>
                <button
                  onClick={() => !isSubmitting && setShowAddForm(false)}
                  className="w-9 h-9 flex items-center justify-center rounded-full text-slate-400 hover:text-white hover:bg-white/10 transition-all shrink-0"
                  title="Close"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              {/* ── MODE TOGGLE PILL ── */}
              <div className="mt-6 inline-flex bg-white/5 border border-white/10 p-1 rounded-2xl gap-1">
                <button
                  type="button"
                  onClick={() => setFormMode('note')}
                  className={`flex items-center gap-2 px-5 py-2.5 rounded-xl text-[11px] font-black uppercase tracking-widest transition-all duration-200 ${formMode === 'note' ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-500/30' : 'text-slate-400 hover:text-white'}`}
                >
                  <span>📝</span> {lang === 'fr' ? 'Note Numérisée' : 'Digitized Note'}
                </button>
                <button
                  type="button"
                  onClick={() => setFormMode('upload')}
                  className={`flex items-center gap-2 px-5 py-2.5 rounded-xl text-[11px] font-black uppercase tracking-widest transition-all duration-200 ${formMode === 'upload' ? 'bg-violet-600 text-white shadow-lg shadow-violet-500/30' : 'text-slate-400 hover:text-white'}`}
                >
                  <span>📤</span> {lang === 'fr' ? 'Télécharger' : 'Upload File'}
                </button>
              </div>
            </div>

            {/* ── BODY ── */}
            <div className="bg-[#f8f9fe] overflow-y-auto custom-scrollbar flex-1">
              {/* Alert banners */}
              {error && (
                <div className="mx-8 mt-6 text-sm text-red-600 bg-red-50 p-4 rounded-2xl font-bold flex items-center gap-3 border border-red-100">
                  <span className="text-lg">⚠️</span> {error}
                </div>
              )}
              {success && (
                <div className="mx-8 mt-6 text-sm text-emerald-600 bg-emerald-50 p-4 rounded-2xl font-bold flex items-center gap-3 border border-emerald-100">
                  <span className="text-lg">✅</span> {success}
                </div>
              )}

              <form id="note-form-inner" onSubmit={handleSubmit} className="p-6 sm:p-8 space-y-6">
                {/* ── ROW 1: Title + Category ── */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                  {/* Title */}
                  <div className="space-y-2">
                    <label className="block text-[10px] font-black text-slate-400 uppercase tracking-[0.18em]">
                      {t.doc_title || 'Document Title'}
                    </label>
                    <div className="relative">
                      <div className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-300 pointer-events-none">
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15.232 5.232l3.536 3.536M9 11l6-6 3 3-6 6H9v-3z" />
                        </svg>
                      </div>
                      <input
                        required
                        type="text"
                        value={formData.title}
                        onChange={e => setFormData({ ...formData, title: e.target.value })}
                        className="w-full pl-10 pr-4 py-3.5 bg-white border border-slate-200 rounded-2xl focus:ring-2 focus:ring-indigo-400/40 focus:border-indigo-400 outline-none text-slate-800 font-semibold text-sm placeholder:font-normal placeholder:text-slate-400 transition-all shadow-sm"
                        placeholder={lang === 'fr' ? 'ex: Rapport Fiscal T4' : 'E.g. Q4 Fiscal Briefing'}
                      />
                    </div>
                  </div>

                  {/* Category */}
                  <div className="space-y-2">
                    <label className="block text-[10px] font-black text-slate-400 uppercase tracking-[0.18em]">
                      {t.category || 'Category'}
                    </label>
                    <div className="relative">
                      <div className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-300 pointer-events-none">
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
                        </svg>
                      </div>
                      <select
                        value={formData.category}
                        onChange={e => setFormData({ ...formData, category: e.target.value })}
                        className="w-full pl-10 pr-10 py-3.5 bg-white border border-slate-200 rounded-2xl focus:ring-2 focus:ring-indigo-400/40 focus:border-indigo-400 outline-none text-slate-800 font-semibold text-sm appearance-none cursor-pointer transition-all shadow-sm"
                      >
                        <option value="Minister Briefings">{t.categories?.briefings || 'Minister Briefings'}</option>
                        <option value="Decision Memos">{t.categories?.memos || 'Decision Memos'}</option>
                        <option value="Internal">{t.categories?.internal || 'Internal'}</option>
                        <option value="Restricted">{t.categories?.restricted || 'Restricted'}</option>
                        <option value="HR Documents">{t.categories?.hr_docs || 'HR Documents'}</option>
                        <option value="Employee Contracts">{t.categories?.contracts || 'Employee Contracts'}</option>
                        <option value="Identity Cards">{t.categories?.ids || 'Identity Cards'}</option>
                      </select>
                      <div className="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-slate-400">
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" />
                        </svg>
                      </div>
                    </div>
                  </div>
                </div>

                {/* ── ROW 2: Content / Upload ── */}
                {formMode === 'note' ? (
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <label className="block text-[10px] font-black text-slate-400 uppercase tracking-[0.18em]">
                        {t.content || 'Executive Summary / Details'}
                      </label>
                      <span className="text-[10px] font-bold text-slate-400 tabular-nums">
                        {formData.content.length} {lang === 'fr' ? 'car.' : 'chars'}
                      </span>
                    </div>
                    <div className="relative">
                      <textarea
                        required
                        rows={9}
                        value={formData.content}
                        onChange={e => setFormData({ ...formData, content: e.target.value })}
                        className="w-full px-6 py-5 bg-white border border-slate-200 rounded-2xl focus:ring-2 focus:ring-indigo-400/40 focus:border-indigo-400 outline-none resize-none text-slate-700 font-medium text-sm leading-relaxed placeholder:text-slate-400 transition-all shadow-sm"
                        placeholder={lang === 'fr' ? 'Saisissez les détails de la note ici...' : 'Enter briefing summary, key decisions, and relevant details...'}
                      />
                      {/* Subtle line-paper effect overlay */}
                      <div className="absolute bottom-4 right-5 text-2xl opacity-5 pointer-events-none select-none">📋</div>
                    </div>
                  </div>
                ) : (
                  <div className="space-y-2">
                    <label className="block text-[10px] font-black text-slate-400 uppercase tracking-[0.18em]">
                      {lang === 'fr' ? 'Fichier Document' : 'Physical Document File'}
                    </label>
                    <div className="relative">
                      <input
                        type="file"
                        required
                        onChange={e => setSelectedFile(e.target.files?.[0] || null)}
                        className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
                      />
                      <div className={`border-2 border-dashed rounded-2xl p-10 text-center transition-all group ${selectedFile ? 'border-indigo-400 bg-indigo-50/50' : 'border-slate-200 bg-white hover:bg-indigo-50/30 hover:border-indigo-300'}`}>
                        <div className="w-14 h-14 bg-white rounded-2xl shadow-md flex items-center justify-center text-2xl mb-3 mx-auto group-hover:scale-110 transition-transform border border-slate-100">
                          {selectedFile ? '✅' : '📄'}
                        </div>
                        <p className="text-sm font-black text-slate-700">
                          {selectedFile ? selectedFile.name : (t.drop_file || (lang === 'fr' ? 'Cliquez ou déposez le fichier ici' : 'Click or drop file here'))}
                        </p>
                        {selectedFile && (
                          <p className="text-xs text-slate-500 mt-1 font-medium">
                            {(selectedFile.size / 1024).toFixed(1)} KB
                          </p>
                        )}
                        {!selectedFile && (
                          <p className="text-xs text-slate-400 mt-1.5 font-medium">PDF, DOCX, JPG — Max 50 MB</p>
                        )}
                      </div>
                    </div>
                  </div>
                )}
              </form>
            </div>

            {/* ── FOOTER ── */}
            <div className="bg-white border-t border-slate-100 px-8 py-5 flex flex-col sm:flex-row items-center justify-between gap-4 shrink-0">
              {/* Shield info */}
              <div className="flex items-center gap-3 text-slate-400">
                <div className="w-9 h-9 rounded-xl bg-emerald-50 border border-emerald-100 flex items-center justify-center text-base shrink-0">🛡️</div>
                <div>
                  <p className="text-[10px] font-black tracking-widest uppercase text-slate-400">Vault Protection</p>
                  <p className="text-[10px] font-medium text-slate-500 leading-tight">
                    {lang === 'fr' ? 'Chiffré · Soumis au Centre d\'Intelligence' : 'Encrypted · Submitted to Intelligence Hub'}
                  </p>
                </div>
              </div>

              {/* Actions */}
              <div className="flex items-center gap-3 w-full sm:w-auto">
                <button
                  type="button"
                  onClick={() => !isSubmitting && setShowAddForm(false)}
                  className="flex-1 sm:flex-none px-6 py-3 text-slate-500 font-black text-xs uppercase tracking-widest rounded-xl hover:bg-slate-100 border border-slate-200 transition-all"
                >
                  {t.cancel_btn || 'Cancel'}
                </button>
                <button
                  type="submit"
                  form="note-form-inner"
                  disabled={isSubmitting}
                  className={`flex-1 sm:flex-none font-black text-xs uppercase tracking-widest py-3 px-8 rounded-xl shadow-lg transition-all active:scale-95 disabled:opacity-50 flex items-center justify-center gap-2 ${formMode === 'upload' ? 'bg-gradient-to-r from-violet-600 to-purple-600 text-white shadow-violet-500/25 hover:shadow-violet-500/40' : 'bg-gradient-to-r from-indigo-600 to-blue-600 text-white shadow-indigo-500/25 hover:shadow-indigo-500/40'}`}
                >
                  {isSubmitting ? (
                    <><span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin inline-block" />&nbsp;{lang === 'fr' ? 'Traitement...' : 'Processing...'}</>
                  ) : formMode === 'upload' ? (
                    <><span>📤</span>&nbsp;{lang === 'fr' ? 'Télécharger' : 'Upload File'}</>
                  ) : (
                    <><span>✦</span>&nbsp;{t.save_btn || 'Save & Initialize'}</>
                  )}
                </button>
              </div>
            </div>

          </div>
        </div>
      )}

      {/* VIEW MODAL */}
      {viewDoc && (
        <div className="fixed inset-0 z-[110] flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-slate-900/80 backdrop-blur-md" onClick={() => setViewDoc(null)}></div>
          <div className="relative w-full max-w-4xl bg-white rounded-[40px] shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
            <div className="p-8 bg-slate-50 border-b border-slate-100 flex justify-between items-center">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-2xl bg-indigo-100 text-indigo-600 flex items-center justify-center text-xl">📄</div>
                <div>
                  <h3 className="font-black text-xl text-slate-800">{viewDoc.title}</h3>
                  <p className="text-xs font-bold text-slate-400 uppercase tracking-widest">{viewDoc.category} • {viewDoc.doc_type}</p>
                </div>
              </div>
              <button onClick={() => setViewDoc(null)} className="w-10 h-10 rounded-full hover:bg-slate-200 flex items-center justify-center transition-colors">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path></svg>
              </button>
            </div>
            <div className="p-10 overflow-y-auto flex-1 bg-white">
              <div className="prose prose-slate max-w-none">
                <div className="text-slate-700 leading-relaxed whitespace-pre-wrap font-medium">
                  {viewDoc.content || (t.physical_attached || (lang === 'fr' ? "Fichier physique attaché. Utilisez le bouton de téléchargement pour y accéder." : "Physical file attached. Use the download button to access the full document."))}
                </div>
              </div>
            </div>
            <div className="p-8 bg-slate-900 flex justify-between items-center">
              <div className="text-slate-400 text-xs font-bold uppercase tracking-widest">
                {lang === 'fr' ? 'Archive officielle' : 'Official Archive'} • {new Date(viewDoc.upload_date).toLocaleDateString()}
              </div>
              <button
                onClick={() => handleDownload(viewDoc)}
                className="bg-white text-slate-900 px-8 py-3 rounded-xl font-black text-xs uppercase tracking-widest hover:bg-indigo-50 transition-all active:scale-95"
              >
                {lang === 'fr' ? 'Télécharger' : 'Download Document'}
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        {/* Sidebar Filters */}
        <div className="md:col-span-1 space-y-4">
          <div className="premium-card p-5 fade-in-up" style={{ animationDelay: '0.1s' }}>
            <h3 className="text-sm font-bold text-slate-400 uppercase tracking-wider mb-4">{t.category || 'Categories'}</h3>
            <ul className="space-y-2">
              <li>
                <button
                  onClick={() => setFilter('All')}
                  className={`w-full flex justify-between items-center text-sm font-medium px-3 py-2 rounded-lg transition-colors ${filter === 'All' ? 'text-indigo-600 bg-indigo-50' : 'text-slate-600 hover:bg-slate-50'}`}
                >
                  {t.categories?.all || 'All Documents'}
                  <span className={`px-2 py-0.5 rounded-full text-xs ${filter === 'All' ? 'bg-indigo-100 text-indigo-700' : 'bg-slate-100 text-slate-500'}`}>{documents.filter(d => d.status !== 'Archived').length}</span>
                </button>
              </li>
              <li>
                <button
                  onClick={() => setFilter('Draft')}
                  className={`w-full flex justify-between items-center text-sm font-medium px-3 py-2 rounded-lg transition-colors ${filter === 'Draft' ? 'text-indigo-600 bg-indigo-50' : 'text-slate-600 hover:bg-slate-50'}`}
                >
                  {t.categories?.drafts || 'Draft Documents'}
                  <span className={`px-2 py-0.5 rounded-full text-xs ${filter === 'Draft' ? 'bg-indigo-100 text-indigo-700' : 'bg-slate-100 text-slate-500'}`}>
                    {documents.filter(d => d.status === 'Draft').length}
                  </span>
                </button>
              </li>
              <li>
                <button
                  onClick={() => setFilter('Pending Approval')}
                  className={`w-full flex justify-between items-center text-sm font-medium px-3 py-2 rounded-lg transition-colors ${filter === 'Pending Approval' ? 'text-indigo-600 bg-indigo-50' : 'text-slate-600 hover:bg-slate-50'}`}
                >
                  {t.categories?.pending || 'Pending Approval'}
                  <span className={`px-2 py-0.5 rounded-full text-xs ${filter === 'Pending Approval' ? 'bg-indigo-100 text-indigo-700' : 'bg-slate-100 text-slate-500'}`}>
                    {documents.filter(d => d.status === 'Pending Approval' || d.status === 'Pending Leader Clearance').length}
                  </span>
                </button>
              </li>
              <li>
                <button
                  onClick={() => setFilter('Archive')}
                  className={`w-full flex justify-between items-center text-sm font-medium px-3 py-2 rounded-lg transition-colors ${filter === 'Archive' ? 'text-indigo-600 bg-indigo-50' : 'text-slate-600 hover:bg-slate-50'}`}
                >
                  {t.categories?.archive || 'Secure Archive'}
                  <span className={`px-2 py-0.5 rounded-full text-xs ${filter === 'Archive' ? 'bg-indigo-100 text-indigo-700' : 'bg-slate-100 text-slate-500'}`}>
                    {documents.filter(d => d.status === 'Archived').length}
                  </span>
                </button>
              </li>
            </ul>
          </div>

          <div className="bg-white border border-slate-100 rounded-3xl p-6 shadow-sm">
            <h3 className="font-black text-sm uppercase tracking-widest text-slate-800 mb-4">{t.strategic_info || 'Strategic Information'}</h3>
            <ul className="space-y-3">
              {t.bullets?.map((bullet: string, i: number) => (
                <li key={i} className="flex items-start gap-3">
                  <span className="text-emerald-500 mt-0.5">✔️</span>
                  <span className="text-sm font-medium text-slate-600 leading-relaxed">{bullet}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Main Document List */}
        <div className="md:col-span-3 premium-card overflow-hidden fade-in-up" style={{ animationDelay: '0.2s' }}>
          <div className="p-6 border-b border-slate-100 flex flex-col xl:flex-row justify-between xl:items-center bg-slate-50/50 gap-4">
            <h3 className="font-bold text-slate-700 uppercase tracking-tight">
              {filter === 'Draft' ? (t.categories?.drafts || 'Draft Documents') :
                filter === 'Pending Approval' ? (t.categories?.pending || 'Pending Approval') :
                  filter === 'Archive' ? (t.categories?.archive || 'Secure Archive') :
                    (t.recent || 'Recent Documents')}
            </h3>
            <div className="flex flex-wrap items-center gap-3">
              <input
                type="text"
                placeholder={t.search_ph || "Search notes..."}
                value={searchTerm}
                onChange={e => setSearchTerm(e.target.value)}
                className="px-4 py-2 border border-slate-200 rounded-xl text-sm bg-white focus:ring-2 focus:ring-indigo-500/20 outline-none w-full sm:w-auto"
              />
              <div className="flex items-center gap-2">

                <button
                  onClick={() => { setFormMode('note'); setShowAddForm(true); }}
                  className="bg-indigo-600 text-white px-4 py-2 rounded-xl text-xs font-black shadow-lg shadow-indigo-500/20 hover:bg-indigo-700 transition-all uppercase tracking-widest whitespace-nowrap"
                >
                  {t.new_btn || '+ New Note'}
                </button>
              </div>
            </div>
          </div>

          <div className="divide-y divide-slate-100">
            {loading ? (
              <div className="p-8 text-center text-slate-500">{t.loading || 'Loading documents...'}</div>
            ) : filteredDocuments.length === 0 ? (
              <div className="p-8 text-center text-slate-500">{t.no_docs || 'No documents found.'}</div>
            ) : (
              filteredDocuments.map((doc: Document) => (
                <div key={doc.id} className="p-4 hover:bg-indigo-50/30 transition-colors flex items-center justify-between group">
                  <div className="flex items-center gap-4 cursor-pointer" onClick={() => handleView(doc)}>
                    <div className="w-10 h-10 rounded-lg bg-blue-100 text-blue-600 flex items-center justify-center shrink-0">
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
                    </div>
                    <div>
                      <h4 className="font-bold text-slate-800 text-sm group-hover:text-indigo-600 transition-colors uppercase tracking-tight">{doc.title}</h4>
                      <div className="flex items-center gap-2 mt-1">
                        <span className={`text-[9px] font-black px-2 py-0.5 rounded-md border tracking-widest uppercase ${doc.category?.includes('Briefing') ? 'bg-purple-50 text-purple-600 border-purple-100' :
                          doc.category?.includes('Memo') ? 'bg-indigo-50 text-indigo-600 border-indigo-100' :
                          doc.category?.includes('Restricted') ? 'bg-rose-50 text-rose-600 border-rose-100' :
                          doc.category?.includes('HR') ? 'bg-emerald-50 text-emerald-600 border-emerald-100' :
                          doc.category?.includes('Contract') ? 'bg-amber-50 text-amber-600 border-amber-100' :
                          doc.category?.includes('Identity') ? 'bg-cyan-50 text-cyan-600 border-cyan-100' :
                          'bg-slate-50 text-slate-500 border-slate-100'
                          }`}>
                          {doc.category}
                        </span>
                        <span className="text-[10px] text-slate-400 font-medium">
                          • {t.created_by || 'by'} {doc.uploader_name}
                        </span>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    {(() => {
                      const getStatusLabel = (status: string) => {
                        if (status === 'Draft') return t.statuses?.draft || 'Draft';
                        if (status === 'Archived') return t.statuses?.archived || 'Archived';
                        if (status === 'Pending Approval') return t.statuses?.pending || 'Pending Approval';
                        if (status === 'Pending Leader Clearance') return t.statuses?.clearance || 'Pending Leader Clearance';
                        return status;
                      };

                      return (
                        <span className={`badge text-[10px] font-black uppercase tracking-widest px-2 py-1 rounded ${doc.status === 'Draft' ? 'bg-slate-100 text-slate-600' :
                          doc.status === 'Archived' ? 'bg-slate-800 text-white' :
                            'bg-amber-100 text-amber-700'
                          }`}>{getStatusLabel(doc.status)}</span>
                      );
                    })()}

                    <div className="flex items-center gap-2">
                      {doc.status === 'Draft' && (
                        <button
                          disabled={processingId === doc.id}
                          onClick={async () => {
                            try {
                              setProcessingId(doc.id);
                              await axios.put(`/api/documents/${doc.id}`, { status: 'Pending Leader Clearance' }, {
                                headers: { Authorization: `Bearer ${token}` }
                              });
                              fetchDocuments();
                            } catch (err) {
                              console.error("Clearance submit failed", err);
                            } finally {
                              setProcessingId(null);
                            }
                          }}
                          className="text-[10px] font-black text-indigo-600 hover:text-indigo-800 uppercase tracking-widest bg-indigo-50 px-3 py-1.5 rounded-lg transition-all disabled:opacity-50"
                        >
                          {processingId === doc.id ? '...' : (t.submit_btn || (lang === 'fr' ? 'Soumettre' : 'Submit'))}
                        </button>
                      )}

                      {(doc.status === 'Pending Leader Clearance' || doc.status === 'Pending Approval') && (
                        <button
                          disabled={processingId === doc.id}
                          onClick={async () => {
                            try {
                              setProcessingId(doc.id);
                              await axios.put(`/api/documents/${doc.id}`, { status: 'Archived' }, {
                                headers: { Authorization: `Bearer ${token}` }
                              });
                              fetchDocuments();
                            } catch (err) {
                              console.error("Archive failed", err);
                            } finally {
                              setProcessingId(null);
                            }
                          }}
                          className="text-[10px] font-black text-emerald-600 hover:text-emerald-800 uppercase tracking-widest bg-emerald-50 px-3 py-1.5 rounded-lg transition-all disabled:opacity-50"
                        >
                          {processingId === doc.id ? '...' : (t.approve_btn || (lang === 'fr' ? 'Approuver' : 'Approve'))}
                        </button>
                      )}

                      <button onClick={() => handleDownload(doc)} className="text-slate-400 hover:text-indigo-600 transition-colors p-2" title="Download">
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16v1a2 2 0 002 2h12a2 2 0 002-2v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path></svg>
                      </button>
                      <button onClick={() => handleView(doc)} className="text-slate-400 hover:text-indigo-600 transition-colors p-2" title="View">
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path></svg>
                      </button>
                      {user?.role === 'Admin' && (
                        <button disabled={processingId === doc.id} onClick={() => handleDelete(doc.id)} className="text-slate-400 hover:text-red-500 transition-colors p-2 disabled:opacity-50" title={lang === 'fr' ? 'Supprimer' : 'Delete'}>
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Documents;
