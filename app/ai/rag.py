from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai.embeddings import EmbeddingService
from app.ai.llm import LLMService
from app.models import DocumentChunk


class RAGService:
    def __init__(self, db: Session):
        self.db = db
        self.embedding_service = EmbeddingService()
        self.llm_service = LLMService()

    def search_similar_chunks(self, user_id: int, question: str, top_k: int = 5) -> list[DocumentChunk]:
        question_vector = self.embedding_service.get_embedding(question)
        rows = self.db.execute(
            select(DocumentChunk, DocumentChunk.document_id)
            .join("document")
            .where(DocumentChunk.embedding.is_not(None))
        ).all()
        scored: list[tuple[float, DocumentChunk]] = []
        for chunk in [row[0] for row in rows]:
            doc = chunk.document
            if doc and doc.user_id == user_id:
                candidate_vector = chunk.embedding or []
                similarity = self._cosine_similarity(question_vector, candidate_vector)
                scored.append((similarity, chunk))

        scored.sort(key=lambda item: item[0], reverse=True)
        return [chunk for _, chunk in scored[:top_k]]

    def build_prompt(self, question: str, context_chunks: list[DocumentChunk]) -> str:
        context_text = "\n\n".join(f"Source document {chunk.document_id} chunk {chunk.chunk_index}:\n{chunk.content}" for chunk in context_chunks)
        return (
            "Use only the supplied context to answer the user's question. "
            "Do not invent information. If the context does not contain the answer, say that the information was not found. "
            "Clearly distinguish the answer from the source information.\n\n"
            f"User question: {question}\n\nContext:\n{context_text}"
        )

    def answer_question(self, user_id: int, question: str, top_k: int = 5) -> tuple[str, list[DocumentChunk]]:
        chunks = self.search_similar_chunks(user_id, question, top_k=top_k)
        prompt = self.build_prompt(question, chunks)
        answer = self.llm_service.generate_response(prompt)
        return answer, chunks

    @staticmethod
    def _cosine_similarity(a: list[float], b: list[float]) -> float:
        if not a or not b:
            return 0.0
        numerator = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return numerator / (norm_a * norm_b)
