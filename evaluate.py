import argparse
import csv
import json
from pathlib import Path
from src.rag_pipeline import RoboticsRAG


QUESTIONS_FILE = "evaluation_questions.json"

FALLBACK_ANSWER = (
    "I do not have enough information in the "
    "knowledge base to answer that."
)


def load_questions():
    with open(QUESTIONS_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def calculate_keyword_score(answer, expected_keywords):
    if not expected_keywords:
        return 0.0

    answer_lower = answer.lower()
    matches = 0

    for keyword in expected_keywords:
        if keyword.lower() in answer_lower:
            matches += 1

    return (matches / len(expected_keywords))


def calculate_source_hit(sources, expected_sources):
    if not expected_sources:
        return False

    retrieved_names = [
        source["source"].lower()
        for source in sources
    ]

    for expected in expected_sources:
        expected = expected.lower()

        for retrieved in retrieved_names:
            if expected in retrieved:
                return True

    return False


def is_refusal(answer):
    return (FALLBACK_ANSWER.lower() in answer.lower())


def evaluate_question(rag, item):

    print("\n" + "=" * 70)
    print(
        f"QUESTION {item['id']}: "
        f"{item['question']}"
    )
    print("=" * 70)

    result = rag.ask(item["question"])

    answer = result["answer"].strip()

    print("\nAnswer:")
    print(answer)

    source_names = []

    for source in result["sources"]:
        source_names.append(source["source"])

    print("\nRetrieved sources:")

    for source_name in source_names:
        print(f"- {source_name}")

    # ---------------------------------
    # Unanswerable question
    # ---------------------------------

    if item["type"] == "unanswerable":
        refusal_correct = is_refusal(answer)
        print(
            "\nRefusal correct:",
            refusal_correct,
        )

        return {
            "id": item["id"],
            "type": item["type"],
            "question": item["question"],
            "answer": answer,
            "keyword_score": "",
            "source_hit": "",
            "refusal_correct": refusal_correct,
            "pass": refusal_correct,
            "sources": " | ".join(
                source_names
            ),
        }

    # ---------------------------------
    # Answerable question
    # ---------------------------------

    keyword_score = (
        calculate_keyword_score(
            answer,
            item.get(
                "expected_keywords",
                [],
            ),
        )
    )

    source_hit = (
        calculate_source_hit(
            result["sources"],
            item.get(
                "expected_sources",
                [],
            ),
        )
    )

    refused = is_refusal(answer)

    # Initial simple automatic rule:
    # at least half the expected terms,
    # correct source,
    # and no false refusal.

    passed = (
        keyword_score >= 0.5
        and source_hit
        and not refused
    )

    print(f"\nKeyword score: "f"{keyword_score:.2f}")
    print(f"Source hit: {source_hit}")
    print(f"Pass: {passed}")

    return {
        "id": item["id"],
        "type": item["type"],
        "question": item["question"],
        "answer": answer,
        "keyword_score": round(
            keyword_score,
            2,
        ),
        "source_hit": source_hit,
        "refusal_correct": "",
        "pass": passed,
        "sources": " | ".join(
            source_names
        ),
    }


def save_results(results, model_name):
    output_folder = Path("evaluation_results")
    output_folder.mkdir(exist_ok=True)

    safe_model_name = (model_name.replace(":", "_",))

    output_path = (output_folder / f"{safe_model_name}_results.csv")

    fieldnames = [
        "id",
        "type",
        "question",
        "answer",
        "keyword_score",
        "source_hit",
        "refusal_correct",
        "pass",
        "sources",
    ]

    with open(
        output_path,
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    return output_path


def print_summary(results, model_name):
    total = len(results)
    passed = sum(1 for result in results if result["pass"])

    answerable = [
        result
        for result in results
        if result["type"]
        != "unanswerable"
    ]

    unanswerable = [
        result
        for result in results
        if result["type"]
        == "unanswerable"
    ]

    source_hits = sum(
        1
        for result in answerable
        if result["source_hit"]
    )

    correct_refusals = sum(
        1
        for result in unanswerable
        if result[
            "refusal_correct"
        ]
    )

    print("\n")
    print("=" * 70)
    print("EVALUATION SUMMARY")
    print("=" * 70)
    print(f"Model: {model_name}")
    print(f"Overall passed: " f"{passed}/{total}")
    print(f"Overall score: " f"{passed / total * 100:.1f}%")
    print(f"Retrieval source hits: " f"{source_hits}/" f"{len(answerable)}")
    print(f"Correct refusals: " f"{correct_refusals}/" f"{len(unanswerable)}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model",
        default="qwen3:1.7b",
        help="Ollama model name",
    )
    args = parser.parse_args()

    questions = load_questions()

    print("=" * 70)
    print("LOCAL ROBOTICS RAG EVALUATION")
    print("=" * 70)
    print(f"\nModel: {args.model}")
    print(f"Questions: {len(questions)}")

    rag = RoboticsRAG(model_name=args.model)

    results = []

    for item in questions:
        result = evaluate_question(rag, item)
        results.append(result)

    output_path = save_results(results, args.model)

    print_summary(results, args.model)

    print(f"\nResults saved to: " f"{output_path}")


if __name__ == "__main__":
    main()
