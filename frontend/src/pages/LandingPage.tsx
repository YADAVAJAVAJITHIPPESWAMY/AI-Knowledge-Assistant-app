import React from 'react';
import { Link } from 'react-router-dom';
import {
  BrainCircuit,
  FileCheck2,
  Search,
  Sparkles,
  Shield,
  ArrowRight,
  Database,
  Layers,
  FileText,
  Lock,
  Cpu,
  BookOpen
} from 'lucide-react';

export const LandingPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-[#F8FAFC] text-slate-800">
      {/* Top Navbar */}
      <header className="sticky top-0 z-40 bg-white/80 backdrop-blur-md border-b border-slate-200/80">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-tr from-brand-600 to-brand-purple text-white shadow-md shadow-brand-500/20">
              <BrainCircuit className="w-6 h-6" />
            </div>
            <span className="text-lg font-bold text-slate-900 tracking-tight">
              Knowledge Assistant
            </span>
          </div>

          <div className="flex items-center gap-4">
            <Link
              to="/login"
              className="text-sm font-semibold text-slate-600 hover:text-slate-900 transition-colors"
            >
              Log in
            </Link>
            <Link
              to="/register"
              className="px-4 py-2 text-sm font-semibold text-white bg-gradient-to-r from-brand-600 to-brand-purple hover:from-brand-700 hover:to-brand-violet rounded-xl shadow-sm transition-all"
            >
              Get Started
            </Link>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative pt-16 pb-20 px-6 max-w-7xl mx-auto text-center overflow-hidden">
        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-brand-50 border border-brand-200 text-brand-700 text-xs font-semibold mb-6">
          <Sparkles className="w-3.5 h-3.5 text-brand-600" />
          <span>Next-Generation RAG Architecture</span>
        </div>

        <h1 className="text-4xl sm:text-6xl font-extrabold text-slate-900 tracking-tight max-w-4xl mx-auto leading-tight sm:leading-none">
          Your personal knowledge base,{' '}
          <span className="bg-gradient-to-r from-brand-600 via-brand-purple to-pink-500 bg-clip-text text-transparent">
            grounded in reality.
          </span>
        </h1>

        <p className="mt-6 text-lg text-slate-600 max-w-2xl mx-auto leading-relaxed">
          Upload PDF textbooks, Word reports, PowerPoint slides, and Markdown notes. Ask complex questions and receive conversational AI answers with verifiable citations down to the exact page and paragraph.
        </p>

        <div className="mt-8 flex flex-wrap items-center justify-center gap-4">
          <Link
            to="/register"
            className="flex items-center gap-2 px-6 py-3.5 text-sm font-bold text-white bg-gradient-to-r from-brand-600 to-brand-purple hover:from-brand-700 hover:to-brand-violet rounded-xl shadow-lg shadow-brand-500/25 transition-all"
          >
            <span>Start Learning Free</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
          <Link
            to="/login"
            className="px-6 py-3.5 text-sm font-semibold text-slate-700 bg-white hover:bg-slate-50 border border-slate-200 rounded-xl shadow-sm transition-colors"
          >
            Sign In to Workspace
          </Link>
        </div>

        {/* Supported Formats */}
        <div className="mt-12 flex flex-wrap items-center justify-center gap-2 text-xs font-medium text-slate-600">
          <span className="text-slate-400">Supported Formats:</span>
          {['PDF', 'DOCX', 'DOC', 'PPTX', 'PPT', 'TXT', 'Markdown'].map((fmt) => (
            <span key={fmt} className="px-2.5 py-1 rounded-lg bg-slate-200/60 border border-slate-300/60 font-mono">
              .{fmt.toLowerCase()}
            </span>
          ))}
        </div>
      </section>

      {/* Visual RAG Workflow Section */}
      <section className="py-16 bg-white border-y border-slate-200/80">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center max-w-2xl mx-auto mb-12">
            <h2 className="text-2xl sm:text-3xl font-bold text-slate-900">
              How Retrieval-Augmented Generation (RAG) Works
            </h2>
            <p className="mt-3 text-sm text-slate-600">
              Unlike generic AI chatbots that hallucinate facts, our system grounds every claim directly in your uploaded materials.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="p-6 rounded-2xl bg-slate-50 border border-slate-200/80 hover:shadow-md transition-shadow">
              <div className="w-10 h-10 rounded-xl bg-indigo-100 text-indigo-600 flex items-center justify-center mb-4">
                <FileText className="w-5 h-5" />
              </div>
              <h3 className="text-base font-bold text-slate-900 mb-1">1. Ingest & Parse</h3>
              <p className="text-xs text-slate-600 leading-relaxed">
                PyMuPDF and office parsers extract text while preserving exact page numbers, slide titles, and sections.
              </p>
            </div>

            <div className="p-6 rounded-2xl bg-slate-50 border border-slate-200/80 hover:shadow-md transition-shadow">
              <div className="w-10 h-10 rounded-xl bg-purple-100 text-purple-600 flex items-center justify-center mb-4">
                <Layers className="w-5 h-5" />
              </div>
              <h3 className="text-base font-bold text-slate-900 mb-1">2. Semantic Chunking</h3>
              <p className="text-xs text-slate-600 leading-relaxed">
                Documents are split into 600-token passages with 100-token overlap, preventing lost context at boundaries.
              </p>
            </div>

            <div className="p-6 rounded-2xl bg-slate-50 border border-slate-200/80 hover:shadow-md transition-shadow">
              <div className="w-10 h-10 rounded-xl bg-blue-100 text-blue-600 flex items-center justify-center mb-4">
                <Database className="w-5 h-5" />
              </div>
              <h3 className="text-base font-bold text-slate-900 mb-1">3. Vector Search</h3>
              <p className="text-xs text-slate-600 leading-relaxed">
                1536-dimensional embeddings in pgvector match conceptual queries even when exact keywords differ.
              </p>
            </div>

            <div className="p-6 rounded-2xl bg-slate-50 border border-slate-200/80 hover:shadow-md transition-shadow">
              <div className="w-10 h-10 rounded-xl bg-emerald-100 text-emerald-600 flex items-center justify-center mb-4">
                <FileCheck2 className="w-5 h-5" />
              </div>
              <h3 className="text-base font-bold text-slate-900 mb-1">4. Grounded Citations</h3>
              <p className="text-xs text-slate-600 leading-relaxed">
                Answers cite sources like [1] or [2]. Click any citation to open the exact supporting passage immediately.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Security & Privacy Banner */}
      <section className="py-16 max-w-7xl mx-auto px-6">
        <div className="p-8 sm:p-12 rounded-3xl bg-navy-900 text-white relative overflow-hidden">
          <div className="max-w-2xl relative z-10">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-slate-800 text-brand-300 text-xs font-medium mb-4">
              <Lock className="w-3.5 h-3.5 text-brand-400" />
              <span>Enterprise Privacy Standard</span>
            </div>
            <h2 className="text-2xl sm:text-3xl font-bold tracking-tight">
              Your Personal Data Stays Private and Isolated
            </h2>
            <p className="mt-3 text-sm text-slate-300 leading-relaxed">
              Every query enforces strict user isolation filters. Retrieved document context is treated as untrusted data to protect against prompt injection. Passwords use Argon2id hashing, and sessions use secure HttpOnly tokens.
            </p>
            <div className="mt-6 flex items-center gap-6 text-xs text-slate-400 font-medium">
              <span className="flex items-center gap-1.5">
                <Shield className="w-4 h-4 text-emerald-400" /> Multi-Tenant Isolation
              </span>
              <span className="flex items-center gap-1.5">
                <Shield className="w-4 h-4 text-emerald-400" /> Zero Document Bleed
              </span>
              <span className="flex items-center gap-1.5">
                <Shield className="w-4 h-4 text-emerald-400" /> Full Deletion Rights
              </span>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 bg-white border-t border-slate-200 text-center text-xs text-slate-500">
        <p>© 2026 AI Knowledge Assistant. Built with React, TypeScript, FastAPI, PostgreSQL & pgvector.</p>
      </footer>
    </div>
  );
};
