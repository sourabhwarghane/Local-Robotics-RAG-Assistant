import streamlit as st
from src.rag_pipeline import RoboticsRAG


FALLBACK_ANSWER = (
    "I do not have enough information in the "
    "knowledge base to answer that."
)


MODEL_OPTIONS = {
    "Qwen3 1.7B — Final": "qwen3:1.7b",
    "Gemma3 1B — Comparison": "gemma3:1b",
}


EXAMPLE_QUESTIONS = [
    "What does the AMR watchdog node monitor?",
    "What is the maximum measuring range of the RPLIDAR C1?",
    "Why does my AMR use BEST_EFFORT QoS for camera images?",
    "What GPS module does my AMR use?",
]


# --------------------------------------------------
# Page configuration
# --------------------------------------------------

st.set_page_config(
    page_title="Robotics RAG Assistant",
    page_icon="🤖",
    layout="wide",
)


# --------------------------------------------------
# RAG loading
# --------------------------------------------------

@st.cache_resource
def load_rag(model_name):
    return RoboticsRAG(model_name=model_name)

# --------------------------------------------------
# Source formatting
# --------------------------------------------------


def get_unique_sources(results):
    sources = []

    seen = set()

    for result in results:
        source = result["source"]
        page = result["page"]

        key = (source, page)

        if key in seen:
            continue

        seen.add(key)

        if page is not None:
            label = (f"{source} — Page {page}")

        else:
            label = source

        sources.append(
            {
                "label": label,
                "source": source,
                "page": page,
                "category": result["category"],

                "rerank_score": result.get(
                    "rerank_score",
                    0.0,
                ),

                "semantic_score": result.get(
                    "semantic_score",
                    0.0,
                ),

                "bm25_score": result.get(
                    "keyword_score",
                    0.0,
                ),
            }
        )

    return sources


# --------------------------------------------------
# Session state
# --------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []


if "active_model" not in st.session_state:
    st.session_state.active_model = ("qwen3:1.7b")


if "pending_question" not in st.session_state:
    st.session_state.pending_question = None


# --------------------------------------------------
# Sidebar
# --------------------------------------------------

with st.sidebar:
    st.title("🤖 Robotics RAG")

    st.write(
        "Local knowledge assistant for "
        "robotics, ROS 2, AMR hardware "
        "and project documentation."
    )
    st.divider()

    # ----------------------------------------------
    # Model selector
    # ----------------------------------------------

    st.subheader("Local LLM")

    model_labels = list(
        MODEL_OPTIONS.keys()
    )

    current_label = next(
        label
        for label, model in MODEL_OPTIONS.items()
        if model
        == st.session_state.active_model
    )

    selected_label = st.selectbox(
        "Model",
        model_labels,
        index=model_labels.index(
            current_label
        ),
    )

    selected_model = (
        MODEL_OPTIONS[
            selected_label
        ]
    )

    if (
        selected_model
        != st.session_state.active_model
    ):

        st.session_state.active_model = (
            selected_model
        )

        st.session_state.messages = []

        # Remove old cached RAG object.
        load_rag.clear()

        st.rerun()

    if (
        st.session_state.active_model
        == "qwen3:1.7b"
    ):

        st.caption(
            "Final model — better answer quality."
        )

    else:
        st.caption(
            "Comparison model — lighter, "
            "but weaker generation quality."
        )

    st.divider()

    # ----------------------------------------------
    # System information
    # ----------------------------------------------

    st.subheader("Retrieval System")

    st.write(
        "**Embeddings:** all-MiniLM-L6-v2"
    )

    st.write(
        "**Vector Search:** FAISS"
    )

    st.write(
        "**Keyword Search:** BM25"
    )

    st.write(
        "**Reranker:** CrossEncoder"
    )

    st.write(
        "**Final context:** Top 3 chunks"
    )

    st.divider()

    # ----------------------------------------------
    # Knowledge base
    # ----------------------------------------------

    st.subheader("Knowledge Base")

    st.write(
        """
        - Autonomous Mobile Robot
        - ROS 2 Humble
        - NVIDIA Jetson Orin Nano
        - RPLIDAR C1
        - ESP32-C3
        - IMX219 Camera
        - BTS7960 Motor Driver
        """
    )

    st.divider()

    if st.button("Clear Conversation", use_container_width=True):
        st.session_state.messages = []

        st.rerun()


# --------------------------------------------------
# Header
# --------------------------------------------------

st.title(
    "Local Robotics Knowledge Assistant"
)

st.caption(
    "Retrieval-Augmented Generation using "
    "FAISS + BM25 + CrossEncoder + Ollama"
)

st.info(
    "This assistant answers questions from a local "
    "robotics knowledge base. Unsupported questions "
    "should be refused rather than answered from guesswork."
)


# --------------------------------------------------
# Example questions
# --------------------------------------------------

st.subheader("Try an example")

