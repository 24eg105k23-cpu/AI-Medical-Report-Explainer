import math
import re
from collections import Counter
from typing import Any, Dict, List, Protocol, Tuple
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.reference_document import ReferenceDocument
from app.schemas.analysis import SourceReferenceSchema

class TextChunker:
    @staticmethod
    def chunk_text(text: str, chunk_size: int = 120, overlap: int = 30) -> List[str]:
        words = text.split()
        if len(words) <= chunk_size:
            return [text]

        chunks = []
        start = 0
        while start < len(words):
            end = min(start + chunk_size, len(words))
            chunk = " ".join(words[start:end])
            chunks.append(chunk)
            if end == len(words):
                break
            start += chunk_size - overlap
        return chunks


class SimpleTFIDFEmbedding:
    """
    Lightweight sparse TF-IDF vectors computed locally without a paid API.
    """

    @staticmethod
    def tokenize(text: str) -> List[str]:
        words = re.findall(r"\b[A-Za-z0-9]{2,}\b", text.lower())
        stopwords = {
            "the", "and", "is", "in", "to", "of", "a", "with", "for", "as", "by", "on", "at", "or",
            "from", "that", "this", "it", "an", "be", "are", "was", "can", "also", "its", "has"
        }
        return [w for w in words if w not in stopwords]

    @classmethod
    def compute_similarity(cls, query: str, doc_text: str) -> float:
        query_counts = Counter(cls.tokenize(query))
        document_counts = Counter(cls.tokenize(doc_text))
        if not query_counts or not document_counts:
            return 0.0

        shared_terms = query_counts.keys() & document_counts.keys()
        if not shared_terms:
            return 0.0

        query_weights = {}
        document_weights = {}
        for term in query_counts.keys() | document_counts.keys():
            document_frequency = int(term in query_counts) + int(term in document_counts)
            inverse_document_frequency = math.log(3 / (1 + document_frequency)) + 1
            query_weights[term] = (
                (1 + math.log(query_counts[term])) * inverse_document_frequency
                if term in query_counts
                else 0
            )
            document_weights[term] = (
                (1 + math.log(document_counts[term])) * inverse_document_frequency
                if term in document_counts
                else 0
            )

        dot_product = sum(query_weights[term] * document_weights[term] for term in shared_terms)
        query_norm = math.sqrt(sum(weight * weight for weight in query_weights.values()))
        document_norm = math.sqrt(sum(weight * weight for weight in document_weights.values()))
        return dot_product / (query_norm * document_norm)


class RetrievalStrategy(Protocol):
    def score(self, query: str, document_text: str) -> float: ...


class LocalTfidfRetriever:
    def score(self, query: str, document_text: str) -> float:
        return SimpleTFIDFEmbedding.compute_similarity(query, document_text)


class MockRetriever:
    def score(self, query: str, document_text: str) -> float:
        query_terms = set(SimpleTFIDFEmbedding.tokenize(query))
        document_terms = set(SimpleTFIDFEmbedding.tokenize(document_text))
        return float(bool(query_terms.intersection(document_terms)))


class RAGService:
    def __init__(self):
        self.chunker = TextChunker()
        strategies: Dict[str, RetrievalStrategy] = {
            "local_tfidf": LocalTfidfRetriever(),
            "mock": MockRetriever(),
        }
        if settings.RETRIEVAL_MODE not in strategies:
            raise ValueError(
                "RETRIEVAL_MODE must be one of: " + ", ".join(sorted(strategies))
            )
        self.retriever = strategies[settings.RETRIEVAL_MODE]

    def retrieve_relevant_sources(
        self,
        db: Session,
        query: str,
        top_k: int = settings.VECTOR_SEARCH_TOP_K,
        min_score: float = 0.05,
    ) -> List[Tuple[SourceReferenceSchema, str, float]]:
        """
        Retrieve relevant reference chunks matching query.
        Returns: List of (SourceReferenceSchema, chunk_text, similarity_score)
        """
        ref_docs = db.query(ReferenceDocument).all()
        scored_chunks: List[Tuple[SourceReferenceSchema, str, float]] = []

        for doc in ref_docs:
            for chunk_meta in doc.chunks_metadata:
                chunk_text = chunk_meta.get("text", "")
                score = self.retriever.score(query, chunk_text)
                if score >= min_score:
                    ref_schema = SourceReferenceSchema(
                        document_id=doc.id,
                        title=doc.title,
                        publisher=doc.publisher,
                        source_url=doc.source_url,
                        revision_date=doc.revision_date,
                        section=chunk_meta.get("section", "General"),
                        chunk_id=chunk_meta.get("chunk_id"),
                    )
                    scored_chunks.append((ref_schema, chunk_text, score))

        # Sort descending by similarity score
        scored_chunks.sort(key=lambda x: x[2], reverse=True)
        return scored_chunks[:top_k]

    def validate_citations(
        self,
        cited_sources: List[SourceReferenceSchema],
        retrieved_sources: List[SourceReferenceSchema],
    ) -> List[SourceReferenceSchema]:
        """
        Safety requirement: LLM must NEVER hallucinate or invent citations.
        Filter citations so ONLY sources that were genuinely retrieved and passed in context are retained.
        """
        valid_titles = {s.title.lower().strip() for s in retrieved_sources}
        valid_chunks = {s.chunk_id for s in retrieved_sources if s.chunk_id}

        strictly_valid: List[SourceReferenceSchema] = []
        for citation in cited_sources:
            if citation.chunk_id and citation.chunk_id in valid_chunks:
                strictly_valid.append(citation)
            elif citation.title.lower().strip() in valid_titles:
                strictly_valid.append(citation)

        # If LLM didn't format citations properly or attempted to invent, fall back to retrieved sources
        if not strictly_valid and retrieved_sources:
            return retrieved_sources[:3]

        return strictly_valid


rag_service = RAGService()
