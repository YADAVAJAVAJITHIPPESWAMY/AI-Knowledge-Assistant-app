import React from 'react';
import { X, FileText, ExternalLink, Bookmark } from 'lucide-react';
import { CitationItem } from '../../types';

interface CitationModalProps {
  citation: CitationItem | null;
  onClose: () => void;
  onNavigateToDocument?: (documentId: string) => void;
}

export const CitationModal: React.FC<CitationModalProps> = ({
  citation,
  onClose,
  onNavigateToDocument
}) => {
  if (!citation) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-navy-900/60 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="relative w-full max-w-lg bg-white rounded-2xl shadow-2xl border border-slate-200 overflow-hidden">
        {/* Modal Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100 bg-slate-50/60">
          <div className="flex items-center gap-2.5">
            <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-brand-100 text-brand-700">
              <FileText className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                <span>Citation [{citation.citation_number}]</span>
                <span className="text-[11px] font-normal px-2 py-0.5 rounded-full bg-brand-50 text-brand-700 border border-brand-200">
                  {Math.round(citation.similarity_score * 100)}% match
                </span>
              </h3>
              <p className="text-xs text-slate-500 truncate max-w-[280px]">
                {citation.document_name}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 space-y-4">
          {/* Location Tags */}
          <div className="flex flex-wrap items-center gap-2 text-xs">
            {citation.page_number && (
              <span className="px-2.5 py-1 font-semibold rounded-md bg-slate-100 text-slate-700">
                📄 Page {citation.page_number}
              </span>
            )}
            {citation.slide_number && (
              <span className="px-2.5 py-1 font-semibold rounded-md bg-amber-50 text-amber-800 border border-amber-200">
                📊 Slide {citation.slide_number}
              </span>
            )}
            {citation.section_title && (
              <span className="px-2.5 py-1 font-medium rounded-md bg-indigo-50 text-indigo-700 border border-indigo-100">
                📌 {citation.section_title}
              </span>
            )}
          </div>

          {/* Extracted Excerpt */}
          <div>
            <label className="text-xs font-semibold text-slate-500 uppercase tracking-wider block mb-1.5">
              Source Excerpt
            </label>
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 text-slate-800 text-sm leading-relaxed max-h-60 overflow-y-auto font-mono whitespace-pre-wrap">
              "{citation.excerpt}"
            </div>
          </div>

          <p className="text-[11px] text-slate-400 italic">
            This verified passage was retrieved from your uploaded document using pgvector semantic search.
          </p>
        </div>

        {/* Modal Footer */}
        <div className="flex items-center justify-end gap-2 px-6 py-3.5 bg-slate-50 border-t border-slate-100">
          <button
            onClick={onClose}
            className="px-4 py-2 text-xs font-medium text-slate-600 hover:text-slate-800 hover:bg-slate-200/60 rounded-xl transition-colors"
          >
            Close
          </button>
          {onNavigateToDocument && (
            <button
              onClick={() => {
                onClose();
                onNavigateToDocument(citation.document_id);
              }}
              className="flex items-center gap-1.5 px-4 py-2 text-xs font-semibold text-white bg-brand-600 hover:bg-brand-700 rounded-xl shadow-sm transition-colors"
            >
              <span>View Document</span>
              <ExternalLink className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