column_1, column_2 = st.columns(2)

with column_1:

    if st.button(
        EXAMPLE_QUESTIONS[0],
        use_container_width=True,
    ):

        st.session_state.pending_question = (
            EXAMPLE_QUESTIONS[0]
        )

    if st.button(
        EXAMPLE_QUESTIONS[2],
        use_container_width=True,
    ):

        st.session_state.pending_question = (
            EXAMPLE_QUESTIONS[2]
        )


with column_2:

    if st.button(
        EXAMPLE_QUESTIONS[1],
        use_container_width=True,
    ):

        st.session_state.pending_question = (
            EXAMPLE_QUESTIONS[1]
        )

    if st.button(
        EXAMPLE_QUESTIONS[3],
        use_container_width=True,
    ):

        st.session_state.pending_question = (
            EXAMPLE_QUESTIONS[3]
        )

st.divider()

# --------------------------------------------------
# Load RAG
# --------------------------------------------------

with st.spinner(
    "Loading robotics knowledge system..."
):

    rag = load_rag(
        st.session_state.active_model
    )


# --------------------------------------------------
# Existing chat history
# --------------------------------------------------

for message in st.session_state.messages:
    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )

        if (
            message["role"] == "assistant"
            and message.get("sources")
        ):

            # --------------------------------------
            # Source list
            # --------------------------------------

            with st.expander(
                "📚 Sources"
            ):

                for source in message[
                    "sources"
                ]:

                    st.markdown(
                        f"**{source['label']}**"
                    )

                    st.caption(
                        f"Category: "
                        f"{source['category']}"
                    )

            # --------------------------------------
            # Retrieval details
            # --------------------------------------

            with st.expander(
                "🔎 Retrieval details"
            ):

                for number, source in enumerate(
                    message["sources"],
                    start=1,
                ):

                    st.markdown(
                        f"### Result {number}"
                    )

                    st.write(
                        f"**Source:** "
                        f"{source['label']}"
                    )

                    st.write(
                        f"**Category:** "
                        f"{source['category']}"
                    )

                    st.write(
                        f"**Rerank score:** "
                        f"{source['rerank_score']:.4f}"
                    )

                    st.write(
                        f"**Semantic score:** "
                        f"{source['semantic_score']:.4f}"
                    )

                    st.write(
                        f"**BM25 score:** "
                        f"{source['bm25_score']:.4f}"
                    )

                    st.divider()


# --------------------------------------------------
# Question input
# --------------------------------------------------

typed_question = st.chat_input(
    "Ask a question about robotics, "
    "ROS 2, your AMR, or its hardware..."
)

question = None

if typed_question:
    question = typed_question


elif st.session_state.pending_question:
    question = (
        st.session_state.pending_question
    )
    st.session_state.pending_question = None


# --------------------------------------------------
# Generate response
# --------------------------------------------------

if question:
    # ----------------------------------------------
    # Display user question
    # ----------------------------------------------
    st.session_state.messages.append(
        {
            "role": "user",
            "content": question,
        }
    )
    with st.chat_message("user"):
        st.markdown(
            question
        )

    # ----------------------------------------------
    # Generate RAG response
    # ----------------------------------------------
    with st.chat_message(
        "assistant"
    ):
        with st.spinner(
            "Searching knowledge base..."
        ):

            result = rag.ask(
                question
            )

        answer = (
            result["answer"].strip()
        )

        st.markdown(
            answer
        )

        sources = []

        # ------------------------------------------
        # Only show evidence if an answer exists
        # ------------------------------------------

        if answer != FALLBACK_ANSWER:
            sources = get_unique_sources(
                result["sources"]
            )

            # --------------------------------------
            # Sources
            # --------------------------------------

            if sources:
                with st.expander(
                    "📚 Sources"
                ):

                    for source in sources:

                        st.markdown(
                            f"**{source['label']}**"
                        )

                        st.caption(
                            f"Category: "
                            f"{source['category']}"
                        )

                # ----------------------------------
                # Retrieval details
                # ----------------------------------

                with st.expander(
                    "🔎 Retrieval details"
                ):

                    for number, source in enumerate(
                        sources,
                        start=1,
                    ):

                        st.markdown(
                            f"### Result {number}"
                        )

                        st.write(
                            f"**Source:** "
                            f"{source['label']}"
                        )

                        st.write(
                            f"**Category:** "
                            f"{source['category']}"
                        )

                        st.write(
                            f"**Rerank score:** "
                            f"{source['rerank_score']:.4f}"
                        )

                        st.write(
                            f"**Semantic score:** "
                            f"{source['semantic_score']:.4f}"
                        )

                        st.write(
                            f"**BM25 score:** "
                            f"{source['bm25_score']:.4f}"
                        )

                        st.divider()

    # ----------------------------------------------
    # Save assistant response
    # ----------------------------------------------

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
            "sources": sources,
        }
    )
