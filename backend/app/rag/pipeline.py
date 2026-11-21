"""
RAG Pipeline Implementation
Integrates User Authentication, Hybrid Retrieval, Prompt Assembly,
OpenAI Chat Completion / Streaming, and Citation Formatting.
"""
import uuid
import json
from typing import List, Optional, AsyncGenerator, Dict, Any, Tuple
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.chunk import DocumentChunk
from app.models.document import Document
from app.services.retrieval_service import retrieval_service
from app.rag.prompts import RAG_SYSTEM_PROMPT
from app.rag.citations import citation_builder
from app.schemas.chat import ChatResponse, CitationItem

try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False
    openai = None


class RAGPipeline:
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.model = settings.OPENAI_CHAT_MODEL
        self.client = None

        if HAS_OPENAI and self.api_key:
            try:
                self.client = openai.OpenAI(api_key=self.api_key)
            except Exception:
                self.client = None

    def query(
        self,
        db: Session,
        user_id: uuid.UUID,
        query_text: str,
        conversation_id: uuid.UUID,
        document_ids: Optional[List[uuid.UUID]] = None,
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> ChatResponse:
        """
        Synchronous RAG query endpoint:
        1. Retrieve relevant chunks for user
        2. Format context and citations
        3. Invoke OpenAI or offline fallback
        4. Return answer + citations
        """
        # 1. Hybrid retrieval
        scored_chunks = retrieval_service.retrieve_relevant_chunks(
            db=db,
            user_id=user_id,
            query=query_text,
            document_ids=document_ids
        )

        # 2. Build citations & format context
        citations = citation_builder.build_citations(scored_chunks)
        context_str = citation_builder.format_context_for_prompt(scored_chunks)

        # 3. Assemble prompt
        system_content = RAG_SYSTEM_PROMPT.format(context=context_str)
        messages = [{"role": "system", "content": system_content}]

        # Append past conversation context if available
        if chat_history:
            for msg in chat_history[-6:]:  # last 3 turns
                messages.append({"role": msg["role"], "content": msg["content"]})

        messages.append({"role": "user", "content": query_text})

        # 4. Generate answer
        answer = ""
        if self.client and self.api_key:
            try:
                completion = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.2,
                )
                answer = completion.choices[0].message.content or ""
            except Exception as e:
                answer = f"Error communicating with AI model: {str(e)}"
        else:
            # Fallback when no OpenAI API key is configured
            answer = self._generate_fallback_response(query_text, scored_chunks, citations)

        return ChatResponse(
            conversation_id=conversation_id,
            query=query_text,
            answer=answer,
            citations=citations
        )

    def stream_query(
        self,
        db: Session,
        user_id: uuid.UUID,
        query_text: str,
        conversation_id: uuid.UUID,
        document_ids: Optional[List[uuid.UUID]] = None,
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> AsyncGenerator[str, None]:
        """
        Server-Sent Events (SSE) generator streaming tokens and citation metadata.
        """
        scored_chunks = retrieval_service.retrieve_relevant_chunks(
            db=db,
            user_id=user_id,
            query=query_text,
            document_ids=document_ids
        )
        citations = citation_builder.build_citations(scored_chunks)
        context_str = citation_builder.format_context_for_prompt(scored_chunks)

        # Emit initial citation payload
        init_payload = {
            "type": "citations",
            "conversation_id": str(conversation_id),
            "citations": [c.model_dump(mode="json") for c in citations]
        }
        yield f"data: {json.dumps(init_payload)}\n\n"

        if self.client and self.api_key:
            try:
                system_content = RAG_SYSTEM_PROMPT.format(context=context_str)
                messages = [{"role": "system", "content": system_content}]
                if chat_history:
                    for msg in chat_history[-6:]:
                        messages.append({"role": msg["role"], "content": msg["content"]})
                messages.append({"role": "user", "content": query_text})

                stream = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.2,
                    stream=True
                )

                for chunk in stream:
                    delta = chunk.choices[0].delta.content or ""
                    if delta:
                        yield f"data: {json.dumps({'type': 'token', 'content': delta})}\n\n"

            except Exception as e:
                yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"
        else:
            # Simulated streaming for offline / fallback mode
            fallback_answer = self._generate_fallback_response(query_text, scored_chunks, citations)
            words = fallback_answer.split(" ")
            for w in words:
                yield f"data: {json.dumps({'type': 'token', 'content': w + ' '})}\n\n"

        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    def _generate_fallback_response(
        self,
        query: str,
        scored_chunks: List[Tuple[DocumentChunk, Document, float]],
        citations: List[CitationItem]
    ) -> str:
        if not scored_chunks:
            return (
                "Based on your uploaded documents, there is insufficient evidence to answer your question. "
                "Please upload relevant materials or ensure your documents have finished indexing."
            )

        # Build grounded summary from top passages
        lines = [
            f"Here is what was found regarding **\"{query}\"** across your uploaded documents:\n"
        ]
        for c in citations[:3]:
            loc = f"Page {c.page_number}" if c.page_number else (f"Slide {c.slide_number}" if c.slide_number else c.section_title)
            lines.append(f"- From **{c.document_name}** ({loc}): \"{c.excerpt}\" [{c.citation_number}]\n")

        lines.append("\n*Note: Configure your `OPENAI_API_KEY` in `.env` to enable full GPT-4o synthesis and conversational reasoning.*")
        return "\n".join(lines)


rag_pipeline = RAGPipeline()
