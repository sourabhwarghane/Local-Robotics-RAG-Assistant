import json


CHUNKS_PATH = "vector_db/chunks.json"


with open(
    CHUNKS_PATH,
    "r",
    encoding="utf-8",
) as file:
    chunks = json.load(file)


search_terms = [
    "measurement range",
    "measuring range",
    "ranging range",
    "distance range",
    "12 m",
    "12m",
]


for term in search_terms:
    print("\n" + "=" * 70)
    print(f"SEARCHING FOR: {term}")
    print("=" * 70)

    found = False

    for chunk in chunks:
        source = chunk["source"].lower()

        if "rplidar_c1_datasheet" not in source:
            continue

        if term.lower() in chunk["text"].lower():
            found = True

            print()
            print("Chunk ID:", chunk["chunk_id"])
            print("Page:", chunk["page"])
            print("-" * 70)
            print(chunk["text"])
            print("-" * 70)

    if not found:
        print("No match found.")
