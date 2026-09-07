# Local Robotics RAG Assistant

A local **Retrieval-Augmented Generation (RAG)** assistant built around robotics documentation and my ROS 2 Autonomous Mobile Robot (AMR) project.

The system combines **FAISS semantic search, BM25 keyword retrieval, CrossEncoder reranking, and a local LLM through Ollama** to generate grounded technical answers with source references.

The final application includes an interactive **Streamlit dashboard** and uses **Qwen3 1.7B** as the primary local LLM.

---

## ✨ Features

- Fully local RAG pipeline
- Multi-format document ingestion
- FAISS semantic retrieval
- BM25 keyword retrieval
- Hybrid search
- CrossEncoder reranking
- Question-only chunk filtering
- Local LLM inference with Ollama
- Source-aware answers
- Streamlit chat interface
- Retrieval score inspection
- Hallucination / refusal testing
- Automated model evaluation

---

## 🧠 Architecture

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

## 📚 Knowledge Base

The knowledge base used during development contains documentation related to:

- Autonomous Mobile Robot architecture
- ROS 2 Humble
- NVIDIA Jetson Orin Nano
- SLAMTEC RPLIDAR C1
- ESP32-C3
- IMX219 camera
- BTS7960 motor driver
- Audio hardware

Development dataset:

```text
Source files         : 22
Document sections    : 223
Extracted text       : ~555,000 characters
Chunks               : ~939
Embedding dimension  : 384
```

Third-party documentation and datasheets are not committed directly to this repository. See [`data/README.md`](data/README.md) for the expected folder structure and [`tools/document_downloader/`](tools/document_downloader/) for the document downloader and source manifest.

---

## 🔍 Retrieval Pipeline

The system uses a hybrid retrieval strategy.

### FAISS

FAISS is used for **semantic similarity**, allowing the system to retrieve relevant passages even when the question and document use different wording.

### BM25

BM25 complements semantic retrieval by matching exact technical terms such as:

```text
RPLIDAR C1
BEST_EFFORT
TensorRT
ESP32-C3
12 meters
```

### CrossEncoder Reranking

Candidates retrieved by FAISS and BM25 are reranked using:

```text
cross-encoder/ms-marco-MiniLM-L6-v2
```

This improved technical retrieval in cases where semantic search found the correct document but did not initially rank the most useful passage first.

---

## 🦙 Local LLM

Primary model:

```text
Qwen3 1.7B
```

served locally through:

```text
Ollama
```

Configuration:

```text
Temperature : 0
Context     : 2048
Top Context : 3 chunks
```

If the retrieved knowledge base does not contain enough information, the assistant is instructed to respond:

```text
I do not have enough information in the knowledge base to answer that.
```

---

## 📊 Evaluation

The system was evaluated using:

```text
12 answerable questions
3 intentionally unanswerable questions
```

### Model Comparison

| Metric | Qwen3 1.7B | Gemma3 1B |
|---|---:|---:|
| Automatic score | **93.3%** | 66.7% |
| Passed | **14/15** | 10/15 |
| Retrieval source hits | **12/12** | **12/12** |
| Correct refusals | **3/3** | 0/3 |
| Final choice | ✅ Qwen3 1.7B | Comparison |

Both models achieved **12/12 correct source retrievals**, showing that retrieval quality and generation quality are separate parts of the RAG system.

Qwen3 1.7B was selected as the final model because it provided better overall answer quality and refusal behavior.

---

## 🖥️ Streamlit Dashboard

The Streamlit interface includes:

- Chat-based querying
- Example questions
- Source display
- Source categories
- Rerank scores
- Semantic scores
- BM25 scores
- Qwen / Gemma model selector
- Hallucination test questions

Run:

```powershell
streamlit run app.py
```

Then open:

```text
http://localhost:8501
```

---

## 📁 Project Structure

```text
Local-Robotics-RAG-Assistant/
│
├── data/
│   ├── README.md
│   └── raw/
│       ├── amr/
│       ├── ros2/
│       ├── sensors/
│       ├── jetson/
│       ├── esp32_c3/
│       ├── motor_driver/
│       └── audio/
│
├── tools/
│   └── document_downloader/
│       ├── download_hardware_and_ros2_docs.ps1
│       ├── README.md
│       └── source_manifest.csv
│
├── notebooks/
│   └── Local_Robotics_RAG_Learning_Notebook.ipynb
│
├── src/
│   ├── __init__.py
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
│   ├── qwen3_1.7b_results.csv
│   └── gemma3_1b_results.csv
│
├── .streamlit/
│   └── config.toml
│
├── app.py
├── ingest.py
├── search.py
├── chat.py
├── evaluate.py
├── evaluation_questions.json
├── requirements.txt
├── .gitignore
└── README.md
```

The generated FAISS index and chunk metadata are created inside `vector_db/` after running the ingestion pipeline and do not need to be committed to GitHub.

---

## ⚙️ Installation

### 1. Clone the repository

```powershell
git clone https://github.com/sourabhwarghane/Local-Robotics-RAG-Assistant.git
cd Local-Robotics-RAG-Assistant
```

### 2. Create a virtual environment

```powershell
python -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\activate
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

### 4. Install the local LLM

Install Ollama and pull Qwen3 1.7B:

```powershell
ollama pull qwen3:1.7b
```

Optional comparison model:

```powershell
ollama pull gemma3:1b
```

### 5. Prepare the knowledge base

Place supported documents inside the appropriate folders under:

```text
data/raw/
```

Third-party robotics and hardware documentation can also be obtained using the resources provided in:

```text
tools/document_downloader/
```

See its README for details.

### 6. Build the vector database

```powershell
python ingest.py
```

This creates the FAISS index and chunk metadata inside:

```text
vector_db/
```

### 7. Run the assistant

CLI:

```powershell
python chat.py
```

Streamlit dashboard:

```powershell
streamlit run app.py
```

---

## 🛠️ Tech Stack

- Python
- Sentence Transformers
- FAISS
- BM25
- CrossEncoder
- Ollama
- Qwen3
- Gemma3
- Streamlit
- PyMuPDF
- python-docx
- BeautifulSoup

---

## 📓 Learning Notebook

The repository includes:

```text
notebooks/Local_Robotics_RAG_Learning_Notebook.ipynb
```

The notebook explains the project step-by-step, including:

- document ingestion
- chunking
- embeddings
- FAISS
- BM25
- hybrid retrieval
- CrossEncoder reranking
- local LLM integration
- hallucination testing
- evaluation
- model comparison

The notebook is intended for learning and experimentation, while the modular Python files contain the actual application.

---

## 🚀 Future Improvements

- Online deployment
- Hosted LLM fallback
- Document upload from the dashboard
- Metadata-based retrieval filtering
- Conversation-aware retrieval
- Larger evaluation dataset
- NVIDIA Jetson deployment
- Integration with the AMR

---

## 👤 Author

**Sourabh Warghane**

AI / Machine Learning / Robotics

**GitHub:**  
https://github.com/sourabhwarghane

**LinkedIn:**  
https://www.linkedin.com/in/sourabh-warghane/