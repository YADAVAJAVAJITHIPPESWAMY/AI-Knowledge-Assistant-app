export interface User {
  id: string;
  name: string;
  email: string;
  created_at: string;
  updated_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export interface Document {
  id: string;
  filename: string;
  file_type: 'pdf' | 'docx' | 'doc' | 'pptx' | 'ppt' | 'txt' | 'md';
  file_size: number;
  processing_status: 'uploaded' | 'processing' | 'indexed' | 'failed';
  page_count: number;
  error_message?: string | null;
  created_at: string;
  updated_at: string;
}

export interface DocumentChunk {
  id: string;
  chunk_index: number;
  chunk_text: string;
  page_number?: number | null;
  slide_number?: number | null;
  section_title?: string | null;
  token_count: number;
  chunk_metadata?: Record<string, any>;
}

export interface DocumentContent {
  id: string;
  filename: string;
  file_type: string;
  page_count: number;
  content: string;
  chunks: DocumentChunk[];
}

export interface CitationItem {
  citation_number: number;
  document_id: string;
  document_name: string;
  page_number?: number | null;
  slide_number?: number | null;
  section_title?: string | null;
  chunk_id: string;
  excerpt: string;
  similarity_score: number;
}

export interface Message {
  id: string;
  conversation_id: string;
  role: 'user' | 'assistant';
  content: string;
  citations?: CitationItem[];
  created_at: string;
}

export interface Conversation {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  message_count: number;
}

export interface ChatResponse {
  conversation_id: string;
  query: string;
  answer: string;
  citations: CitationItem[];
  created_at: string;
}

export interface InsightResult {
  title: string;
  document_ids: string[];
  result: string;
  metadata?: Record<string, any>;
}

export interface QuizQuestion {
  question: string;
  options: string[];
  correct_answer_index: number;
  explanation: string;
}

export interface QuizResponse {
  document_id: string;
  document_name: string;
  quiz: QuizQuestion[];
}
