from src.embeddings import EmbeddingModel
from src.vector_store import load_vector_store
from src.retriever import HybridRetriever


TOP_K = 5


def main():
    print("=" * 60)
    print("LOCAL ROBOTICS KNOWLEDGE SEARCH")
    print("=" * 60)

    print("\nLoading vector database...")

    index, chunks = load_vector_store("vector_db")

    print(f"Loaded {index.ntotal} vectors.")

    embedding_model = EmbeddingModel()

    retriever = HybridRetriever(
        index=index,
        chunks=chunks,
        embedding_model=embedding_model,
    )

    while True:
        print()

        question = input(
            "Ask a robotics question "
            "(or type 'exit'): "
        ).strip()

        if question.lower() in {"exit", "quit"}:
            break

        if not question:
            continue

        results = retriever.search(question, top_k=TOP_K)

        print("\n" + "=" * 60)
        print("RETRIEVED RESULTS")
        print("=" * 60)

        for rank, result in enumerate(results, start=1):
            print()
            print("-" * 60)

            print(f"Result #{rank}")

            print(
                f"Rerank score   : "
                f"{result['rerank_score']:.4f}"
            )

            print(
                f"Semantic score : "
                f"{result['semantic_score']:.4f}"
            )

            print(
                f"BM25 score     : "
                f"{result['keyword_score']:.4f}"
            )

            print(
                f"Source     : "
                f"{result['source']}"
            )
            print(
                f"Category   : "
                f"{result['category']}"
            )
            print(
                f"Page       : "
                f"{result['page']}"
            )

            print()
            print(result["text"])

        print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
