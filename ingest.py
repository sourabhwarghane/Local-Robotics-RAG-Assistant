from collections import Counter
from src.document_loader import load_documents
from src.text_splitter import create_chunks
from src.embeddings import EmbeddingModel
from src.vector_store import create_faiss_index, save_vector_store


DATA_PATH = "data/raw"


def main():
    print("=" * 60)
    print("LOCAL ROBOTICS RAG - DOCUMENT LOADER")
    print("=" * 60)
    print("\nLoading knowledge base...\n")

    documents = load_documents(DATA_PATH)
    chunks = create_chunks(
        documents,
        chunk_size=1000,
        chunk_overlap=200,
    )

    print("\n" + "=" * 60)
    print("GENERATING EMBEDDINGS")
    print("=" * 60)

    texts = [
        chunk["text"]
        for chunk in chunks
    ]
    embedding_model = EmbeddingModel()
    embeddings = embedding_model.encode_documents(texts)
    print()
    print("Embedding matrix shape:", embeddings.shape)

    print("\n" + "=" * 60)
    print("CREATING FAISS INDEX")
    print("=" * 60)

    index = create_faiss_index(embeddings)
    print("Vectors stored in FAISS:", index.ntotal)

    print("\n" + "=" * 60)
    print("SAVING VECTOR DATABASE")
    print("=" * 60)

    save_vector_store(index, chunks, folder_path="vector_db")

    if not documents:
        print("\nNo documents were loaded.")
        return

    print("\n" + "=" * 60)
    print("KNOWLEDGE BASE SUMMARY")
    print("=" * 60)

    categories = Counter(
        document["category"]
        for document in documents
    )

    file_types = Counter(
        document["file_type"]
        for document in documents
    )

    print("\nCategories:")

    for category, count in categories.items():
        print(f"  {category:<20} {count}")

    print("\nFile types:")

    for file_type, count in file_types.items():
        print(f"  {file_type:<20} {count}")

    print("\n" + "=" * 60)
    print("SAMPLE DOCUMENT")
    print("=" * 60)

    sample = documents[0]

    print("\nSource:")
    print(sample["source"])

    print("\nCategory:")
    print(sample["category"])

    print("\nFile type:")
    print(sample["file_type"])

    print("\nPage:")
    print(sample["page"])

    print("\nExtracted text:")
    print("-" * 60)

    print(sample["text"][:1000])

    print("\n" + "-" * 60)

    print(
        f"\nTotal extracted characters: "
        f"{sum(len(doc['text']) for doc in documents):,}"
    )

    print("\n" + "=" * 60)
    print("CHUNKING SUMMARY")
    print("=" * 60)

    print(f"\nOriginal document sections : {len(documents)}")
    print(f"Generated chunks           : {len(chunks)}")

    average_chunk_size = (
        sum(len(chunk["text"]) for chunk in chunks)
        / len(chunks)
    )

    print(
        f"Average chunk size         : "
        f"{average_chunk_size:.0f} characters"
    )

    print("\n" + "=" * 60)
    print("SAMPLE CHUNKS")
    print("=" * 60)

    for chunk in chunks[:3]:
        print()
        print("-" * 60)
        print("Chunk ID :", chunk["chunk_id"])
        print("Source   :", chunk["source"])
        print("Category :", chunk["category"])
        print("Page     :", chunk["page"])

        print()

        print(chunk["text"][:1000])


if __name__ == "__main__":
    main()
