import React, { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import {
  Lightbulb,
  FileText,
  Layers,
  Sparkles,
  BookOpen,
  HelpCircle,
  CheckCircle,
  XCircle,
  ArrowRight,
  RefreshCw,
  GitCompare
} from 'lucide-react';
import { api } from '../services/apiClient';
import { Document, InsightResult, QuizResponse, QuizQuestion } from '../types';

export const InsightsPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'summarize' | 'compare' | 'concepts' | 'quiz'>('summarize');

  // Single doc selection for summarize, concepts, quiz
  const [selectedDocId, setSelectedDocId] = useState<string>('');

  // Multi doc selection for compare
  const [compareDocIds, setCompareDocIds] = useState<string[]>([]);

  // Results state
  const [insightData, setInsightData] = useState<InsightResult | null>(null);
  const [quizData, setQuizData] = useState<QuizResponse | null>(null);
  const [quizAnswers, setQuizAnswers] = useState<Record<number, number>>({});
  const [quizSubmitted, setQuizSubmitted] = useState<boolean>(false);

  // Fetch indexed documents
  const { data: documents = [] } = useQuery<Document[]>({
    queryKey: ['documents'],
    queryFn: () => api.get<Document[]>('/api/documents'),
  });
  const indexedDocs = documents.filter((d) => d.processing_status === 'indexed');

  // Set default selected document once loaded
  React.useEffect(() => {
    if (indexedDocs.length > 0 && !selectedDocId) {
      setSelectedDocId(indexedDocs[0].id);
    }
  }, [indexedDocs, selectedDocId]);

  // Summarize Mutation
  const summarizeMutation = useMutation({
    mutationFn: (docId: string) =>
      api.post<InsightResult>('/api/insights/summarize', { document_id: docId }),
    onSuccess: (data) => setInsightData(data),
  });

  // Compare Mutation
  const compareMutation = useMutation({
    mutationFn: (docIds: string[]) =>
      api.post<InsightResult>('/api/insights/compare', { document_ids: docIds }),
    onSuccess: (data) => setInsightData(data),
  });

  // Concepts Mutation
  const conceptsMutation = useMutation({
    mutationFn: (docId: string) =>
      api.post<InsightResult>('/api/insights/key-concepts', { document_id: docId }),
    onSuccess: (data) => setInsightData(data),
  });

  // Quiz Mutation
  const quizMutation = useMutation({
    mutationFn: (docId: string) =>
      api.post<QuizResponse>('/api/insights/quiz', { document_id: docId }),
    onSuccess: (data) => {
      setQuizData(data);
      setQuizAnswers({});
      setQuizSubmitted(false);
    },
  });

  const handleRunInsight = () => {
    setInsightData(null);
    setQuizData(null);

    if (activeTab === 'summarize') {
      summarizeMutation.mutate(selectedDocId);
    } else if (activeTab === 'compare') {
      if (compareDocIds.length < 2) {
        alert('Please select at least 2 documents to compare.');
        return;
      }
      compareMutation.mutate(compareDocIds);
    } else if (activeTab === 'concepts') {
      conceptsMutation.mutate(selectedDocId);
    } else if (activeTab === 'quiz') {
      quizMutation.mutate(selectedDocId);
    }
  };

  const isPending =
    summarizeMutation.isPending ||
    compareMutation.isPending ||
    conceptsMutation.isPending ||
    quizMutation.isPending;

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">Knowledge Insights</h1>
        <p className="text-xs sm:text-sm text-slate-500 mt-1">
          Synthesize learning materials into executive summaries, cross-document comparisons, core concepts, and interactive revision quizzes.
        </p>
      </div>

      {/* Tabs */}
      <div className="flex flex-wrap items-center gap-2 p-1.5 bg-slate-200/60 rounded-2xl w-fit">
        <button
          onClick={() => {
            setActiveTab('summarize');
            setInsightData(null);
          }}
          className={`flex items-center gap-2 px-4 py-2 text-xs font-bold rounded-xl transition-all ${
            activeTab === 'summarize'
              ? 'bg-white text-brand-700 shadow-sm'
              : 'text-slate-600 hover:text-slate-900'
          }`}
        >
          <FileText className="w-3.5 h-3.5" />
          <span>Document Summarizer</span>
        </button>

        <button
          onClick={() => {
            setActiveTab('compare');
            setInsightData(null);
          }}
          className={`flex items-center gap-2 px-4 py-2 text-xs font-bold rounded-xl transition-all ${
            activeTab === 'compare'
              ? 'bg-white text-brand-700 shadow-sm'
              : 'text-slate-600 hover:text-slate-900'
          }`}
        >
          <GitCompare className="w-3.5 h-3.5" />
          <span>Cross-Document Comparison</span>
        </button>

        <button
          onClick={() => {
            setActiveTab('concepts');
            setInsightData(null);
          }}
          className={`flex items-center gap-2 px-4 py-2 text-xs font-bold rounded-xl transition-all ${
            activeTab === 'concepts'
              ? 'bg-white text-brand-700 shadow-sm'
              : 'text-slate-600 hover:text-slate-900'
          }`}
        >
          <Lightbulb className="w-3.5 h-3.5" />
          <span>Key Concepts</span>
        </button>

        <button
          onClick={() => {
            setActiveTab('quiz');
            setInsightData(null);
          }}
          className={`flex items-center gap-2 px-4 py-2 text-xs font-bold rounded-xl transition-all ${
            activeTab === 'quiz'
              ? 'bg-white text-brand-700 shadow-sm'
              : 'text-slate-600 hover:text-slate-900'
          }`}
        >
          <HelpCircle className="w-3.5 h-3.5" />
          <span>Revision Quiz</span>
        </button>
      </div>

      {/* Controls Bar */}
      <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-sm flex flex-col sm:flex-row items-center justify-between gap-4">
        {activeTab !== 'compare' ? (
          <div className="w-full sm:w-auto flex-1">
            <label className="text-xs font-bold text-slate-500 uppercase tracking-wider block mb-1.5">
              Select Target Document
            </label>
            <select
              value={selectedDocId}
              onChange={(e) => setSelectedDocId(e.target.value)}
              className="w-full sm:max-w-md px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-800 focus:outline-none focus:ring-2 focus:ring-brand-500/20"
            >
              {indexedDocs.length === 0 ? (
                <option value="">No indexed documents available</option>
              ) : (
                indexedDocs.map((doc) => (
                  <option key={doc.id} value={doc.id}>
                    📄 {doc.filename} ({doc.page_count} pages)
                  </option>
                ))
              )}
            </select>
          </div>
        ) : (
          <div className="w-full flex-1">
            <label className="text-xs font-bold text-slate-500 uppercase tracking-wider block mb-1.5">
              Select 2 to 5 Documents to Compare ({compareDocIds.length} selected)
            </label>
            <div className="flex flex-wrap gap-2">
              {indexedDocs.map((doc) => {
                const isSelected = compareDocIds.includes(doc.id);
                return (
                  <button
                    key={doc.id}
                    onClick={() => {
                      if (isSelected) {
                        setCompareDocIds(compareDocIds.filter((id) => id !== doc.id));
                      } else {
                        if (compareDocIds.length >= 5) {
                          alert('You can select up to 5 documents at a time.');
                          return;
                        }
                        setCompareDocIds([...compareDocIds, doc.id]);
                      }
                    }}
                    className={`px-3 py-1.5 rounded-xl text-xs font-medium border transition-all ${
                      isSelected
                        ? 'bg-brand-50 border-brand-500 text-brand-700 font-semibold shadow-sm'
                        : 'bg-slate-50 border-slate-200 text-slate-600 hover:bg-slate-100'
                    }`}
                  >
                    📄 {doc.filename}
                  </button>
                );
              })}
            </div>
          </div>
        )}

        <button
          onClick={handleRunInsight}
          disabled={isPending || indexedDocs.length === 0}
          className="w-full sm:w-auto flex items-center justify-center gap-2 px-6 py-2.5 rounded-xl bg-gradient-to-r from-brand-600 to-brand-purple hover:from-brand-700 hover:to-brand-violet text-white text-xs font-bold shadow-md shadow-brand-500/20 disabled:opacity-50 transition-all shrink-0"
        >
          {isPending ? (
            <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
          ) : (
            <Sparkles className="w-4 h-4" />
          )}
          <span>Generate Insights</span>
        </button>
      </div>

      {/* Results Section */}
      {isPending && (
        <div className="p-12 text-center bg-white rounded-2xl border border-slate-200">
          <div className="w-8 h-8 border-4 border-brand-200 border-t-brand-600 rounded-full animate-spin mx-auto mb-3" />
          <p className="text-xs font-semibold text-slate-700">Synthesizing document knowledge...</p>
          <p className="text-[11px] text-slate-400 mt-1">Analyzing passages and extracting key concepts.</p>
        </div>
      )}

      {/* Insight Text Output */}
      {insightData && !isPending && (
        <div className="p-6 sm:p-8 rounded-2xl bg-white border border-slate-200 shadow-sm space-y-4 animate-in fade-in">
          <div className="flex items-center gap-2 pb-4 border-b border-slate-100">
            <Sparkles className="w-5 h-5 text-brand-600" />
            <h2 className="text-base font-bold text-slate-900">{insightData.title}</h2>
          </div>
          <div className="prose prose-sm max-w-none text-slate-800 text-xs sm:text-sm leading-relaxed whitespace-pre-wrap font-sans">
            {insightData.result}
          </div>
        </div>
      )}

      {/* Quiz Output */}
      {quizData && !isPending && (
        <div className="p-6 sm:p-8 rounded-2xl bg-white border border-slate-200 shadow-sm space-y-6 animate-in fade-in">
          <div className="flex items-center justify-between pb-4 border-b border-slate-100">
            <div>
              <h2 className="text-base font-bold text-slate-900">
                Revision Assessment: {quizData.document_name}
              </h2>
              <p className="text-xs text-slate-500">Test your mastery of the concepts extracted from this document.</p>
            </div>
            {quizSubmitted && (
              <span className="px-3 py-1 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200 text-xs font-bold">
                Score: {Object.entries(quizAnswers).filter(([qIdx, ans]) => quizData.quiz[Number(qIdx)].correct_answer_index === ans).length} / {quizData.quiz.length}
              </span>
            )}
          </div>

          <div className="space-y-6">
            {quizData.quiz.map((q, qIndex) => (
              <div key={qIndex} className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-3">
                <p className="text-xs sm:text-sm font-semibold text-slate-900">
                  {qIndex + 1}. {q.question}
                </p>

                <div className="space-y-2">
                  {q.options.map((opt, optIndex) => {
                    const isSelected = quizAnswers[qIndex] === optIndex;
                    const isCorrect = q.correct_answer_index === optIndex;
                    let optStyle = 'bg-white border-slate-200 text-slate-700 hover:bg-slate-100';

                    if (quizSubmitted) {
                      if (isCorrect) {
                        optStyle = 'bg-emerald-50 border-emerald-500 text-emerald-800 font-semibold';
                      } else if (isSelected && !isCorrect) {
                        optStyle = 'bg-red-50 border-red-500 text-red-800 font-semibold';
                      }
                    } else if (isSelected) {
                      optStyle = 'bg-brand-50 border-brand-500 text-brand-800 font-semibold shadow-sm';
                    }

                    return (
                      <button
                        key={optIndex}
                        disabled={quizSubmitted}
                        onClick={() => setQuizAnswers({ ...quizAnswers, [qIndex]: optIndex })}
                        className={`w-full text-left p-3 rounded-xl border text-xs transition-all flex items-center justify-between ${optStyle}`}
                      >
                        <span>{opt}</span>
                        {quizSubmitted && isCorrect && <CheckCircle className="w-4 h-4 text-emerald-600" />}
                        {quizSubmitted && isSelected && !isCorrect && <XCircle className="w-4 h-4 text-red-600" />}
                      </button>
                    );
                  })}
                </div>

                {quizSubmitted && (
                  <div className="p-3 rounded-lg bg-indigo-50/60 border border-indigo-100 text-[11px] text-indigo-900 leading-relaxed">
                    <span className="font-bold">Explanation:</span> {q.explanation}
                  </div>
                )}
              </div>
            ))}
          </div>

          <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-100">
            {!quizSubmitted ? (
              <button
                onClick={() => setQuizSubmitted(true)}
                className="px-6 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-700 text-white text-xs font-bold shadow-md transition-colors"
              >
                Submit Answers
              </button>
            ) : (
              <button
                onClick={() => {
                  setQuizAnswers({});
                  setQuizSubmitted(false);
                }}
                className="px-6 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-white text-xs font-bold transition-colors"
              >
                Retake Quiz
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
