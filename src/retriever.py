import re
import numpy as np
from rank_bm25 import BM25Okapi
from src.vector_store import search_vector_store
from src.reranker import Reranker


def tokenize(text):
    """
    Normalize technical terms before BM25 tokenization.

    Examples:
    BEST_EFFORT -> best effort
    sensor-data -> sensor data
    """
    text = text.lower()
    text = text.replace("_", " ")
    text = text.replace("-", " ")

    return re.findall(r"\b\w+\b", text)


class HybridRetriever:

    def __init__(
        self,
        index,
        chunks,
        embedding_model,
        semantic_candidates=50,
        keyword_candidates=50,
    ):

        self.index = index
        self.chunks = chunks
        self.embedding_model = embedding_model

        self.semantic_candidates = (semantic_candidates)
        self.keyword_candidates = (keyword_candidates)

        print("Building BM25 keyword index...")

        tokenized_chunks = [
            tokenize(chunk["text"])
            for chunk in chunks
        ]

        self.bm25 = BM25Okapi(tokenized_chunks)
        print("BM25 index ready.")
        self.reranker = Reranker()

    def get_semantic_candidates(self, question):
        query_embedding = (self.embedding_model.encode_query(question))

        results = search_vector_store(
            index=self.index,
            chunks=self.chunks,
            query_embedding=query_embedding,
            top_k=self.semantic_candidates,
        )

        candidates = {}

        for result in results:
            result["semantic_score"] = (result["score"])
            candidates[result["chunk_id"]] = result
        return candidates

    def get_keyword_candidates(self, question):
        query_tokens = tokenize(question)

        scores = self.bm25.get_scores(query_tokens)

        top_indices = np.argsort(
            scores
        )[::-1][
            :self.keyword_candidates
        ]
        candidates = {}

        for index_position in top_indices:
            score = float(scores[index_position])

            if score <= 0:
                continue

            chunk = self.chunks[index_position].copy()
            chunk["keyword_score"] = score
            candidates[chunk["chunk_id"]] = chunk

        return candidates

    def search(self, question, top_k=5):
        # ---------------------------------
        # FAISS candidates
        # ---------------------------------
        semantic_candidates = (self.get_semantic_candidates(question))

        # ---------------------------------
        # BM25 candidates
        # ---------------------------------
        keyword_candidates = (self.get_keyword_candidates(question))

        # ---------------------------------
        # Merge candidate sets
        # ---------------------------------
        merged = {}

        for chunk_id, result in (semantic_candidates.items()):
            merged[chunk_id] = result

        for chunk_id, result in (keyword_candidates.items()):
            if chunk_id in merged:
                merged[
                    chunk_id
                ]["keyword_score"] = (
                    result[
                        "keyword_score"
                    ]
                )
            else:
                result["semantic_score"] = 0.0
                merged[chunk_id] = result

        # Add missing scores
        for result in merged.values():
            result.setdefault("semantic_score", 0.0)
            result.setdefault("keyword_score", 0.0)

        candidates = list(merged.values())

        # ---------------------------------
        # CrossEncoder reranking
        # ---------------------------------

        results = self.reranker.rerank(
            question=question,
            candidates=candidates,
            top_k=top_k,
        )
        return results
