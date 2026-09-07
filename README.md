# Local Robotics RAG Assistant

A local **Retrieval-Augmented Generation (RAG)** assistant for robotics documentation, ROS 2 resources, hardware datasheets, and my Autonomous Mobile Robot (AMR) project.

The system combines **FAISS semantic search, BM25 keyword retrieval, CrossEncoder reranking, and a local LLM through Ollama** to generate grounded technical answers with source references.

The final application includes an interactive **Streamlit dashboard** and runs locally using **Qwen3 1.7B**.

---

## Features

* Fully local RAG pipeline
* Multi-format document ingestion
* FAISS semantic retrieval
* BM25 keyword retrieval
* Hybrid search
* CrossEncoder reranking
* Question-only chunk filtering
* Local LLM inference with Ollama
* Source-aware answers
* Streamlit chat interface
* Retrieval score inspection
* Hallucination / refusal testing
* Automated model evaluation

---

## Architecture

```text
Robotics Documents
        ↓
Text Extraction
        ↓
Chunking
        ↓
SentenceTransformer Embeddings
        ↓
┌─────────────────────────────┐
│                             │
↓                             ↓
FAISS                        BM25
Semantic Search        Keyword Search
│                             │
└──────────────┬──────────────┘
               ↓
      Candidate Chunks
               ↓
     CrossEncoder Reranking
               ↓
   Question-only Filtering
               ↓
        Top 3 Contexts
               ↓
        Ollama Local LLM
          Qwen3 1.7B
               ↓
       Answer + Sources
               ↓
      Streamlit Dashboard
```

---

## Knowledge Base

The current knowledge base contains documentation related to:

* Autonomous Mobile Robot architecture
* ROS 2 Humble
* NVIDIA Jetson Orin Nano
* SLAMTEC RPLIDAR C1
* ESP32-C3
* IMX219 camera
* BTS7960 motor driver
* Audio hardware

Current dataset:

```text
Source files         : 22
Document sections    : 223
Extracted text       : ~555,000 characters
Chunks               : ~939
Embedding dimension  : 384
```

---

## Retrieval Pipeline

The system uses a hybrid retrieval strategy.

### FAISS

Used for semantic similarity between the user question and document chunks.

### BM25

Used for exact technical terms such as:

```text
RPLIDAR C1
BEST_EFFORT
TensorRT
ESP32-C3
12 meters
```

### CrossEncoder

The retrieved candidates are reranked using:

```text
cross-encoder/ms-marco-MiniLM-L6-v2
```

This improved retrieval for technical specifications where semantic search alone did not always rank the best passage first.

---

## Local LLM

Final selected model:

```text
Qwen3 1.7B
```

Running through:

```text
Ollama
```

Configuration:

```text
Temperature : 0
Context     : 2048
Top Context : 3 chunks
```

If the knowledge base does not contain enough information, the assistant is instructed to respond:

```text
I do not have enough information in the knowledge base to answer that.
```

---

## Evaluation

The system was evaluated using:

```text
12 answerable questions
3 intentionally unanswerable questions
```

### Model Comparison

| Metric                |   Qwen3 1.7B |  Gemma3 1B |
| --------------------- | -----------: | ---------: |
| Automatic score       |    **93.3%** |      66.7% |
| Passed                |    **14/15** |      10/15 |
| Retrieval source hits |    **12/12** |  **12/12** |
| Correct refusals      |      **3/3** |        0/3 |
| Final choice          | ✅ Qwen3 1.7B | Comparison |

An important result was that **both models achieved 12/12 correct source retrievals**, showing that retrieval quality and generation quality are separate parts of the RAG system.

---

## Streamlit Dashboard

The project includes a Streamlit interface with:

* Chat-based querying
* Example questions
* Source display
* Source categories
* Rerank scores
* Semantic scores
* BM25 scores
* Qwen / Gemma model selector
* Hallucination test questions

Run:

```bash
streamlit run app.py
```

Then open:

```text
http://localhost:8501
```

---

## Project Structure

```text
Local_RAG_Robotics_Assistant/
│
├── data/
│   └── raw/
│
├── notebooks/
│   └── Local_Robotics_RAG_Learning_Notebook.ipynb
│
├── vector_db/
│   ├── robotics.index
│   └── chunks.json
│
├── src/
│   ├── document_loader.py
│   ├── text_splitter.py
│   ├── embeddings.py
│   ├── vector_store.py
│   ├── retriever.py
│   ├── reranker.py
│   ├── llm.py
│   └── rag_pipeline.py
│
├── evaluation_results/
│
├── app.py
├── ingest.py
├── search.py
├── chat.py
├── evaluate.py
├── evaluation_questions.json
├── requirements.txt
└── README.md
```

---

## Installation

Create and activate a virtual environment:

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Install Ollama and pull the final model:

```bash
ollama pull qwen3:1.7b
```

Build the vector database:

```bash
python ingest.py
```

Run the CLI assistant:

```bash
python chat.py
```

Or launch the web interface:

```bash
streamlit run app.py
```

---

## Tech Stack

```text
Python
Sentence Transformers
FAISS
BM25
CrossEncoder
Ollama
Qwen3
Gemma3
Streamlit
PyMuPDF
python-docx
BeautifulSoup
```

---

## Learning Notebook

The repository also contains a notebook explaining the project step-by-step:

```text
notebooks/Local_Robotics_RAG_Learning_Notebook.ipynb
```

It covers chunking, embeddings, FAISS, BM25, reranking, local LLM integration, evaluation, and model comparison.

The notebook is for learning and experimentation, while the modular Python files contain the actual application.

---

## Future Improvements

* Online deployment
* Hosted LLM fallback
* Document upload from the dashboard
* Larger evaluation dataset
* Metadata-based retrieval filtering
* Conversation-aware retrieval
* Jetson deployment
* Integration with the AMR

---

## Author

**Sourabh Warghane**

AI / Machine Learning / Robotics

GitHub:
https://github.com/sourabhwarghane

LinkedIn:
https://www.linkedin.com/in/sourabh-warghane/
