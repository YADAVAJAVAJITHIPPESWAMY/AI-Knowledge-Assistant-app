import React, { useState, useRef, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useLocation } from 'react-router-dom';
import {
  Send,
  Plus,
  Trash2,
  FileText,
  Sparkles,
  Bot,
  User as UserIcon,
  Copy,
  Check,
  Filter,
  ExternalLink,
  MessageSquare
} from 'lucide-react';
import { api } from '../services/apiClient';
import { Document, Conversation, Message, CitationItem, ChatResponse } from '../types';
import { CitationModal } from '../components/common/CitationModal';
import { formatDate } from '../utils/cn';

export const ChatPage: React.FC = () => {
  const queryClient = useQueryClient();
  const location = useLocation();

  const [activeConvId, setActiveConvId] = useState<string | null>(
    (location.state as any)?.conversationId || null
  );
  const [selectedDocIds, setSelectedDocIds] = useState<string[]>([]);
  const [inputQuery, setInputQuery] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [copiedId, setCopiedId] = useState<string | null>(null);

  // Citation inspection modal state
  const [activeCitation, setActiveCitation] = useState<CitationItem | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  // 1. Fetch user's indexed documents
  const { data: documents = [] } = useQuery<Document[]>({
    queryKey: ['documents'],
    queryFn: () => api.get<Document[]>('/api/documents'),
  });
  const indexedDocs = documents.filter((d) => d.processing_status === 'indexed');

  // 2. Fetch conversations
  const { data: conversations = [], refetch: refetchConvs } = useQuery<Conversation[]>({
    queryKey: ['conversations'],
    queryFn: () => api.get<Conversation[]>('/api/conversations'),
  });

  // 3. Fetch active conversation messages
  const { data: messages = [], refetch: refetchMessages } = useQuery<Message[]>({
    queryKey: ['messages', activeConvId],
    queryFn: () =>
      activeConvId ? api.get<Message[]>(`/api/conversations/${activeConvId}/messages`) : Promise.resolve([]),
    enabled: !!activeConvId,
  });

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isStreaming]);

  // Handle New Chat
  const handleNewChat = () => {
    setActiveConvId(null);
    setInputQuery('');
  };

  // Delete Conversation
  const deleteConvMutation = useMutation({
    mutationFn: (id: string) => api.delete(`/api/conversations/${id}`),
    onSuccess: () => {
      refetchConvs();
      if (activeConvId) setActiveConvId(null);
    },
  });

  // Submit Query
  const handleSend = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    const query = inputQuery.trim();
    if (!query || isStreaming) return;

    setInputQuery('');
    setIsStreaming(true);

    try {
      const response = await api.post<ChatResponse>('/api/chat/query', {
        query,
        conversation_id: activeConvId,
        document_ids: selectedDocIds.length > 0 ? selectedDocIds : null,
      });

      if (!activeConvId) {
        setActiveConvId(response.conversation_id);
        refetchConvs();
      }

      await refetchMessages();
    } catch (err: any) {
      alert(`Chat query failed: ${err.message}`);
    } finally {
      setIsStreaming(false);
    }
  };

  const handleCopy = (id: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const suggestedQuestions = [
    'What are the core concepts covered in my uploaded materials?',
    'Summarize the system design architecture and scalability trade-offs.',
    'What did I learn about database normalization?',
    'Compare the primary themes across these documents.',
  ];

  return (
    <div className="flex h-[calc(100vh-8rem)] rounded-3xl overflow-hidden bg-white border border-slate-200 shadow-sm animate-in fade-in">
      {/* Left Chat History & Filter Sidebar */}
      <div className="hidden md:flex flex-col w-72 bg-slate-50 border-r border-slate-200">
        {/* New Chat Button */}
        <div className="p-3 border-b border-slate-200">
          <button
            onClick={handleNewChat}
            className="w-full flex items-center justify-center gap-2 py-2 px-3 rounded-xl bg-white hover:bg-slate-100 text-slate-800 text-xs font-bold border border-slate-200 shadow-sm transition-all"
          >
            <Plus className="w-4 h-4 text-brand-600" />
            <span>New Chat Session</span>
          </button>
        </div>

        {/* Document Filter Selector */}
        <div className="p-3 border-b border-slate-200">
          <label className="text-[11px] font-bold text-slate-500 uppercase tracking-wider block mb-1.5">
            Grounded Scope
          </label>
          <select
            className="w-full px-2.5 py-1.5 text-xs bg-white border border-slate-200 rounded-lg text-slate-700 focus:outline-none focus:ring-2 focus:ring-brand-500/20"
            value={selectedDocIds[0] || 'all'}
            onChange={(e) => {
              const val = e.target.value;
              setSelectedDocIds(val === 'all' ? [] : [val]);
            }}
          >
            <option value="all">🔍 Search All Documents ({indexedDocs.length})</option>
            {indexedDocs.map((d) => (
              <option key={d.id} value={d.id}>
                📄 {d.filename}
              </option>
            ))}
          </select>
        </div>

        {/* Conversation List */}
        <div className="flex-1 overflow-y-auto p-2 space-y-1">
          <div className="px-2 py-1 text-[10px] font-bold text-slate-400 uppercase tracking-wider">
            Recent Conversations
          </div>
          {conversations.length === 0 ? (
            <p className="px-3 py-2 text-xs text-slate-400 italic">No conversations yet.</p>
          ) : (
            conversations.map((c) => (
              <div
                key={c.id}
                onClick={() => setActiveConvId(c.id)}
                className={`group flex items-center justify-between p-2 rounded-xl text-xs cursor-pointer transition-colors ${
                  activeConvId === c.id
                    ? 'bg-brand-50 text-brand-900 font-semibold border border-brand-200'
                    : 'text-slate-600 hover:bg-slate-200/60'
                }`}
              >
                <div className="flex items-center gap-2 overflow-hidden">
                  <MessageSquare className="w-3.5 h-3.5 shrink-0 text-slate-400" />
                  <span className="truncate">{c.title}</span>
                </div>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    if (window.confirm('Delete this conversation?')) {
                      deleteConvMutation.mutate(c.id);
                    }
                  }}
                  className="opacity-0 group-hover:opacity-100 p-1 text-slate-400 hover:text-red-500 transition-opacity"
                >
                  <Trash2 className="w-3 h-3" />
                </button>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Main Chat Conversation View */}
      <div className="flex-1 flex flex-col h-full bg-[#FCFDFE]">
        {/* Messages Feed */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-6">
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-center max-w-lg mx-auto py-12">
              <div className="w-14 h-14 rounded-2xl bg-gradient-to-tr from-brand-600 to-brand-purple text-white flex items-center justify-center mb-4 shadow-xl shadow-brand-500/20">
                <Sparkles className="w-7 h-7" />
              </div>
              <h2 className="text-xl font-bold text-slate-900 tracking-tight">
                Ask Questions Grounded in Your Documents
              </h2>
              <p className="text-xs text-slate-500 mt-2 leading-relaxed">
                Every answer synthesizes retrieved excerpts from your indexed PDF, Word, and PowerPoint files with clickable citations.
              </p>

              {/* Suggested Questions */}
              <div className="mt-6 w-full space-y-2">
                <p className="text-[11px] font-bold text-slate-400 uppercase tracking-wider text-left">
                  Suggested Prompts
                </p>
                <div className="grid grid-cols-1 gap-2">
                  {suggestedQuestions.map((q, idx) => (
                    <button
                      key={idx}
                      onClick={() => {
                        setInputQuery(q);
                      }}
                      className="text-left p-3 rounded-xl bg-white hover:bg-brand-50/50 border border-slate-200 text-xs text-slate-700 transition-colors shadow-sm hover:border-brand-300 font-medium"
                    >
                      💡 {q}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex gap-3 max-w-3xl ${
                  msg.role === 'user' ? 'ml-auto justify-end' : 'mr-auto justify-start'
                }`}
              >
                {msg.role === 'assistant' && (
                  <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-brand-600 to-brand-purple text-white flex items-center justify-center shrink-0 shadow-sm mt-0.5">
                    <Bot className="w-4 h-4" />
                  </div>
                )}

                <div
                  className={`relative p-4 rounded-2xl text-xs sm:text-sm leading-relaxed max-w-2xl ${
                    msg.role === 'user'
                      ? 'bg-gradient-to-r from-brand-600 to-brand-purple text-white font-medium rounded-br-xs shadow-md shadow-brand-500/10'
                      : 'bg-white border border-slate-200 text-slate-800 rounded-bl-xs shadow-sm'
                  }`}
                >
                  {/* Message content */}
                  <div className="whitespace-pre-wrap font-sans">{msg.content}</div>

                  {/* Verifiable Citation Badges */}
                  {msg.role === 'assistant' && msg.citations && msg.citations.length > 0 && (
                    <div className="mt-3 pt-3 border-t border-slate-100 flex flex-wrap items-center gap-1.5">
                      <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mr-1">
                        Sources:
                      </span>
                      {msg.citations.map((c, i) => (
                        <button
                          key={i}
                          onClick={() => setActiveCitation(c)}
                          className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-brand-50 hover:bg-brand-100 text-brand-700 border border-brand-200 text-[11px] font-semibold transition-colors cursor-pointer"
                        >
                          <span>[{c.citation_number}]</span>
                          <span className="truncate max-w-[120px]">{c.document_name}</span>
                          {c.page_number && <span className="text-[10px] text-slate-400">p.{c.page_number}</span>}
                          {c.slide_number && <span className="text-[10px] text-slate-400">s.{c.slide_number}</span>}
                        </button>
                      ))}
                    </div>
                  )}

                  {/* Copy Button */}
                  {msg.role === 'assistant' && (
                    <button
                      onClick={() => handleCopy(msg.id, msg.content)}
                      className="absolute top-2 right-2 p-1 text-slate-400 hover:text-slate-600 rounded"
                      title="Copy response"
                    >
                      {copiedId === msg.id ? <Check className="w-3.5 h-3.5 text-emerald-500" /> : <Copy className="w-3.5 h-3.5" />}
                    </button>
                  )}
                </div>

                {msg.role === 'user' && (
                  <div className="w-8 h-8 rounded-xl bg-slate-800 text-white flex items-center justify-center shrink-0 shadow-sm mt-0.5">
                    <UserIcon className="w-4 h-4" />
                  </div>
                )}
              </div>
            ))
          )}

          {isStreaming && (
            <div className="flex gap-3 max-w-2xl mr-auto">
              <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-brand-600 to-brand-purple text-white flex items-center justify-center shrink-0 animate-pulse">
                <Bot className="w-4 h-4" />
              </div>
              <div className="p-4 rounded-2xl bg-white border border-slate-200 text-slate-500 text-xs flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-brand-500 animate-bounce" />
                <div className="w-2 h-2 rounded-full bg-brand-500 animate-bounce delay-100" />
                <div className="w-2 h-2 rounded-full bg-brand-500 animate-bounce delay-200" />
                <span>Searching vector database and generating grounded answer...</span>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Chat Input Bar */}
        <div className="p-4 bg-white border-t border-slate-200">
          <form onSubmit={handleSend} className="relative flex items-center">
            <textarea
              rows={1}
              value={inputQuery}
              onChange={(e) => setInputQuery(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSend();
                }
              }}
              placeholder="Ask a question about your uploaded documents... (Shift+Enter for newline)"
              className="w-full pl-4 pr-12 py-3 bg-slate-50 border border-slate-200 rounded-2xl text-xs sm:text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 resize-none max-h-32 transition-colors"
            />
            <button
              type="submit"
              disabled={!inputQuery.trim() || isStreaming}
              className="absolute right-2.5 p-2 rounded-xl bg-gradient-to-r from-brand-600 to-brand-purple hover:from-brand-700 hover:to-brand-violet text-white shadow-sm disabled:opacity-40 transition-all cursor-pointer"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>
          <div className="mt-2 text-center text-[10px] text-slate-400">
            Answers are grounded in your private documents. Citations are verified against exact passages.
          </div>
        </div>
      </div>

      {/* Citation Inspector Modal */}
      <CitationModal
        citation={activeCitation}
        onClose={() => setActiveCitation(null)}
      />
    </div>
  );
};
