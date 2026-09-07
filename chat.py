from src.rag_pipeline import RoboticsRAG


def print_sources(results):
    """
    Display unique document sources used
    by the RAG system.
    """

    shown = set()

    print("\nSources:")

    for result in results:

        source = result["source"]
        page = result["page"]

        key = (
            source,
            page,
        )

        if key in shown:
            continue

        shown.add(key)

        if page is not None:

            print(
                f"- {source} "
                f"(Page {page})"
            )

        else:

            print(
                f"- {source}"
            )


def main():

    print("=" * 60)
    print(
        "LOCAL ROBOTICS RAG ASSISTANT"
    )
    print("=" * 60)

    rag = RoboticsRAG()

    while True:

        print()

        question = input(
            "Ask a robotics question "
            "(or type 'exit'): "
        ).strip()

        if question.lower() in {
            "exit",
            "quit",
        }:
            break

        if not question:
            continue

        print(
            "\nSearching knowledge base..."
        )

        result = rag.ask(
            question
        )

        print("\n" + "=" * 60)
        print("ANSWER")
        print("=" * 60)

        print()

        answer = result["answer"].strip()
        print(answer)
        fallback_answer = (
            "I do not have enough information in the "
            "knowledge base to answer that."
        )
        if answer != fallback_answer:
            print_sources(
                result["sources"]
            )

        print(
            "\n" + "=" * 60
        )


if __name__ == "__main__":
    main()
