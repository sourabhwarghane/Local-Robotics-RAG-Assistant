def split_text(text, chunk_size=1000, chunk_overlap=200):
    """
    Split text into overlapping chunks.

    chunk_size:
        Maximum approximate number of characters
        in each chunk.

    chunk_overlap:
        Number of characters shared between
        neighbouring chunks.
    """

    if not text:
        return []

    if len(text) <= chunk_size:
        return [text]

    chunks = []

    start = 0
    text_length = len(text)

    while start < text_length:
        end = min(start + chunk_size, text_length)
        chunk = text[start:end]

        # Try to avoid cutting in the middle
        # of a paragraph or sentence.
        if end < text_length:
            possible_breaks = [
                chunk.rfind("\n"),
                chunk.rfind(". "),
                chunk.rfind("? "),
                chunk.rfind("! "),
            ]

            best_break = max(possible_breaks)

            # Only use the natural break if it
            # isn't too far from the end.
            if best_break > chunk_size * 0.6:
                end = start + best_break + 1
                chunk = text[start:end]

        chunk = chunk.strip()

        if chunk:
            chunks.append(chunk)

        new_start = end - chunk_overlap

        # Safety check so the loop always advances.
        if new_start <= start:
            new_start = end

        while (
            new_start < text_length
            and new_start > 0
            and not text[new_start - 1].isspace()
        ):
            new_start += 1
        start = new_start
    return chunks


def create_chunks(documents, chunk_size=1000, chunk_overlap=200):
    """
    Split loaded documents into smaller chunks
    while preserving their metadata.
    """
    all_chunks = []

    chunk_id = 0

    for document in documents:
        text_chunks = split_text(
            document["text"],
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

        for index, text in enumerate(text_chunks):
            chunk = {
                "chunk_id": chunk_id,
                "text": text,
                "source": document["source"],
                "source_path": document["source_path"],
                "category": document["category"],
                "file_type": document["file_type"],
                "page": document["page"],
                "chunk_index": index,
            }

            all_chunks.append(chunk)
            chunk_id += 1

    return all_chunks
