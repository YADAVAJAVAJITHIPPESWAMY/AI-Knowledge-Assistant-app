import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  UploadCloud,
  FileText,
  Search,
  Filter,
  Trash2,
  RefreshCw,
  Eye,
  CheckCircle2,
  Clock,
  AlertCircle,
  X,
  FileCode,
  Layers
} from 'lucide-react';
import { api } from '../services/apiClient';
import { Document, DocumentContent } from '../types';
import { formatBytes, formatDate } from '../utils/cn';

export const DocumentsPage: React.FC = () => {
  const queryClient = useQueryClient();
  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState<string>('all');
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);

  // Preview document state
  const [previewDocId, setPreviewDocId] = useState<string | null>(null);

  // Fetch documents
  const { data: documents = [], isLoading } = useQuery<Document[]>({
    queryKey: ['documents', searchQuery, filterType],
    queryFn: () => {
      let url = '/api/documents';
      const params = new URLSearchParams();
      if (searchQuery.trim()) params.append('query', searchQuery.trim());
      if (filterType !== 'all') params.append('file_type', filterType);
      const qs = params.toString();
      return api.get<Document[]>(qs ? `${url}?${qs}` : url);
    },
    refetchInterval: 4000,
  });

  // Fetch document preview content
  const { data: previewContent, isLoading: isPreviewLoading } = useQuery<DocumentContent>({
    queryKey: ['documentContent', previewDocId],
    queryFn: () => api.get<DocumentContent>(`/api/documents/${previewDocId}/content`),
    enabled: !!previewDocId,
  });

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: (id: string) => api.delete(`/api/documents/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents'] });
      if (previewDocId) setPreviewDocId(null);
    },
  });

  // Reprocess mutation
  const reprocessMutation = useMutation({
    mutationFn: (id: string) => api.post(`/api/documents/${id}/reprocess`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents'] });
    },
  });

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    setIsUploading(true);
    setUploadError(null);

    // Support uploading multiple files sequentially
    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      if (file.size > 20 * 1024 * 1024) {
        setUploadError(`File ${file.name} exceeds 20MB limit.`);
        continue;
      }

      const formData = new FormData();
      formData.append('file', file);

      try {
        await api.post('/api/documents/upload', formData);
      } catch (err: any) {
        setUploadError(err.message || `Failed to upload ${file.name}`);
      }
    }

    setIsUploading(false);
    queryClient.invalidateQueries({ queryKey: ['documents'] });
    e.target.value = '';
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">Document Management</h1>
          <p className="text-xs sm:text-sm text-slate-500 mt-1">
            Upload textbooks, research notes, and slides. Extract passages and generate searchable vector embeddings.
          </p>
        </div>

        {/* Upload Button */}
        <label className="flex items-center justify-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-brand-600 to-brand-purple hover:from-brand-700 hover:to-brand-violet text-white text-xs font-bold shadow-md shadow-brand-500/20 cursor-pointer transition-all">
          <UploadCloud className="w-4 h-4" />
          <span>Upload Documents</span>
          <input
            type="file"
            multiple
            className="hidden"
            accept=".pdf,.docx,.doc,.pptx,.ppt,.txt,.md"
            onChange={handleFileUpload}
            disabled={isUploading}
          />
        </label>
      </div>

      {uploadError && (
        <div className="p-4 rounded-xl bg-red-50 border border-red-200 text-red-700 text-xs flex items-center justify-between">
          <div className="flex items-center gap-2">
            <AlertCircle className="w-4 h-4" />
            <span>{uploadError}</span>
          </div>
          <button onClick={() => setUploadError(null)} className="text-red-500 hover:text-red-700">
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Filter and Search Bar */}
      <div className="flex flex-col sm:flex-row items-center gap-3 bg-white p-3 rounded-2xl border border-slate-200 shadow-sm">
        <div className="relative flex-1 w-full">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input
            type="text"
            placeholder="Search documents by filename..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-800 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500"
          />
        </div>

        <div className="flex items-center gap-2 w-full sm:w-auto">
          <Filter className="w-4 h-4 text-slate-400 hidden sm:block" />
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="w-full sm:w-auto px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-700 focus:outline-none focus:ring-2 focus:ring-brand-500/20"
          >
            <option value="all">All Formats</option>
            <option value="pdf">PDF (.pdf)</option>
            <option value="docx">Word (.docx, .doc)</option>
            <option value="pptx">PowerPoint (.pptx, .ppt)</option>
            <option value="txt">Text (.txt)</option>
            <option value="md">Markdown (.md)</option>
          </select>
        </div>
      </div>

      {/* Documents Grid / List */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        {isLoading ? (
          <div className="p-12 text-center">
            <div className="w-8 h-8 border-4 border-brand-200 border-t-brand-600 rounded-full animate-spin mx-auto mb-3" />
            <p className="text-xs text-slate-500">Loading documents...</p>
          </div>
        ) : documents.length === 0 ? (
          <div className="p-12 text-center">
            <FileText className="w-12 h-12 text-slate-300 mx-auto mb-3" />
            <h3 className="text-sm font-bold text-slate-800">No documents found</h3>
            <p className="text-xs text-slate-500 max-w-sm mx-auto mt-1">
              Drag and drop PDF files, Word docs, PowerPoint presentations, or notes to get started.
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-200 bg-slate-50 text-[11px] font-bold text-slate-500 uppercase tracking-wider">
                  <th className="py-3 px-4">Document</th>
                  <th className="py-3 px-4">Format</th>
                  <th className="py-3 px-4">Size</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4">Pages / Segments</th>
                  <th className="py-3 px-4">Uploaded</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-xs">
                {documents.map((doc) => (
                  <tr key={doc.id} className="hover:bg-slate-50/80 transition-colors">
                    <td className="py-3 px-4 font-semibold text-slate-900 max-w-xs truncate">
                      {doc.filename}
                    </td>
                    <td className="py-3 px-4">
                      <span className="px-2 py-0.5 rounded-md bg-slate-100 text-slate-700 font-mono text-[10px] uppercase font-bold">
                        .{doc.file_type}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-slate-500">{formatBytes(doc.file_size)}</td>
                    <td className="py-3 px-4">
                      {doc.processing_status === 'indexed' && (
                        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-emerald-50 text-emerald-700 text-[11px] font-semibold border border-emerald-200">
                          <CheckCircle2 className="w-3 h-3" /> Indexed
                        </span>
                      )}
                      {doc.processing_status === 'processing' && (
                        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-blue-50 text-blue-700 text-[11px] font-semibold border border-blue-200">
                          <div className="w-2.5 h-2.5 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
                          Processing
                        </span>
                      )}
                      {doc.processing_status === 'uploaded' && (
                        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-amber-50 text-amber-700 text-[11px] font-semibold border border-amber-200">
                          <Clock className="w-3 h-3" /> Queued
                        </span>
                      )}
                      {doc.processing_status === 'failed' && (
                        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-red-50 text-red-700 text-[11px] font-semibold border border-red-200" title={doc.error_message || ''}>
                          <AlertCircle className="w-3 h-3" /> Failed
                        </span>
                      )}
                    </td>
                    <td className="py-3 px-4 text-slate-600 font-medium">
                      {doc.page_count > 0 ? `${doc.page_count} pages` : '—'}
                    </td>
                    <td className="py-3 px-4 text-slate-400">{formatDate(doc.created_at)}</td>
                    <td className="py-3 px-4 text-right">
                      <div className="flex items-center justify-end gap-1.5">
                        {/* Preview */}
                        <button
                          onClick={() => setPreviewDocId(doc.id)}
                          title="Preview Extracted Content"
                          className="p-1.5 text-slate-500 hover:text-brand-600 hover:bg-slate-100 rounded-lg transition-colors"
                        >
                          <Eye className="w-4 h-4" />
                        </button>

                        {/* Reprocess if failed */}
                        {doc.processing_status === 'failed' && (
                          <button
                            onClick={() => reprocessMutation.mutate(doc.id)}
                            title="Retry Processing"
                            className="p-1.5 text-amber-600 hover:bg-amber-50 rounded-lg transition-colors"
                          >
                            <RefreshCw className="w-4 h-4" />
                          </button>
                        )}

                        {/* Delete */}
                        <button
                          onClick={() => {
                            if (window.confirm(`Delete "${doc.filename}" and its vector embeddings?`)) {
                              deleteMutation.mutate(doc.id);
                            }
                          }}
                          title="Delete Document"
                          className="p-1.5 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Document Content Preview Modal */}
      {previewDocId && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-navy-900/60 backdrop-blur-sm animate-in fade-in">
          <div className="relative w-full max-w-3xl max-h-[85vh] bg-white rounded-2xl shadow-2xl border border-slate-200 flex flex-col overflow-hidden">
            <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100 bg-slate-50">
              <div className="flex items-center gap-2.5">
                <FileCode className="w-5 h-5 text-brand-600" />
                <div>
                  <h3 className="text-sm font-bold text-slate-900 truncate max-w-md">
                    {previewContent?.filename || 'Document Preview'}
                  </h3>
                  <span className="text-[11px] text-slate-500">
                    {previewContent?.chunks.length || 0} Searchable Chunks • {previewContent?.page_count || 1} Pages
                  </span>
                </div>
              </div>
              <button
                onClick={() => setPreviewDocId(null)}
                className="p-1.5 text-slate-400 hover:text-slate-600 rounded-lg"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto p-6 space-y-4">
              {isPreviewLoading ? (
                <div className="py-12 text-center">
                  <div className="w-8 h-8 border-4 border-brand-200 border-t-brand-600 rounded-full animate-spin mx-auto mb-2" />
                  <p className="text-xs text-slate-500">Extracting document passages...</p>
                </div>
              ) : previewContent?.chunks.length === 0 ? (
                <p className="text-xs text-slate-500 italic">No extracted chunks found for this document.</p>
              ) : (
                previewContent?.chunks.map((chunk) => (
                  <div key={chunk.id} className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-2">
                    <div className="flex items-center justify-between text-[11px] font-semibold text-slate-500">
                      <span className="text-brand-700">Chunk #{chunk.chunk_index + 1}</span>
                      <div className="flex items-center gap-2">
                        {chunk.page_number && <span className="bg-slate-200 px-2 py-0.5 rounded">Page {chunk.page_number}</span>}
                        {chunk.slide_number && <span className="bg-amber-100 text-amber-800 px-2 py-0.5 rounded">Slide {chunk.slide_number}</span>}
                        {chunk.section_title && <span className="text-slate-600 truncate max-w-[200px]">{chunk.section_title}</span>}
                      </div>
                    </div>
                    <p className="text-xs text-slate-800 leading-relaxed font-mono whitespace-pre-wrap">
                      {chunk.chunk_text}
                    </p>
                  </div>
                ))
              )}
            </div>

            <div className="px-6 py-3 bg-slate-50 border-t border-slate-100 flex justify-end">
              <button
                onClick={() => setPreviewDocId(null)}
                className="px-4 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-200 rounded-xl transition-colors"
              >
                Close Preview
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
