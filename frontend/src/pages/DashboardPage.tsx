import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import {
  FileText,
  MessageSquare,
  UploadCloud,
  CheckCircle2,
  Clock,
  Sparkles,
  ArrowRight,
  Database,
  Layers,
  AlertCircle
} from 'lucide-react';
import { api } from '../services/apiClient';
import { Document, Conversation } from '../types';
import { useAuth } from '../contexts/AuthContext';
import { formatBytes, formatDate } from '../utils/cn';

export const DashboardPage: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);

  // Fetch documents
  const { data: documents = [], refetch: refetchDocs } = useQuery<Document[]>({
    queryKey: ['documents'],
    queryFn: () => api.get<Document[]>('/api/documents'),
    refetchInterval: 5000, // auto-refresh for processing status
  });

  // Fetch conversations
  const { data: conversations = [] } = useQuery<Conversation[]>({
    queryKey: ['conversations'],
    queryFn: () => api.get<Conversation[]>('/api/conversations'),
  });

  // Metrics calculations
  const totalDocs = documents.length;
  const indexedDocs = documents.filter((d) => d.processing_status === 'indexed').length;
  const totalPages = documents.reduce((acc, curr) => acc + (curr.page_count || 0), 0);
  const totalConversations = conversations.length;

  const handleQuickUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    setIsUploading(true);
    setUploadError(null);

    const formData = new FormData();
    formData.append('file', files[0]);

    try {
      await api.post('/api/documents/upload', formData);
      refetchDocs();
    } catch (err: any) {
      setUploadError(err.message || 'Upload failed');
    } finally {
      setIsUploading(false);
      e.target.value = '';
    }
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      {/* Welcome Banner */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-navy-900 via-navy-800 to-slate-900 p-8 text-white shadow-xl">
        <div className="relative z-10 max-w-2xl">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-brand-500/20 text-brand-300 border border-brand-500/30 text-xs font-semibold mb-3">
            <Sparkles className="w-3.5 h-3.5" />
            <span>AI Knowledge Assistant 2.0</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight">
            Welcome back, {user?.name || 'Scholar'}!
          </h1>
          <p className="mt-2 text-sm text-slate-300 leading-relaxed">
            Your personal RAG knowledge assistant has indexed{' '}
            <span className="font-semibold text-brand-300">{indexedDocs} documents</span> across{' '}
            <span className="font-semibold text-brand-300">{totalPages} pages & slides</span>. Ask questions and get answers grounded strictly in your verified materials.
          </p>

          <div className="mt-6 flex flex-wrap items-center gap-3">
            <Link
              to="/chat"
              className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-brand-600 to-brand-purple text-white text-xs font-bold shadow-lg shadow-brand-500/25 hover:from-brand-700 hover:to-brand-violet transition-all"
            >
              <MessageSquare className="w-4 h-4" />
              <span>Open AI Chat</span>
            </Link>
            <Link
              to="/documents"
              className="px-5 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition-colors"
            >
              Manage Documents
            </Link>
          </div>
        </div>

        {/* Ambient background decoration */}
        <div className="absolute right-0 top-0 bottom-0 w-96 bg-gradient-to-l from-brand-500/10 via-brand-purple/10 to-transparent pointer-events-none" />
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-sm flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Total Documents</p>
            <h3 className="text-2xl font-bold text-slate-900 mt-1">{totalDocs}</h3>
            <span className="text-[11px] text-slate-400 mt-0.5 block">{indexedDocs} fully indexed</span>
          </div>
          <div className="flex items-center justify-center w-12 h-12 rounded-xl bg-indigo-50 text-indigo-600">
            <FileText className="w-6 h-6" />
          </div>
        </div>

        <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-sm flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Indexed Pages</p>
            <h3 className="text-2xl font-bold text-slate-900 mt-1">{totalPages}</h3>
            <span className="text-[11px] text-emerald-600 font-medium mt-0.5 block">Searchable Chunks</span>
          </div>
          <div className="flex items-center justify-center w-12 h-12 rounded-xl bg-purple-50 text-brand-purple">
            <Layers className="w-6 h-6" />
          </div>
        </div>

        <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-sm flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Conversations</p>
            <h3 className="text-2xl font-bold text-slate-900 mt-1">{totalConversations}</h3>
            <span className="text-[11px] text-slate-400 mt-0.5 block">Persistent sessions</span>
          </div>
          <div className="flex items-center justify-center w-12 h-12 rounded-xl bg-blue-50 text-blue-600">
            <MessageSquare className="w-6 h-6" />
          </div>
        </div>

        <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-sm flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Vector Store</p>
            <h3 className="text-2xl font-bold text-slate-900 mt-1">1536d</h3>
            <span className="text-[11px] text-slate-400 mt-0.5 block">pgvector Cosine Index</span>
          </div>
          <div className="flex items-center justify-center w-12 h-12 rounded-xl bg-emerald-50 text-emerald-600">
            <Database className="w-6 h-6" />
          </div>
        </div>
      </div>

      {/* Main Dashboard Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Recent Documents Table (2 columns on wide screen) */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-bold text-slate-900">Recently Uploaded Documents</h2>
            <Link to="/documents" className="text-xs font-semibold text-brand-600 hover:text-brand-700 flex items-center gap-1">
              <span>View All</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
            {documents.length === 0 ? (
              <div className="p-8 text-center">
                <FileText className="w-10 h-10 text-slate-300 mx-auto mb-2" />
                <p className="text-sm font-semibold text-slate-700">No documents uploaded yet</p>
                <p className="text-xs text-slate-400 mt-1">Upload PDF, Word, or Markdown files to begin asking questions.</p>
              </div>
            ) : (
              <div className="divide-y divide-slate-100">
                {documents.slice(0, 5).map((doc) => (
                  <div key={doc.id} className="p-4 flex items-center justify-between hover:bg-slate-50 transition-colors">
                    <div className="flex items-center gap-3">
                      <div className="flex items-center justify-center w-9 h-9 rounded-lg bg-slate-100 text-slate-600 font-bold text-xs uppercase">
                        {doc.file_type}
                      </div>
                      <div>
                        <h4 className="text-xs font-semibold text-slate-900 truncate max-w-xs sm:max-w-md">
                          {doc.filename}
                        </h4>
                        <div className="flex items-center gap-2 text-[11px] text-slate-400 mt-0.5">
                          <span>{formatBytes(doc.file_size)}</span>
                          <span>•</span>
                          <span>{formatDate(doc.created_at)}</span>
                          {doc.page_count > 0 && (
                            <>
                              <span>•</span>
                              <span>{doc.page_count} pages/slides</span>
                            </>
                          )}
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center gap-2">
                      {doc.processing_status === 'indexed' && (
                        <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-emerald-50 text-emerald-700 text-[11px] font-semibold border border-emerald-200">
                          <CheckCircle2 className="w-3 h-3" /> Indexed
                        </span>
                      )}
                      {doc.processing_status === 'processing' && (
                        <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-blue-50 text-blue-700 text-[11px] font-semibold border border-blue-200">
                          <div className="w-2.5 h-2.5 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
                          Processing
                        </span>
                      )}
                      {doc.processing_status === 'uploaded' && (
                        <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-amber-50 text-amber-700 text-[11px] font-semibold border border-amber-200">
                          <Clock className="w-3 h-3" /> Queued
                        </span>
                      )}
                      {doc.processing_status === 'failed' && (
                        <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-red-50 text-red-700 text-[11px] font-semibold border border-red-200">
                          <AlertCircle className="w-3 h-3" /> Failed
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Quick Upload & Recent Chats */}
        <div className="space-y-6">
          {/* Quick Upload Card */}
          <div className="p-6 rounded-2xl bg-white border border-slate-200 shadow-sm">
            <h3 className="text-sm font-bold text-slate-900 mb-1">Quick Document Upload</h3>
            <p className="text-xs text-slate-500 mb-4">
              Add a new PDF, DOCX, or Markdown file to index.
            </p>

            {uploadError && (
              <div className="mb-3 p-2.5 rounded-lg bg-red-50 text-red-700 text-xs">
                {uploadError}
              </div>
            )}

            <label className="flex flex-col items-center justify-center p-6 border-2 border-dashed border-slate-200 hover:border-brand-500 rounded-xl cursor-pointer bg-slate-50 hover:bg-brand-50/20 transition-all">
              <UploadCloud className="w-8 h-8 text-brand-600 mb-2" />
              <span className="text-xs font-semibold text-slate-700">
                {isUploading ? 'Uploading & parsing...' : 'Click or drop file here'}
              </span>
              <span className="text-[10px] text-slate-400 mt-1">PDF, DOCX, PPTX, TXT up to 20MB</span>
              <input
                type="file"
                className="hidden"
                disabled={isUploading}
                accept=".pdf,.docx,.doc,.pptx,.ppt,.txt,.md"
                onChange={handleQuickUpload}
              />
            </label>
          </div>

          {/* Recent Chat History */}
          <div className="p-6 rounded-2xl bg-white border border-slate-200 shadow-sm">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-bold text-slate-900">Recent Chats</h3>
              <Link to="/chat" className="text-xs font-semibold text-brand-600 hover:text-brand-700">
                New Chat
              </Link>
            </div>

            {conversations.length === 0 ? (
              <p className="text-xs text-slate-400">No chat history yet.</p>
            ) : (
              <div className="space-y-2">
                {conversations.slice(0, 4).map((c) => (
                  <button
                    key={c.id}
                    onClick={() => navigate('/chat', { state: { conversationId: c.id } })}
                    className="w-full text-left p-2.5 rounded-xl hover:bg-slate-50 text-xs text-slate-700 flex items-center justify-between transition-colors border border-transparent hover:border-slate-200"
                  >
                    <span className="truncate max-w-[180px] font-medium">{c.title}</span>
                    <span className="text-[10px] text-slate-400">{formatDate(c.updated_at)}</span>
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
