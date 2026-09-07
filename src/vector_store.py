from pathlib import Path
import json
import faiss
import numpy as np


def create_faiss_index(embeddings):
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)
    index.add(np.asarray(embeddings, dtype=np.float32,))
    return index


def save_vector_store(index, chunks, folder_path="vector_db"):
    folder = Path(folder_path)
    folder.mkdir(parents=True, exist_ok=True)

    index_path = folder / "robotics.index"
    metadata_path = folder / "chunks.json"

    faiss.write_index(index, str(index_path))

    with open(metadata_path, "w", encoding="utf-8") as file:
        json.dump(chunks, file, indent=2, ensure_ascii=False)

    print(f"FAISS index saved : {index_path}")
    print(f"Chunk data saved  : {metadata_path}")


def load_vector_store(folder_path="vector_db"):
    folder = Path(folder_path)
    index_path = folder / "robotics.index"
    metadata_path = folder / "chunks.json"

    index = faiss.read_index(str(index_path))

    with open(metadata_path, "r", encoding="utf-8") as file:
        chunks = json.load(file)
    return index, chunks


def search_vector_store(index, chunks, query_embedding, top_k=5):
    scores, indices = index.search(query_embedding, top_k)
    results = []

    for score, index_position in zip(scores[0], indices[0],):
        if index_position == -1:
            continue

        chunk = chunks[index_position].copy()
        chunk["score"] = float(score)
        results.append(chunk)
    return results
