import numpy as np
from sentence_transformers import CrossEncoder

RERANKER_MODEL = ("cross-encoder/ms-marco-MiniLM-L6-v2")


class Reranker:

    def __init__(self, model_name=RERANKER_MODEL):
        print(
            f"Loading reranker model: "
            f"{model_name}"
        )
        self.model = CrossEncoder(model_name)
        print("Reranker model loaded.")

    def rerank(self, question, candidates, top_k=5):
        if not candidates:
            return []

        pairs = [
            (
                question,
                candidate["text"],
            )
            for candidate in candidates
        ]

        scores = self.model.predict(pairs, batch_size=16)
        scores = np.asarray(scores).reshape(-1)

        reranked_results = []

        for candidate, score in zip(candidates, scores):
            result = candidate.copy()

            result["rerank_score"] = float(score)

            reranked_results.append(result)

        reranked_results.sort(
            key=lambda item: item[
                "rerank_score"
            ],
            reverse=True,
        )

        return reranked_results[:top_k]
