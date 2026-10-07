'use client';

import React, { useState, useEffect, useCallback } from 'react';
import {
  Shield,
  ShieldCheck,
  FileText,
  Lock,
  Brain,
  Network,
  Briefcase,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Eye,
  EyeOff,
  Upload,
  Activity,
  Layers,
  Sparkles,
  RefreshCw,
  UserCheck,
  Compass,
  FileCheck,
  ChevronRight,
  ArrowUpRight
} from 'lucide-react';
import { api } from '@/lib/api';
import {
  User,
  VaultDocument,
  Claim,
  Opportunity,
  EligibilityReport,
  DisclosurePreview,
  CareerGaps,
  AuditLogItem,
  GraphData
} from '@/types';

type ActiveTab =
  | 'dashboard'
  | 'vault'
  | 'credentials'
  | 'graph'
  | 'opportunities'
  | 'eligibility'
  | 'privacy'
  | 'career'
  | 'audit';

export default function VerifaiApp() {
  const [activeTab, setActiveTab] = useState<ActiveTab>('dashboard');
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(() => (typeof window !== 'undefined' ? api.getToken() : null));
  const [loading, setLoading] = useState<boolean>(true);
  const [actionLoading, setActionLoading] = useState<boolean>(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // Authentication State
  const [authMode, setAuthMode] = useState<'login' | 'register'>('login');
  const [email, setEmail] = useState('researcher@verifai.io');
  const [password, setPassword] = useState('ResearchPassword123!');
  const [fullName, setFullName] = useState('Dr. Alex Rivera');

  // Data States
  const [dashboard, setDashboard] = useState<any>(null);
  const [documents, setDocuments] = useState<VaultDocument[]>([]);
  const [selectedDoc, setSelectedDoc] = useState<VaultDocument | null>(null);
  const [claims, setClaims] = useState<Claim[]>([]);
  const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
  const [selectedOpportunity, setSelectedOpportunity] = useState<Opportunity | null>(null);
  const [eligibilityReport, setEligibilityReport] = useState<EligibilityReport | null>(null);
  const [disclosurePreview, setDisclosurePreview] = useState<DisclosurePreview | null>(null);
  const [packages, setPackages] = useState<any[]>([]);
  const [careerGaps, setCareerGaps] = useState<CareerGaps | null>(null);
  const [auditLogs, setAuditLogs] = useState<AuditLogItem[]>([]);
  const [graphData, setGraphData] = useState<GraphData | null>(null);

  // Form inputs
  const [newOppTitle, setNewOppTitle] = useState('Machine Learning Research Engineer');
  const [newOppOrg, setNewOppOrg] = useState('DeepMind Applied AI');
  const [newOppType, setNewOppType] = useState('JOB');
  const [newOppDesc, setNewOppDesc] = useState(
    'Applicants must possess a Bachelor degree in Computer Science (CSE) with minimum CGPA of 8.0 or above. Proficiency in Python and Machine Learning is required. Experience with Cloud or Docker is preferred.'
  );

  const fetchUserData = useCallback(async () => {
    setLoading(true);
    try {
      const [dash, docsRes, claimsRes, oppsRes, gaps, logsRes, graphRes] = await Promise.all([
        api.getDashboardSummary().catch(() => null),
        api.listDocuments().catch(() => ({ documents: [] })),
        api.listCredentials().catch(() => ({ claims: [] })),
        api.listOpportunities().catch(() => ({ opportunities: [] })),
        api.getCareerGaps().catch(() => null),
        api.getAuditLogs().catch(() => ({ logs: [] })),
        api.getKnowledgeGraph().catch(() => null),
      ]);

      if (dash) {
        setDashboard(dash);
        setUser(dash.user);
      }
      setDocuments(docsRes.documents || []);
      setClaims(claimsRes.claims || []);
      setOpportunities(oppsRes.opportunities || []);
      setCareerGaps(gaps);
      setAuditLogs(logsRes.logs || []);
      setGraphData(graphRes);

      if (oppsRes.opportunities && oppsRes.opportunities.length > 0) {
        setSelectedOpportunity((prev) => prev || oppsRes.opportunities[0]);
      }
    } catch (err: any) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (token) {
      fetchUserData();
    } else {
      setLoading(false);
    }
  }, [token, fetchUserData]);

  const showNotification = (text: string, type: 'success' | 'error' = 'success') => {
    setMessage({ text, type });
    setTimeout(() => setMessage(null), 5000);
  };

  const handleAuth = async (e: React.FormEvent) => {
    e.preventDefault();
    setActionLoading(true);
    try {
      if (authMode === 'register') {
        const res = await api.register(email, password, fullName);
        setUser(res.user);
        setToken(res.access_token);
        showNotification('Registration successful! Welcome to VERIFAI.');
      } else {
        const res = await api.login(email, password);
        setUser(res.user);
        setToken(res.access_token);
        showNotification('Authenticated successfully via Argon2id.');
      }
      await fetchUserData();
    } catch (err: any) {
      showNotification(err.message || 'Authentication error', 'error');
    } finally {
      setActionLoading(false);
    }
  };

  const handleLogout = async () => {
    await api.logout();
    setToken(null);
    setUser(null);
    showNotification('Logged out successfully.');
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setActionLoading(true);
    try {
      const doc = await api.uploadDocument(file);
      showNotification(`Document '${doc.filename}' encrypted with AES-256-GCM and structured claims extracted!`);
      await fetchUserData();
      setActiveTab('vault');
    } catch (err: any) {
      showNotification(err.message, 'error');
    } finally {
      setActionLoading(false);
    }
  };

  const handleCreateOpportunity = async (e: React.FormEvent) => {
    e.preventDefault();
    setActionLoading(true);
    try {
      const opp = await api.createOpportunity({
        title: newOppTitle,
        organization: newOppOrg,
        description: newOppDesc,
        opportunity_type: newOppType,
      });
      showNotification(`Opportunity ingested! Extracted ${opp.extracted_requirements.count} condition rules.`);
      await fetchUserData();
      setSelectedOpportunity(opp);
      setActiveTab('eligibility');
    } catch (err: any) {
      showNotification(err.message, 'error');
    } finally {
      setActionLoading(false);
    }
  };

  const handleEvaluate = async (oppId: string) => {
    setActionLoading(true);
    try {
      const rep = await api.evaluateEligibility(oppId);
      setEligibilityReport(rep);
      showNotification(`Eligibility evaluated: ${rep.status} (${rep.match_score}%)`);
    } catch (err: any) {
      showNotification(err.message, 'error');
    } finally {
      setActionLoading(false);
    }
  };

  const handlePreviewDisclosure = async (oppId: string) => {
    setActionLoading(true);
    try {
      const prev = await api.previewDisclosure(oppId);
      setDisclosurePreview(prev);
      setActiveTab('privacy');
    } catch (err: any) {
      showNotification(err.message, 'error');
    } finally {
      setActionLoading(false);
    }
  };

  const handleApproveDisclosure = async () => {
    if (!disclosurePreview) return;
    setActionLoading(true);
    try {
      const reqAttrs = disclosurePreview.requested_attributes.map((r) => r.attribute);
      const pkg = await api.approveDisclosure(disclosurePreview.opportunity_id, reqAttrs);
      showNotification(`Selective Disclosure Approved! W3C Package hash: ${pkg.package_hash.substring(0, 12)}...`);
      const pkgsRes = await api.listPackages();
      setPackages(pkgsRes.packages || []);
      await fetchUserData();
    } catch (err: any) {
      showNotification(err.message, 'error');
    } finally {
      setActionLoading(false);
    }
  };

  const seedSyntheticBenchmarkData = async () => {
    setActionLoading(true);
    try {
      // 1. Ingest synthetic academic transcript as simulated bytes
      const sampleBlob = new Blob([
        `%PDF-1.4\nUniversity Grade Sheet - Official Academic Transcript\nDegree: Bachelor of Technology\nBranch: Computer Science and Engineering (CSE)\nCGPA: 8.85\nKey Skills: Python, Machine Learning, Data Structures, FastAPI, SQL\nResidential Address: 104 Privacy Avenue, Cyber District 4\nDate of Birth: 24/09/2002\nPhone: +1-987-654-3210`
      ], { type: 'application/pdf' });
      const testFile = new File([sampleBlob], 'official_academic_transcript.pdf', { type: 'application/pdf' });
      await api.uploadDocument(testFile);

      // 2. Ingest benchmark opportunities
      await api.createOpportunity({
        title: 'Senior AI Platform Engineer',
        organization: 'DeepMind Advanced Research',
        description: 'Requires Bachelor of Technology in CSE with CGPA >= 7.5. Must have Python, Machine Learning, and SQL expertise.',
        opportunity_type: 'JOB',
      });

      await api.createOpportunity({
        title: 'Global Quantum & Cloud Fellowship',
        organization: 'European Research Institute',
        description: 'Applicants must possess Computer Science background with CGPA above 8.0 and German A2 language proficiency or Cloud Experience.',
        opportunity_type: 'SCHOLARSHIP',
      });

      showNotification('Benchmark dataset successfully loaded into your secure vault!');
      await fetchUserData();
    } catch (err: any) {
      showNotification(err.message, 'error');
    } finally {
      setActionLoading(false);
    }
  };

  if (!token) {
    return (
      <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col justify-center items-center px-4 relative overflow-hidden">
        {/* Subtle background glow */}
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[400px] bg-indigo-600/10 blur-[140px] pointer-events-none rounded-full" />
        <div className="absolute bottom-10 right-10 w-[400px] h-[300px] bg-emerald-600/10 blur-[120px] pointer-events-none rounded-full" />

        <div className="max-w-md w-full z-10">
          <div className="text-center mb-8">
            <div className="inline-flex items-center gap-2.5 px-4 py-1.5 rounded-full bg-slate-900 border border-slate-800 text-indigo-400 text-xs font-semibold mb-4">
              <Shield className="w-3.5 h-3.5" />
              <span>Zero-Trust Privacy & Credential Intelligence</span>
            </div>
            <h1 className="text-4xl font-extrabold tracking-tight text-white mb-2">VERIFAI</h1>
            <p className="text-slate-400 text-sm">
              &ldquo;Prove what matters. Share only what is needed.&rdquo;
            </p>
          </div>

          <div className="bg-slate-900/80 backdrop-blur-xl border border-slate-800 rounded-2xl p-7 shadow-2xl">
            <div className="flex border-b border-slate-800 mb-6">
              <button
                onClick={() => setAuthMode('login')}
                className={`flex-1 pb-3 text-sm font-semibold transition-all ${
                  authMode === 'login'
                    ? 'border-b-2 border-indigo-500 text-indigo-400'
                    : 'text-slate-400 hover:text-slate-300'
                }`}
              >
                Sign In
              </button>
              <button
                onClick={() => setAuthMode('register')}
                className={`flex-1 pb-3 text-sm font-semibold transition-all ${
                  authMode === 'register'
                    ? 'border-b-2 border-indigo-500 text-indigo-400'
                    : 'text-slate-400 hover:text-slate-300'
                }`}
              >
                Create Account
              </button>
            </div>

            <form onSubmit={handleAuth} className="space-y-4">
              {authMode === 'register' && (
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Full Name</label>
                  <input
                    type="text"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    required
                    className="w-full bg-slate-950/80 border border-slate-700/80 rounded-lg px-3.5 py-2.5 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500"
                    placeholder="Jane Doe"
                  />
                </div>
              )}

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Email Address</label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  className="w-full bg-slate-950/80 border border-slate-700/80 rounded-lg px-3.5 py-2.5 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500"
                  placeholder="user@example.com"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Password (Argon2id Salted)</label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  className="w-full bg-slate-950/80 border border-slate-700/80 rounded-lg px-3.5 py-2.5 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500"
                  placeholder="••••••••"
                />
              </div>

              <button
                type="submit"
                disabled={actionLoading}
                className="w-full bg-indigo-600 hover:bg-indigo-500 text-white font-medium py-2.5 rounded-lg transition-all duration-200 shadow-lg shadow-indigo-600/25 flex items-center justify-center gap-2 mt-2"
              >
                {actionLoading ? (
                  <RefreshCw className="w-4 h-4 animate-spin" />
                ) : authMode === 'login' ? (
                  <>
                    <Lock className="w-4 h-4" />
                    <span>Authenticate</span>
                  </>
                ) : (
                  <>
                    <UserCheck className="w-4 h-4" />
                    <span>Register New Identity</span>
                  </>
                )}
              </button>
            </form>

            <div className="mt-5 pt-4 border-t border-slate-800/80 text-center">
              <p className="text-xs text-slate-500">
                Encrypted at rest using AES-256-GCM. Passwords hashed with Argon2id. Zero plaintext storage.
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col antialiased">
      {/* Top Banner & Notifications */}
      {message && (
        <div
          className={`fixed top-4 right-4 z-50 px-4 py-3 rounded-xl border shadow-xl flex items-center gap-3 backdrop-blur-md transition-all ${
            message.type === 'success'
              ? 'bg-emerald-950/90 border-emerald-700 text-emerald-200'
              : 'bg-rose-950/90 border-rose-700 text-rose-200'
          }`}
        >
          {message.type === 'success' ? (
            <CheckCircle2 className="w-5 h-5 text-emerald-400" />
          ) : (
            <AlertTriangle className="w-5 h-5 text-rose-400" />
          )}
          <span className="text-sm font-medium">{message.text}</span>
        </div>
      )}

      {/* Main Header */}
      <header className="h-16 border-b border-slate-800 bg-slate-900/60 backdrop-blur-md px-6 flex items-center justify-between sticky top-0 z-30">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-600 to-indigo-400 flex items-center justify-center shadow-md shadow-indigo-600/30">
            <ShieldCheck className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-lg text-white tracking-tight">VERIFAI</span>
              <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-950/80 text-emerald-400 border border-emerald-800/60">
                AES-256-GCM Encrypted
              </span>
            </div>
            <p className="text-[11px] text-slate-400 font-normal">
              Privacy-Preserving AI Credential & Eligibility Intelligence
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={seedSyntheticBenchmarkData}
            disabled={actionLoading}
            className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-indigo-950/60 border border-indigo-800/60 text-indigo-300 text-xs font-medium hover:bg-indigo-900/60 transition-colors shadow-sm"
          >
            <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
            <span>Load Benchmark Suite</span>
          </button>

          <label className="cursor-pointer flex items-center gap-2 px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium transition-all shadow-md shadow-indigo-600/20">
            <Upload className="w-3.5 h-3.5" />
            <span>Upload Document</span>
            <input type="file" onChange={handleFileUpload} accept=".pdf,.png,.jpg,.jpeg" className="hidden" />
          </label>

          <div className="h-6 w-px bg-slate-800 mx-1" />

          <div className="flex items-center gap-2 text-xs text-slate-300">
            <div className="w-7 h-7 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-xs font-semibold text-slate-200">
              {user?.full_name ? user.full_name[0] : 'U'}
            </div>
            <span className="hidden md:inline font-medium">{user?.full_name || user?.email}</span>
            <button
              onClick={handleLogout}
              className="text-slate-400 hover:text-rose-400 text-xs ml-1 transition-colors"
            >
              Sign Out
            </button>
          </div>
        </div>
      </header>

      {/* App Body */}
      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar Navigation */}
        <aside className="w-64 border-r border-slate-800/80 bg-slate-900/40 p-4 flex flex-col gap-1 shrink-0">
          <div className="text-[11px] font-semibold text-slate-500 uppercase px-3 py-2">
            Intelligence Modules
          </div>

          <button
            onClick={() => setActiveTab('dashboard')}
            className={`flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all ${
              activeTab === 'dashboard'
                ? 'bg-indigo-600/15 text-indigo-300 border border-indigo-500/30'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
            }`}
          >
            <Activity className="w-4 h-4 text-indigo-400" />
            <span>Readiness Dashboard</span>
          </button>

          <button
            onClick={() => setActiveTab('vault')}
            className={`flex items-center justify-between px-3 py-2.5 rounded-xl text-sm font-medium transition-all ${
              activeTab === 'vault'
                ? 'bg-indigo-600/15 text-indigo-300 border border-indigo-500/30'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
            }`}
          >
            <div className="flex items-center gap-3">
              <Lock className="w-4 h-4 text-emerald-400" />
              <span>Document Vault</span>
            </div>
            <span className="text-xs px-2 py-0.5 rounded-full bg-slate-800 text-slate-400">
              {documents.length}
            </span>
          </button>

          <button
            onClick={() => setActiveTab('credentials')}
            className={`flex items-center justify-between px-3 py-2.5 rounded-xl text-sm font-medium transition-all ${
              activeTab === 'credentials'
                ? 'bg-indigo-600/15 text-indigo-300 border border-indigo-500/30'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
            }`}
          >
            <div className="flex items-center gap-3">
              <FileCheck className="w-4 h-4 text-cyan-400" />
              <span>Credential Profile</span>
            </div>
            <span className="text-xs px-2 py-0.5 rounded-full bg-slate-800 text-slate-400">
              {claims.length}
            </span>
          </button>

          <button
            onClick={() => setActiveTab('graph')}
            className={`flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all ${
              activeTab === 'graph'
                ? 'bg-indigo-600/15 text-indigo-300 border border-indigo-500/30'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
            }`}
          >
            <Network className="w-4 h-4 text-violet-400" />
            <span>Knowledge Graph</span>
          </button>

          <div className="text-[11px] font-semibold text-slate-500 uppercase px-3 pt-5 pb-2">
            Reasoning & Privacy
          </div>

          <button
            onClick={() => setActiveTab('opportunities')}
            className={`flex items-center justify-between px-3 py-2.5 rounded-xl text-sm font-medium transition-all ${
              activeTab === 'opportunities'
                ? 'bg-indigo-600/15 text-indigo-300 border border-indigo-500/30'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
            }`}
          >
            <div className="flex items-center gap-3">
              <Briefcase className="w-4 h-4 text-amber-400" />
              <span>Opportunity Analyzer</span>
            </div>
            <span className="text-xs px-2 py-0.5 rounded-full bg-slate-800 text-slate-400">
              {opportunities.length}
            </span>
          </button>

          <button
            onClick={() => setActiveTab('eligibility')}
            className={`flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all ${
              activeTab === 'eligibility'
                ? 'bg-indigo-600/15 text-indigo-300 border border-indigo-500/30'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
            }`}
          >
            <Brain className="w-4 h-4 text-indigo-400" />
            <span>Hybrid Eligibility Engine</span>
          </button>

          <button
            onClick={() => setActiveTab('privacy')}
            className={`flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all ${
              activeTab === 'privacy'
                ? 'bg-indigo-600/15 text-indigo-300 border border-indigo-500/30'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
            }`}
          >
            <EyeOff className="w-4 h-4 text-rose-400" />
            <span>Selective Disclosure</span>
          </button>

          <button
            onClick={() => setActiveTab('career')}
            className={`flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all ${
              activeTab === 'career'
                ? 'bg-indigo-600/15 text-indigo-300 border border-indigo-500/30'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
            }`}
          >
            <Compass className="w-4 h-4 text-orange-400" />
            <span>Career Gap Radar</span>
          </button>

          <div className="text-[11px] font-semibold text-slate-500 uppercase px-3 pt-5 pb-2">
            Governance & Audit
          </div>

          <button
            onClick={() => setActiveTab('audit')}
            className={`flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all ${
              activeTab === 'audit'
                ? 'bg-indigo-600/15 text-indigo-300 border border-indigo-500/30'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
            }`}
          >
            <Shield className="w-4 h-4 text-blue-400" />
            <span>Security Audit Trail</span>
          </button>

          <div className="mt-auto pt-4 border-t border-slate-800/80 px-2 text-[11px] text-slate-500 flex items-center justify-between">
            <span>W3C VC 2.0 Spec</span>
            <span className="text-emerald-400">Online</span>
          </div>
        </aside>

        {/* Content Area */}
        <main className="flex-1 overflow-y-auto p-6 md:p-8 bg-slate-950">
          {/* TAB 1: READINESS DASHBOARD */}
          {activeTab === 'dashboard' && (
            <div className="space-y-6 max-w-6xl">
              <div>
                <h2 className="text-2xl font-bold tracking-tight text-white">Eligibility & Readiness Intelligence</h2>
                <p className="text-sm text-slate-400 mt-1">
                  Continuous evaluation of personal verified credentials against market requirements.
                </p>
              </div>

              {/* Metric Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 backdrop-blur-md">
                  <div className="flex items-center justify-between text-slate-400 mb-2">
                    <span className="text-xs font-semibold uppercase tracking-wider">Vault Documents</span>
                    <Lock className="w-4 h-4 text-emerald-400" />
                  </div>
                  <div className="text-3xl font-extrabold text-white">{documents.length}</div>
                  <div className="text-xs text-emerald-400/90 mt-1 flex items-center gap-1">
                    <ShieldCheck className="w-3.5 h-3.5" />
                    <span>AES-256-GCM Encrypted</span>
                  </div>
                </div>

                <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 backdrop-blur-md">
                  <div className="flex items-center justify-between text-slate-400 mb-2">
                    <span className="text-xs font-semibold uppercase tracking-wider">Extracted Claims</span>
                    <FileCheck className="w-4 h-4 text-cyan-400" />
                  </div>
                  <div className="text-3xl font-extrabold text-white">{claims.length}</div>
                  <div className="text-xs text-cyan-400/90 mt-1">
                    {claims.filter((c) => c.category === 'SKILL').length} Verified Skills
                  </div>
                </div>

                <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 backdrop-blur-md">
                  <div className="flex items-center justify-between text-slate-400 mb-2">
                    <span className="text-xs font-semibold uppercase tracking-wider">Target Opportunities</span>
                    <Briefcase className="w-4 h-4 text-amber-400" />
                  </div>
                  <div className="text-3xl font-extrabold text-white">{opportunities.length}</div>
                  <div className="text-xs text-slate-400 mt-1">Ingested criteria rules</div>
                </div>

                <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 backdrop-blur-md">
                  <div className="flex items-center justify-between text-slate-400 mb-2">
                    <span className="text-xs font-semibold uppercase tracking-wider">Market Readiness</span>
                    <Brain className="w-4 h-4 text-indigo-400" />
                  </div>
                  <div className="text-3xl font-extrabold text-indigo-400">
                    {careerGaps ? `${careerGaps.market_readiness_score}%` : 'N/A'}
                  </div>
                  <div className="text-xs text-slate-400 mt-1">Average match across criteria</div>
                </div>
              </div>

              {/* Quick Flow Banner */}
              <div className="bg-gradient-to-r from-indigo-950/60 via-slate-900/60 to-slate-900/60 border border-indigo-800/40 rounded-2xl p-6 relative overflow-hidden">
                <div className="max-w-2xl">
                  <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-900/40 border border-indigo-700/50 text-indigo-300 text-xs font-medium mb-3">
                    <Sparkles className="w-3.5 h-3.5" />
                    <span>How VERIFAI Works</span>
                  </div>
                  <h3 className="text-lg font-bold text-white mb-2">
                    Upload Once. Prove Anywhere. Disclose Minimally.
                  </h3>
                  <p className="text-sm text-slate-300 leading-relaxed mb-4">
                    Your certificates and marksheets are encrypted locally. Multimodal AI extracts structured claims with visual grounding. When applying to an opportunity, VERIFAI reasons over evidence and mathematically strips non-required personal data (such as address and date of birth).
                  </p>
                  <div className="flex items-center gap-3">
                    <button
                      onClick={() => setActiveTab('vault')}
                      className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold transition-all shadow-md shadow-indigo-600/20 flex items-center gap-1.5"
                    >
                      <span>Go to Secure Vault</span>
                      <ChevronRight className="w-4 h-4" />
                    </button>
                    <button
                      onClick={seedSyntheticBenchmarkData}
                      className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium transition-all"
                    >
                      Load Sample Credentials
                    </button>
                  </div>
                </div>
              </div>

              {/* Recent Activity & Opportunities */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Opportunities Snapshot */}
                <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="font-bold text-sm text-white flex items-center gap-2">
                      <Briefcase className="w-4 h-4 text-amber-400" />
                      <span>Ingested Opportunities</span>
                    </h3>
                    <button
                      onClick={() => setActiveTab('opportunities')}
                      className="text-xs text-indigo-400 hover:text-indigo-300"
                    >
                      View All
                    </button>
                  </div>

                  {opportunities.length === 0 ? (
                    <div className="text-center py-8 text-slate-500 text-xs">
                      No opportunities ingested yet. Add job or scholarship requirements to evaluate eligibility.
                    </div>
                  ) : (
                    <div className="space-y-3">
                      {opportunities.slice(0, 3).map((opp) => (
                        <div
                          key={opp.id}
                          className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800/80 flex items-center justify-between hover:border-slate-700 transition-all cursor-pointer"
                          onClick={() => {
                            setSelectedOpportunity(opp);
                            handleEvaluate(opp.id);
                            setActiveTab('eligibility');
                          }}
                        >
                          <div>
                            <div className="text-sm font-semibold text-slate-200">{opp.title}</div>
                            <div className="text-xs text-slate-400 mt-0.5">{opp.organization}</div>
                          </div>
                          <div className="flex items-center gap-2">
                            <span className="text-[11px] px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-mono">
                              {opp.extracted_requirements?.count || 0} Rules
                            </span>
                            <ArrowUpRight className="w-4 h-4 text-slate-500" />
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {/* Audit Trail Snapshot */}
                <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="font-bold text-sm text-white flex items-center gap-2">
                      <Shield className="w-4 h-4 text-emerald-400" />
                      <span>Recent Security Audit Log</span>
                    </h3>
                    <button
                      onClick={() => setActiveTab('audit')}
                      className="text-xs text-indigo-400 hover:text-indigo-300"
                    >
                      Audit Trail
                    </button>
                  </div>

                  {auditLogs.length === 0 ? (
                    <div className="text-center py-8 text-slate-500 text-xs">
                      Audit log initialized. Security events will appear here.
                    </div>
                  ) : (
                    <div className="space-y-2.5">
                      {auditLogs.slice(0, 4).map((log) => (
                        <div
                          key={log.id}
                          className="p-2.5 rounded-lg bg-slate-950/40 border border-slate-800/60 flex items-center justify-between text-xs"
                        >
                          <div className="flex items-center gap-2">
                            <span className="w-2 h-2 rounded-full bg-emerald-400" />
                            <span className="font-mono text-slate-300">{log.event_type}</span>
                          </div>
                          <span className="font-mono text-slate-500 text-[10px]">
                            {new Date(log.created_at).toLocaleTimeString()}
                          </span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: DOCUMENT VAULT */}
          {activeTab === 'vault' && (
            <div className="space-y-6 max-w-6xl">
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                  <h2 className="text-2xl font-bold tracking-tight text-white">Secure Document Vault</h2>
                  <p className="text-sm text-slate-400 mt-1">
                    AES-256-GCM encrypted storage at rest with multimodal layout understanding.
                  </p>
                </div>

                <label className="cursor-pointer inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold transition-all shadow-lg shadow-indigo-600/25">
                  <Upload className="w-4 h-4" />
                  <span>Upload Certificate or Transcript</span>
                  <input type="file" onChange={handleFileUpload} accept=".pdf,.png,.jpg,.jpeg" className="hidden" />
                </label>
              </div>

              {documents.length === 0 ? (
                <div className="border border-dashed border-slate-800 rounded-3xl p-12 text-center bg-slate-900/20">
                  <div className="w-14 h-14 rounded-2xl bg-indigo-950/60 border border-indigo-800/60 flex items-center justify-center mx-auto mb-4 text-indigo-400">
                    <Lock className="w-7 h-7" />
                  </div>
                  <h3 className="text-lg font-bold text-white mb-2">Vault is Currently Empty</h3>
                  <p className="text-sm text-slate-400 max-w-md mx-auto mb-6">
                    Upload your degree certificates, marksheets, transcripts, or training certificates. They are encrypted using unique per-user keys derived via HKDF.
                  </p>
                  <button
                    onClick={seedSyntheticBenchmarkData}
                    className="px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium"
                  >
                    Load Sample Academic Transcript
                  </button>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
                  {documents.map((doc) => (
                    <div
                      key={doc.id}
                      className="bg-slate-900/70 border border-slate-800 rounded-2xl p-5 hover:border-slate-700 transition-all flex flex-col justify-between group"
                    >
                      <div>
                        <div className="flex items-start justify-between gap-3 mb-3">
                          <div className="w-10 h-10 rounded-xl bg-slate-800 flex items-center justify-center text-indigo-400 shrink-0">
                            <FileText className="w-5 h-5" />
                          </div>
                          <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-emerald-950/80 border border-emerald-800/60 text-emerald-400 font-semibold">
                            {doc.doc_type}
                          </span>
                        </div>

                        <h4 className="text-sm font-bold text-white truncate mb-1" title={doc.filename}>
                          {doc.filename}
                        </h4>
                        <div className="text-xs text-slate-400 flex items-center gap-2 mb-3">
                          <span>{(doc.file_size_bytes / 1024).toFixed(1)} KB</span>
                          <span>•</span>
                          <span className="text-emerald-400 font-mono flex items-center gap-1">
                            <ShieldCheck className="w-3 h-3" />
                            GCM Verified
                          </span>
                        </div>

                        <div className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-3 text-[11px] font-mono text-slate-400 space-y-1 mb-4">
                          <div className="flex justify-between">
                            <span>SHA-256:</span>
                            <span className="text-slate-300">{doc.sha256_hash.substring(0, 10)}...</span>
                          </div>
                          <div className="flex justify-between">
                            <span>Status:</span>
                            <span className="text-cyan-400">{doc.status}</span>
                          </div>
                          <div className="flex justify-between">
                            <span>Claims Found:</span>
                            <span className="text-indigo-300 font-semibold">{doc.claims_count || 'Analyzed'}</span>
                          </div>
                        </div>
                      </div>

                      <div className="flex items-center gap-2 pt-2 border-t border-slate-800/60">
                        <button
                          onClick={async () => {
                            const full = await api.getDocument(doc.id);
                            setSelectedDoc(full);
                          }}
                          className="flex-1 py-1.5 rounded-lg bg-indigo-950/60 hover:bg-indigo-900/60 text-indigo-300 text-xs font-medium border border-indigo-800/40 text-center"
                        >
                          Inspect Claims
                        </button>
                        <button
                          onClick={async () => {
                            if (confirm(`Securely delete '${doc.filename}' from vault and database?`)) {
                              await api.deleteDocument(doc.id);
                              showNotification('Document securely deleted.');
                              fetchUserData();
                            }
                          }}
                          className="px-2.5 py-1.5 rounded-lg bg-rose-950/40 hover:bg-rose-900/40 text-rose-400 text-xs border border-rose-800/30"
                        >
                          Delete
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* Document Claim Modal / Inspector */}
              {selectedDoc && (
                <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
                  <div className="bg-slate-900 border border-slate-800 rounded-3xl max-w-2xl w-full p-6 max-h-[85vh] flex flex-col shadow-2xl">
                    <div className="flex items-center justify-between pb-4 border-b border-slate-800">
                      <div>
                        <h3 className="font-bold text-white text-base">{selectedDoc.filename}</h3>
                        <p className="text-xs text-slate-400 font-mono mt-0.5">SHA-256: {selectedDoc.sha256_hash}</p>
                      </div>
                      <button
                        onClick={() => setSelectedDoc(null)}
                        className="text-slate-400 hover:text-white p-1"
                      >
                        ✕
                      </button>
                    </div>

                    <div className="py-4 overflow-y-auto space-y-4">
                      <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                        Extracted Structured Claims & Visual Grounding
                      </div>

                      {selectedDoc.claims && selectedDoc.claims.length > 0 ? (
                        <div className="space-y-2.5">
                          {selectedDoc.claims.map((c) => (
                            <div
                              key={c.id}
                              className="p-3 rounded-xl bg-slate-950/80 border border-slate-800 flex items-start justify-between"
                            >
                              <div>
                                <div className="flex items-center gap-2 mb-1">
                                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-indigo-950 border border-indigo-800/60 text-indigo-300">
                                    {c.category}
                                  </span>
                                  <span className="text-xs font-semibold text-white">{c.field_name}</span>
                                </div>
                                <div className="text-sm font-medium text-slate-200">
                                  {typeof c.field_value === 'object' ? JSON.stringify(c.field_value) : String(c.field_value)}
                                </div>
                                {c.bounding_box && (
                                  <div className="text-[10px] font-mono text-slate-500 mt-1">
                                    Visual Grounding: Page {c.page_number || 1} [x:{c.bounding_box.x}, y:{c.bounding_box.y}]
                                  </div>
                                )}
                              </div>

                              <div className="text-right">
                                <span className="text-xs font-mono font-semibold text-emerald-400">
                                  {(c.confidence * 100).toFixed(0)}% Conf
                                </span>
                              </div>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <div className="text-sm text-slate-500 py-4 text-center">
                          No direct claims materialized.
                        </div>
                      )}
                    </div>

                    <div className="pt-4 border-t border-slate-800 text-right">
                      <button
                        onClick={() => setSelectedDoc(null)}
                        className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium"
                      >
                        Close Inspector
                      </button>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* TAB 3: CREDENTIAL PROFILE */}
          {activeTab === 'credentials' && (
            <div className="space-y-6 max-w-6xl">
              <div>
                <h2 className="text-2xl font-bold tracking-tight text-white">Credential Profile & Claims</h2>
                <p className="text-sm text-slate-400 mt-1">
                  Canonical claims verified across all uploaded transcripts, degrees, and certificates.
                </p>
              </div>

              {claims.length === 0 ? (
                <div className="border border-dashed border-slate-800 rounded-3xl p-12 text-center bg-slate-900/20">
                  <FileCheck className="w-12 h-12 text-slate-600 mx-auto mb-3" />
                  <h3 className="text-base font-bold text-white mb-1">No Claims in Portfolio</h3>
                  <p className="text-xs text-slate-400 max-w-md mx-auto mb-4">
                    Upload transcripts or certificates into the Secure Vault to populate your structured claims portfolio.
                  </p>
                  <button
                    onClick={seedSyntheticBenchmarkData}
                    className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium"
                  >
                    Load Sample Academic Portfolio
                  </button>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                  {/* Education Claims */}
                  <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5">
                    <h3 className="text-sm font-bold text-white flex items-center gap-2 mb-4 pb-2 border-b border-slate-800">
                      <span className="w-2.5 h-2.5 rounded-full bg-cyan-400" />
                      <span>Academic & Education Claims</span>
                    </h3>
                    <div className="space-y-3">
                      {claims
                        .filter((c) => c.category === 'EDUCATION')
                        .map((c) => (
                          <div key={c.id} className="p-3 rounded-xl bg-slate-950/60 border border-slate-800">
                            <div className="text-xs text-slate-400 capitalize">{c.field_name.replace('_', ' ')}</div>
                            <div className="text-sm font-bold text-white mt-0.5">{String(c.field_value)}</div>
                            <div className="flex items-center justify-between text-[10px] text-slate-500 mt-2 font-mono">
                              <span>Source: {c.issuer || 'Registrar'}</span>
                              <span className="text-emerald-400">{(c.confidence * 100).toFixed(0)}% Confidence</span>
                            </div>
                          </div>
                        ))}
                    </div>
                  </div>

                  {/* Skill Claims */}
                  <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5">
                    <h3 className="text-sm font-bold text-white flex items-center gap-2 mb-4 pb-2 border-b border-slate-800">
                      <span className="w-2.5 h-2.5 rounded-full bg-indigo-400" />
                      <span>Evidenced Technical Skills</span>
                    </h3>
                    <div className="flex flex-wrap gap-2.5">
                      {claims
                        .filter((c) => c.category === 'SKILL')
                        .map((c) => (
                          <div
                            key={c.id}
                            className="px-3 py-1.5 rounded-xl bg-indigo-950/60 border border-indigo-800/60 text-indigo-300 text-xs font-medium flex items-center gap-2"
                          >
                            <span>{String(c.field_value)}</span>
                            <span className="text-[10px] text-indigo-400/80 font-mono">
                              {(c.confidence * 100).toFixed(0)}%
                            </span>
                          </div>
                        ))}
                    </div>
                  </div>

                  {/* Sensitive Identity Data (Protected by Selective Disclosure) */}
                  <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 md:col-span-2">
                    <h3 className="text-sm font-bold text-white flex items-center gap-2 mb-4 pb-2 border-b border-slate-800">
                      <EyeOff className="w-4 h-4 text-rose-400" />
                      <span>Sensitive Document Attributes (Automatic Zero-Trust Protection)</span>
                    </h3>
                    <p className="text-xs text-slate-400 mb-3">
                      The following attributes were detected during multimodal analysis of your files. Under VERIFAI&rsquo;s Zero-Trust policy, they are automatically flagged for redaction and withheld from all applications unless explicitly mandated.
                    </p>
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                      {claims
                        .filter((c) => c.category === 'IDENTITY')
                        .map((c) => (
                          <div key={c.id} className="p-3 rounded-xl bg-rose-950/20 border border-rose-900/40">
                            <div className="text-[11px] font-mono text-rose-400 uppercase tracking-wider">{c.field_name}</div>
                            <div className="text-xs text-slate-300 font-medium mt-1 truncate">{String(c.field_value)}</div>
                            <div className="text-[10px] text-rose-400/80 font-mono mt-2">Default: REDACTED</div>
                          </div>
                        ))}
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* TAB 4: KNOWLEDGE GRAPH */}
          {activeTab === 'graph' && (
            <div className="space-y-6 max-w-6xl">
              <div>
                <h2 className="text-2xl font-bold tracking-tight text-white">Personal Credential Knowledge Graph</h2>
                <p className="text-sm text-slate-400 mt-1">
                  Queryable entity-relationship graph connecting User, Credentials, Evidencing Documents, Skills, and Requirements.
                </p>
              </div>

              <div className="bg-slate-900/80 border border-slate-800 rounded-3xl p-6 min-h-[500px] flex flex-col justify-between">
                <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-800">
                  <div className="flex items-center gap-3">
                    <Network className="w-5 h-5 text-indigo-400" />
                    <span className="text-sm font-bold text-white">Interactive Graph Engine</span>
                    <span className="text-xs font-mono text-slate-400">
                      ({graphData?.node_count || 0} Nodes, {graphData?.edge_count || 0} Edges)
                    </span>
                  </div>
                  <button
                    onClick={fetchUserData}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 text-xs text-slate-300 hover:bg-slate-700 transition-colors"
                  >
                    <RefreshCw className="w-3.5 h-3.5" />
                    <span>Refresh Graph</span>
                  </button>
                </div>

                {/* Visual SVG Node-Link representation */}
                <div className="flex-1 w-full bg-slate-950/80 rounded-2xl border border-slate-800/80 p-6 flex flex-col items-center justify-center relative overflow-hidden">
                  <div className="w-full grid grid-cols-1 md:grid-cols-3 gap-6 z-10">
                    {/* User Identity Column */}
                    <div className="space-y-3">
                      <div className="text-xs font-bold text-indigo-400 uppercase tracking-wider">User Identity Node</div>
                      <div className="p-4 rounded-2xl bg-indigo-950/60 border border-indigo-700/60 shadow-lg">
                        <div className="flex items-center gap-2 text-sm font-bold text-white">
                          <UserCheck className="w-4 h-4 text-indigo-400" />
                          <span>{user?.full_name || 'Current User'}</span>
                        </div>
                        <div className="text-[11px] font-mono text-slate-400 mt-1 truncate">ID: {user?.id}</div>
                      </div>
                    </div>

                    {/* Claims & Skills Column */}
                    <div className="space-y-3">
                      <div className="text-xs font-bold text-cyan-400 uppercase tracking-wider">Claims & Skills Nodes</div>
                      <div className="space-y-2 max-h-80 overflow-y-auto pr-1">
                        {claims.slice(0, 5).map((c) => (
                          <div
                            key={c.id}
                            className="p-3 rounded-xl bg-slate-900 border border-slate-800 text-xs hover:border-cyan-500/50 transition-all"
                          >
                            <div className="flex justify-between items-center text-[10px] font-mono text-cyan-400">
                              <span>[:HAS_CLAIM]</span>
                              <span>{(c.confidence * 100).toFixed(0)}%</span>
                            </div>
                            <div className="font-semibold text-white mt-0.5">{c.field_name}</div>
                            <div className="text-slate-400 text-[11px]">{String(c.field_value)}</div>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Evidencing Documents Column */}
                    <div className="space-y-3">
                      <div className="text-xs font-bold text-emerald-400 uppercase tracking-wider">Evidence Nodes</div>
                      <div className="space-y-2 max-h-80 overflow-y-auto pr-1">
                        {documents.slice(0, 4).map((d) => (
                          <div
                            key={d.id}
                            className="p-3 rounded-xl bg-slate-900 border border-slate-800 text-xs hover:border-emerald-500/50 transition-all"
                          >
                            <div className="flex justify-between items-center text-[10px] font-mono text-emerald-400">
                              <span>[:EVIDENCED_BY]</span>
                              <span>{d.doc_type}</span>
                            </div>
                            <div className="font-semibold text-white mt-0.5 truncate">{d.filename}</div>
                            <div className="text-slate-400 text-[11px] font-mono">SHA: {d.sha256_hash.substring(0, 12)}...</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>

                <div className="mt-4 pt-3 border-t border-slate-800/80 text-xs text-slate-500 flex items-center justify-between">
                  <span>Graph schema: (User)-[:HAS_CLAIM]&rarr;(Claim)-[:EVIDENCED_BY]&rarr;(Document)</span>
                  <span className="font-mono">NetworkX / Neo4j Ready</span>
                </div>
              </div>
            </div>
          )}

          {/* TAB 5: OPPORTUNITY ANALYZER */}
          {activeTab === 'opportunities' && (
            <div className="space-y-6 max-w-6xl">
              <div>
                <h2 className="text-2xl font-bold tracking-tight text-white">Opportunity Ingestion & Requirement Extraction</h2>
                <p className="text-sm text-slate-400 mt-1">
                  Extract deterministic criteria rules and condition trees from unstructured job and scholarship descriptions.
                </p>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Form to Ingest Opportunity */}
                <div className="lg:col-span-1 bg-slate-900/70 border border-slate-800 rounded-3xl p-6">
                  <h3 className="font-bold text-sm text-white mb-4 flex items-center gap-2">
                    <Sparkles className="w-4 h-4 text-indigo-400" />
                    <span>Ingest New Opportunity</span>
                  </h3>

                  <form onSubmit={handleCreateOpportunity} className="space-y-4">
                    <div>
                      <label className="block text-xs font-medium text-slate-300 mb-1">Title</label>
                      <input
                        type="text"
                        value={newOppTitle}
                        onChange={(e) => setNewOppTitle(e.target.value)}
                        required
                        className="w-full bg-slate-950/80 border border-slate-700/80 rounded-lg px-3.5 py-2 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500"
                        placeholder="Job or Fellowship Title"
                      />
                    </div>

                    <div>
                      <label className="block text-xs font-medium text-slate-300 mb-1">Organization</label>
                      <input
                        type="text"
                        value={newOppOrg}
                        onChange={(e) => setNewOppOrg(e.target.value)}
                        required
                        className="w-full bg-slate-950/80 border border-slate-700/80 rounded-lg px-3.5 py-2 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500"
                        placeholder="Organization Name"
                      />
                    </div>

                    <div>
                      <label className="block text-xs font-medium text-slate-300 mb-1">Type</label>
                      <select
                        value={newOppType}
                        onChange={(e) => setNewOppType(e.target.value)}
                        className="w-full bg-slate-950/80 border border-slate-700/80 rounded-lg px-3.5 py-2 text-xs text-slate-100 focus:outline-none focus:border-indigo-500"
                      >
                        <option value="JOB">Job Position</option>
                        <option value="INTERNSHIP">Internship</option>
                        <option value="SCHOLARSHIP">Scholarship</option>
                        <option value="ADMISSION">University Admission</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-xs font-medium text-slate-300 mb-1">
                        Criteria & Description (Natural Language)
                      </label>
                      <textarea
                        rows={5}
                        value={newOppDesc}
                        onChange={(e) => setNewOppDesc(e.target.value)}
                        required
                        className="w-full bg-slate-950/80 border border-slate-700/80 rounded-lg px-3.5 py-2 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500"
                        placeholder="Enter eligibility text..."
                      />
                    </div>

                    <button
                      type="submit"
                      disabled={actionLoading}
                      className="w-full py-2.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-xs flex items-center justify-center gap-2 shadow-lg shadow-indigo-600/20"
                    >
                      {actionLoading ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Layers className="w-3.5 h-3.5" />}
                      <span>Extract Requirements Schema</span>
                    </button>
                  </form>
                </div>

                {/* List of Ingested Opportunities & Conditions */}
                <div className="lg:col-span-2 space-y-4">
                  <div className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                    Ingested Opportunities ({opportunities.length})
                  </div>

                  {opportunities.length === 0 ? (
                    <div className="p-8 border border-dashed border-slate-800 rounded-2xl text-center text-slate-500 text-sm">
                      No opportunities ingested yet. Submit criteria using the form on the left.
                    </div>
                  ) : (
                    opportunities.map((opp) => (
                      <div
                        key={opp.id}
                        className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 hover:border-slate-700 transition-all space-y-3"
                      >
                        <div className="flex items-start justify-between">
                          <div>
                            <span className="text-[10px] font-mono font-semibold px-2 py-0.5 rounded bg-amber-950/80 border border-amber-800/60 text-amber-400">
                              {opp.opportunity_type}
                            </span>
                            <h4 className="text-base font-bold text-white mt-1.5">{opp.title}</h4>
                            <div className="text-xs text-slate-400">{opp.organization}</div>
                          </div>

                          <div className="flex items-center gap-2">
                            <button
                              onClick={() => {
                                setSelectedOpportunity(opp);
                                handleEvaluate(opp.id);
                                setActiveTab('eligibility');
                              }}
                              className="px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium flex items-center gap-1"
                            >
                              <Brain className="w-3.5 h-3.5" />
                              <span>Evaluate Eligibility</span>
                            </button>
                          </div>
                        </div>

                        <p className="text-xs text-slate-300 bg-slate-950/40 p-3 rounded-xl border border-slate-800/60">
                          {opp.description}
                        </p>

                        <div>
                          <div className="text-[11px] font-semibold text-slate-400 uppercase mb-2">
                            Extracted Deterministic Rules ({opp.extracted_requirements?.count || 0})
                          </div>
                          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                            {opp.extracted_requirements?.requirements?.map((req, i) => (
                              <div
                                key={i}
                                className="p-2.5 rounded-lg bg-slate-950 border border-slate-800/80 text-xs flex items-center justify-between"
                              >
                                <div>
                                  <span className="text-[10px] font-mono text-indigo-400 uppercase">{req.field}: </span>
                                  <span className="font-semibold text-slate-200">
                                    {Array.isArray(req.value) ? req.value.join(', ') : String(req.value)}
                                  </span>
                                </div>
                                <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-800 text-slate-400">
                                  {req.operator}
                                </span>
                              </div>
                            ))}
                          </div>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            </div>
          )}

          {/* TAB 6: HYBRID ELIGIBILITY ENGINE */}
          {activeTab === 'eligibility' && (
            <div className="space-y-6 max-w-6xl">
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                  <h2 className="text-2xl font-bold tracking-tight text-white">Hybrid Eligibility Engine</h2>
                  <p className="text-sm text-slate-400 mt-1">
                    Multi-phase reasoning: Deterministic Rules + Calibrated Claim Confidence + Evidence Grounding.
                  </p>
                </div>

                {selectedOpportunity && (
                  <button
                    onClick={() => handleEvaluate(selectedOpportunity.id)}
                    disabled={actionLoading}
                    className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-md"
                  >
                    <RefreshCw className={`w-3.5 h-3.5 ${actionLoading ? 'animate-spin' : ''}`} />
                    <span>Re-evaluate Evidence</span>
                  </button>
                )}
              </div>

              {/* Opportunity Selector */}
              {opportunities.length > 0 && (
                <div className="flex items-center gap-2 overflow-x-auto pb-2">
                  <span className="text-xs text-slate-500 font-medium shrink-0">Select Target:</span>
                  {opportunities.map((opp) => (
                    <button
                      key={opp.id}
                      onClick={() => {
                        setSelectedOpportunity(opp);
                        handleEvaluate(opp.id);
                      }}
                      className={`px-3 py-1.5 rounded-xl text-xs font-medium whitespace-nowrap transition-all ${
                        selectedOpportunity?.id === opp.id
                          ? 'bg-indigo-600 text-white shadow-sm'
                          : 'bg-slate-900 border border-slate-800 text-slate-400 hover:text-white'
                      }`}
                    >
                      {opp.title}
                    </button>
                  ))}
                </div>
              )}

              {eligibilityReport ? (
                <div className="space-y-6">
                  {/* Score & Verdict Banner */}
                  <div className="bg-slate-900/80 border border-slate-800 rounded-3xl p-6 backdrop-blur-md flex flex-col md:flex-row items-center justify-between gap-6">
                    <div className="flex items-center gap-5">
                      <div
                        className={`w-20 h-20 rounded-2xl flex flex-col items-center justify-center font-extrabold text-2xl shadow-lg border ${
                          eligibilityReport.status === 'ELIGIBLE'
                            ? 'bg-emerald-950/80 border-emerald-700 text-emerald-400 shadow-emerald-900/30'
                            : eligibilityReport.status === 'PARTIALLY_ELIGIBLE'
                            ? 'bg-amber-950/80 border-amber-700 text-amber-400 shadow-amber-900/30'
                            : 'bg-rose-950/80 border-rose-700 text-rose-400 shadow-rose-900/30'
                        }`}
                      >
                        <span>{eligibilityReport.match_score}%</span>
                        <span className="text-[10px] font-semibold tracking-wider uppercase">Match</span>
                      </div>

                      <div>
                        <div className="flex items-center gap-2">
                          <span
                            className={`text-xs font-bold font-mono px-2.5 py-0.5 rounded-full uppercase ${
                              eligibilityReport.status === 'ELIGIBLE'
                                ? 'bg-emerald-950 text-emerald-400 border border-emerald-800'
                                : eligibilityReport.status === 'PARTIALLY_ELIGIBLE'
                                ? 'bg-amber-950 text-amber-400 border border-amber-800'
                                : 'bg-rose-950 text-rose-400 border border-rose-800'
                            }`}
                          >
                            Verdict: {eligibilityReport.status.replace('_', ' ')}
                          </span>
                        </div>
                        <h3 className="text-xl font-bold text-white mt-1.5">
                          {selectedOpportunity?.title}
                        </h3>
                        <p className="text-xs text-slate-400">{selectedOpportunity?.organization}</p>
                      </div>
                    </div>

                    <button
                      onClick={() => handlePreviewDisclosure(eligibilityReport.opportunity_id)}
                      className="px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs transition-all shadow-lg shadow-indigo-600/25 flex items-center gap-2"
                    >
                      <EyeOff className="w-4 h-4" />
                      <span>Review Selective Disclosure</span>
                    </button>
                  </div>

                  {/* Requirements Breakdown (Satisfied vs Missing) */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* Satisfied Criteria with Evidence Citations */}
                    <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5">
                      <h4 className="text-sm font-bold text-emerald-400 flex items-center gap-2 mb-4 pb-2 border-b border-slate-800">
                        <CheckCircle2 className="w-4 h-4" />
                        <span>Satisfied Requirements ({eligibilityReport.satisfied_rules.length})</span>
                      </h4>

                      <div className="space-y-3">
                        {eligibilityReport.satisfied_rules.map((item, i) => (
                          <div key={i} className="p-3.5 rounded-xl bg-slate-950 border border-emerald-900/40 space-y-2">
                            <div className="flex items-start justify-between">
                              <span className="text-xs font-bold text-white">{item.rule.description}</span>
                              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800/60 font-semibold">
                                Proven
                              </span>
                            </div>

                            {item.evidence && (
                              <div className="text-[11px] font-mono bg-slate-900/80 p-2 rounded-lg text-slate-300 border border-slate-800">
                                <div className="text-emerald-400 font-semibold flex items-center gap-1">
                                  <FileText className="w-3 h-3" />
                                  <span>{item.evidence.document_name}</span>
                                </div>
                                <div className="text-slate-400 text-[10px] mt-0.5">
                                  Claim: {item.evidence.field_name} = {String(item.evidence.field_value)} (Page {item.evidence.page_number})
                                </div>
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Missing Requirements */}
                    <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5">
                      <h4 className="text-sm font-bold text-rose-400 flex items-center gap-2 mb-4 pb-2 border-b border-slate-800">
                        <XCircle className="w-4 h-4" />
                        <span>Missing / Unevidenced Criteria ({eligibilityReport.missing_rules.length})</span>
                      </h4>

                      {eligibilityReport.missing_rules.length === 0 ? (
                        <div className="text-xs text-emerald-400 py-6 text-center font-medium">
                          ✓ All mandatory criteria have supporting evidence!
                        </div>
                      ) : (
                        <div className="space-y-3">
                          {eligibilityReport.missing_rules.map((item, i) => (
                            <div key={i} className="p-3.5 rounded-xl bg-slate-950 border border-rose-900/40 space-y-1">
                              <div className="text-xs font-bold text-white">{item.rule.description}</div>
                              <div className="text-[11px] text-rose-400/90">{item.reason}</div>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Explainable AI Report */}
                  <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6">
                    <h4 className="text-sm font-bold text-white flex items-center gap-2 mb-3">
                      <Brain className="w-4 h-4 text-indigo-400" />
                      <span>Explainable AI Reasoning Report</span>
                    </h4>
                    <div className="bg-slate-950/80 p-5 rounded-xl border border-slate-800 text-xs text-slate-300 leading-relaxed font-sans whitespace-pre-line">
                      {eligibilityReport.explanation_markdown}
                    </div>
                  </div>
                </div>
              ) : (
                <div className="p-12 border border-dashed border-slate-800 rounded-3xl text-center text-slate-500 text-sm">
                  Select an opportunity and click &ldquo;Evaluate Eligibility&rdquo; to execute the hybrid reasoning engine.
                </div>
              )}
            </div>
          )}

          {/* TAB 7: SELECTIVE DISCLOSURE & PRIVACY ENGINE */}
          {activeTab === 'privacy' && (
            <div className="space-y-6 max-w-6xl">
              <div>
                <h2 className="text-2xl font-bold tracking-tight text-white">Privacy & Selective Disclosure Center</h2>
                <p className="text-sm text-slate-400 mt-1">
                  Enforces Data Minimization: Calculates strictly necessary information and redacts unneeded PII.
                </p>
              </div>

              {disclosurePreview ? (
                <div className="space-y-6">
                  {/* Privacy Metric Banner */}
                  <div className="bg-gradient-to-r from-emerald-950/60 via-slate-900/60 to-slate-900/60 border border-emerald-800/40 rounded-3xl p-6 flex flex-col sm:flex-row items-center justify-between gap-6">
                    <div>
                      <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-900/40 border border-emerald-700/60 text-emerald-300 text-xs font-semibold mb-2">
                        <ShieldCheck className="w-3.5 h-3.5" />
                        <span>Data Minimization Policy Active</span>
                      </div>
                      <h3 className="text-lg font-bold text-white">
                        Selective Disclosure for {disclosurePreview.opportunity_title}
                      </h3>
                      <p className="text-xs text-slate-400 mt-0.5">
                        Target Organization: {disclosurePreview.organization}
                      </p>
                    </div>

                    <div className="text-center sm:text-right">
                      <div className="text-3xl font-extrabold text-emerald-400">
                        {disclosurePreview.disclosure_reduction_percentage}%
                      </div>
                      <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                        Disclosure Reduction (DRP)
                      </div>
                    </div>
                  </div>

                  {/* Side-by-side Attribute Comparison */}
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* Disclosed / Requested */}
                    <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-5 space-y-3">
                      <h4 className="text-xs font-bold text-emerald-400 uppercase tracking-wider flex items-center gap-1.5 pb-2 border-b border-slate-800">
                        <Eye className="w-4 h-4" />
                        <span>Disclosed Attributes (Strictly Required)</span>
                      </h4>

                      {disclosurePreview.requested_attributes.map((req, i) => (
                        <div key={i} className="p-3 rounded-xl bg-slate-950 border border-emerald-900/30 flex items-start justify-between">
                          <div>
                            <div className="text-xs font-bold text-white">{req.attribute}</div>
                            <div className="text-[11px] text-slate-300 font-mono mt-0.5">{req.value_preview}</div>
                            <div className="text-[10px] text-slate-500 mt-1">Needed for: {req.required_by}</div>
                          </div>
                          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800/50 font-semibold">
                            ALLOW
                          </span>
                        </div>
                      ))}
                    </div>

                    {/* Redacted / Protected */}
                    <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-5 space-y-3">
                      <h4 className="text-xs font-bold text-rose-400 uppercase tracking-wider flex items-center gap-1.5 pb-2 border-b border-slate-800">
                        <EyeOff className="w-4 h-4" />
                        <span>Protected & Redacted Attributes (Withheld)</span>
                      </h4>

                      {disclosurePreview.redacted_attributes.map((red, i) => (
                        <div key={i} className="p-3 rounded-xl bg-slate-950 border border-rose-900/30 flex items-start justify-between">
                          <div>
                            <div className="text-xs font-bold text-slate-200">{red.attribute}</div>
                            <div className="text-[11px] text-rose-300/80 mt-0.5">{red.reason}</div>
                          </div>
                          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-rose-950 text-rose-400 border border-rose-800/50 font-semibold">
                            WITHHOLD
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Explicit User Approval CTA */}
                  <div className="bg-slate-900/90 border border-indigo-900/50 rounded-2xl p-6 flex flex-col sm:flex-row items-center justify-between gap-4">
                    <div className="text-xs text-slate-300">
                      <span className="font-bold text-white block mb-0.5">Human-in-the-Loop Approval Required</span>
                      No data will be submitted or shared autonomously. Approving signs and generates an authenticated W3C Verifiable Presentation package.
                    </div>

                    <button
                      onClick={handleApproveDisclosure}
                      disabled={actionLoading}
                      className="px-6 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs shadow-lg shadow-indigo-600/30 whitespace-nowrap"
                    >
                      {actionLoading ? 'Packaging...' : 'Approve & Generate W3C Package'}
                    </button>
                  </div>
                </div>
              ) : (
                <div className="p-12 border border-dashed border-slate-800 rounded-3xl text-center text-slate-500 text-sm">
                  Run an eligibility evaluation on any target opportunity to generate its Minimum Disclosure preview.
                </div>
              )}
            </div>
          )}

          {/* TAB 8: CAREER GAP RADAR */}
          {activeTab === 'career' && (
            <div className="space-y-6 max-w-6xl">
              <div>
                <h2 className="text-2xl font-bold tracking-tight text-white">Career Gap Intelligence</h2>
                <p className="text-sm text-slate-400 mt-1">
                  Aggregated analysis of recurring missing skills across target opportunities.
                </p>
              </div>

              {careerGaps ? (
                <div className="space-y-6">
                  {/* Top Stats */}
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
                    <div className="p-5 rounded-2xl bg-slate-900/70 border border-slate-800">
                      <div className="text-xs font-semibold text-slate-400 uppercase">Opportunities Sampled</div>
                      <div className="text-3xl font-extrabold text-white mt-1">
                        {careerGaps.total_opportunities_analyzed}
                      </div>
                    </div>

                    <div className="p-5 rounded-2xl bg-slate-900/70 border border-slate-800">
                      <div className="text-xs font-semibold text-slate-400 uppercase">Portfolio Skill Count</div>
                      <div className="text-3xl font-extrabold text-cyan-400 mt-1">
                        {careerGaps.user_skill_count}
                      </div>
                    </div>

                    <div className="p-5 rounded-2xl bg-slate-900/70 border border-slate-800">
                      <div className="text-xs font-semibold text-slate-400 uppercase">Market Readiness Score</div>
                      <div className="text-3xl font-extrabold text-indigo-400 mt-1">
                        {careerGaps.market_readiness_score}%
                      </div>
                    </div>
                  </div>

                  {/* Prioritized Missing Skills Bar List */}
                  <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-6">
                    <h3 className="text-sm font-bold text-white mb-4">
                      Prioritized Skill Gaps (High Market Demand vs Missing in Vault)
                    </h3>

                    {careerGaps.top_skill_gaps.length === 0 ? (
                      <div className="text-xs text-slate-500 py-6 text-center">
                        No recurring skill gaps identified. Either all criteria are satisfied or more opportunities are needed.
                      </div>
                    ) : (
                      <div className="space-y-4">
                        {careerGaps.top_skill_gaps.map((gap, i) => (
                          <div key={i} className="space-y-1.5">
                            <div className="flex justify-between text-xs">
                              <span className="font-bold text-white">{gap.skill}</span>
                              <span className="text-amber-400 font-mono">
                                Missing in {gap.missing_in_opportunities} of {careerGaps.total_opportunities_analyzed} targets ({gap.gap_percentage}%)
                              </span>
                            </div>
                            <div className="w-full bg-slate-950 h-2.5 rounded-full overflow-hidden border border-slate-800">
                              <div
                                className="bg-gradient-to-r from-amber-500 to-rose-500 h-full rounded-full"
                                style={{ width: `${gap.gap_percentage}%` }}
                              />
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              ) : (
                <div className="p-12 border border-dashed border-slate-800 rounded-3xl text-center text-slate-500 text-sm">
                  Loading career gap analytics...
                </div>
              )}
            </div>
          )}

          {/* TAB 9: SECURITY AUDIT TRAIL */}
          {activeTab === 'audit' && (
            <div className="space-y-6 max-w-6xl">
              <div>
                <h2 className="text-2xl font-bold tracking-tight text-white">Security & Audit Trail</h2>
                <p className="text-sm text-slate-400 mt-1">
                  Tamper-evident, append-only security log recording cryptographic hashes of all authentication, upload, and disclosure events.
                </p>
              </div>

              <div className="bg-slate-900/80 border border-slate-800 rounded-3xl overflow-hidden shadow-2xl">
                <div className="p-5 border-b border-slate-800 flex items-center justify-between">
                  <div className="flex items-center gap-2 text-xs font-semibold text-slate-300">
                    <Shield className="w-4 h-4 text-emerald-400" />
                    <span>Cryptographic Audit Entries ({auditLogs.length})</span>
                  </div>
                  <button
                    onClick={fetchUserData}
                    className="flex items-center gap-1.5 px-3 py-1 rounded-lg bg-slate-800 text-xs text-slate-300 hover:bg-slate-700"
                  >
                    <RefreshCw className="w-3 h-3" />
                    <span>Refresh</span>
                  </button>
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs">
                    <thead className="bg-slate-950/60 text-slate-400 uppercase font-mono text-[10px] border-b border-slate-800">
                      <tr>
                        <th className="px-5 py-3">Timestamp (UTC)</th>
                        <th className="px-5 py-3">Event Type</th>
                        <th className="px-5 py-3">Status</th>
                        <th className="px-5 py-3">Integrity Checksum (SHA-256)</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/60 font-mono">
                      {auditLogs.map((log) => (
                        <tr key={log.id} className="hover:bg-slate-800/30 transition-colors">
                          <td className="px-5 py-3 text-slate-400 text-[11px]">
                            {new Date(log.created_at).toLocaleString()}
                          </td>
                          <td className="px-5 py-3 font-semibold text-slate-200">{log.event_type}</td>
                          <td className="px-5 py-3">
                            <span
                              className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
                                log.status === 'SUCCESS'
                                  ? 'bg-emerald-950 text-emerald-400 border border-emerald-800/60'
                                  : 'bg-rose-950 text-rose-400 border border-rose-800/60'
                              }`}
                            >
                              {log.status}
                            </span>
                          </td>
                          <td className="px-5 py-3 text-slate-500 text-[11px] truncate max-w-xs" title={log.metadata_hash}>
                            {log.metadata_hash}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
