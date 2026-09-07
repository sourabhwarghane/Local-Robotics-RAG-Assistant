from src.embeddings import EmbeddingModel
from src.vector_store import load_vector_store
from src.retriever import HybridRetriever
from src.llm import LocalLLM


class RoboticsRAG:

    def __init__(self, vector_db_path="vector_db", model_name=None):

        print("Loading Robotics RAG system...")

        # Load FAISS + chunk metadata
        self.index, self.chunks = (load_vector_store(vector_db_path))

        print(
            f"Loaded "
            f"{self.index.ntotal} vectors."
        )

        # Load embedding model
        self.embedding_model = (EmbeddingModel())

        # Create hybrid retriever
        self.retriever = (
            HybridRetriever(
                index=self.index,
                chunks=self.chunks,
                embedding_model=(
                    self.embedding_model
                ),
            )
        )

        # Load local LLM
        if model_name:
            self.llm = LocalLLM(model_name=model_name)
        else:
            self.llm = LocalLLM()

        print("Robotics RAG ready.")

    def build_context(self, results):
        """
        Convert retrieved chunks into a single
        context block for the LLM.
        """

        context_parts = []

        for number, result in enumerate(results, start=1):
            source = result["source"]
            page = result["page"]
            text = result["text"]

            source_info = source

            if page is not None:
                source_info += (f" | Page {page}")

            section = (
                f"\n"
                f"[SOURCE {number}]\n"
                f"{source_info}\n"
                f"{text}\n"
            )

            context_parts.append(section)

        return "\n".join(context_parts)

    def build_prompt(self, question, context):
        """
        Build a grounded prompt for the local LLM.
        """
        return f"""
    You are a Robotics Knowledge Assistant.

    Use the CONTEXT below to answer the QUESTION.

    Instructions:

    - Answer only using information from the context.
    - If the answer is present, give a short and clear technical answer.
    - Do not add facts that are not supported by the context.
    - Use the technical terminology used in the context whenever possible.
    - Prefer precise source wording over broader or vague wording.
    For example, if the context says "freshness", "low latency",
    "guaranteed delivery", or "retransmission", use those concepts
    instead of replacing them with a general word such as "efficiency".
    - Write the answer as grammatically correct, complete sentences,
    while preserving the technical terminology used in the context.
    - Do not guess or infer undocumented hardware, specifications,
    behavior, or project details.
    - If the context does not contain enough information to answer,
    say exactly:

    I do not have enough information in the knowledge base to answer that.

    CONTEXT:

    {context}

    QUESTION:

    {question}

    ANSWER:
    """

    def is_question_only_chunk(self, text):
        """
        Detect chunks that are mainly lists of
        study/interview questions rather than answers.
        """

        text_lower = text.lower()

        question_count = text.count("?")

        has_answer_marker = ("answer:" in text_lower)

        if (
            question_count >= 3
            and not has_answer_marker
        ):
            return True
        return False

    def ask(self, question, top_k=3):
        """
        Full RAG flow:
        question -> retrieval -> filtering
        -> context -> LLM -> answer
        """

        # Retrieve more candidates first.
        candidate_results = self.retriever.search(question, top_k=9)

        # Remove chunks that are mainly question lists.
        filtered_results = []

        for result in candidate_results:
            if self.is_question_only_chunk(result["text"]):
                continue

            filtered_results.append(result)

        # Keeps only the best final chunks.
        results = filtered_results[:top_k]

        # Builds context.
        context = self.build_context(results)

        # Builds prompt.
        prompt = self.build_prompt(question, context)

        # Generates answer.
        answer = self.llm.generate(prompt)

        return {
            "question": question,
            "answer": answer,
            "sources": results,
        }
