# 🏦 Intelligent Complaint Analysis for Financial Services

## 📌 Project Overview
CrediTrust Financial faces a critical challenge: thousands of customer complaints pour in monthly regarding Credit Cards, Loans, and Money Transfers. Manual analysis is slow and reactive.

This project implements a **Retrieval-Augmented Generation (RAG) Chatbot** that transforms this raw financial complaint data into actionable insights. It allows stakeholders to ask natural language questions (e.g., *"Why are customers unhappy with Credit Card fees?"*) and receive evidence-backed answers grounded in real customer narratives.

## 🚀 Key Features
*   **RAG Architecture**: Combines semantic search retrieval with generative AI.
*   **Scalable Ingestion**: Optimized pipeline (`ingest_parquet.py`) to handle 1.3M+ rows without memory crashes.
*   **Dual-Mode Operation**: 
    *   **Full Pipeline**: Runs deep analysis and evaluation.
    *   **Lite Mode**: A lightweight, memory-safe mock mode for UI demonstrations on restricted hardware.
*   **Interactive UI**: A polished chat interface built with **Streamlit**.
*   **Transparency**: Every answer cites specific Complaint IDs as evidence.

## 📂 Project Structure

```text
RAG-COMPLAINT-CHATBOT/
├── .github/                  # CI/CD Workflows
├── .vscode/                  # VS Code settings
├── data/
│   ├── raw/                  # Input: complaints.csv & complaint_embeddings.parquet
│   └── processed/            # Cleaned data: filtered_complaints.csv
├── notebooks/                # Development & Analysis
│   ├── 01_eda_preprocessing.ipynb  # Exploratory Data Analysis & Cleaning
│   ├── 02_chunking_embedding.ipynb # Vector store creation (Sampled)
│   └── 03_rag_evaluation.ipynb     # System evaluation metrics
├── src/                      # Core Logic Modules
│   ├── __init__.py
│   ├── data_loader.py        # Data loading & PII scrubbing logic
│   ├── ingest_parquet.py     # Memory-optimized ingestion for full dataset
│   ├── rag_pipeline.py       # Full RAG logic (Retriever + LLM)
│   ├── rag_pipeline_lite.py  # Lightweight mock service for low-RAM demos
│   └── utils.py              # Helper utilities
├── tests/                    # Unit tests
├── vector_store/             # Sample Vector Database (from Notebook 2)
├── vector_store_full/        # Full Vector Database (from ingest_parquet.py)
├── app.py                    # Streamlit Application
├── requirements.txt          # Python dependencies
└── README.md                 # Project documentation
```

---

## 🛠️ Installation & Setup

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd RAG-COMPLAINT-CHATBOT
```

### 2. Create a Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Data Setup
1.  Download the **CFPB Complaint Dataset**.
2.  Place `complaints.csv` and `complaint_embeddings.parquet` in the `data/raw/` directory.

---

## 📝 Workflow & Usage

### Step 1: Preprocessing & EDA
Run the notebook to analyze the data and filter for the 5 key products (Credit Cards, Loans, etc.).
*   **Notebook:** `notebooks/01_eda_preprocessing.ipynb`
*   **Output:** `data/processed/filtered_complaints.csv`

### Step 2: Ingestion (Building the Knowledge Base)
To handle the massive dataset without crashing RAM, we use a streaming ingestion script.
```bash
python src/ingest_parquet.py
```
*   **Output:** Creates the `vector_store_full/` directory containing the ChromaDB index.

### Step 3: Launch the Chatbot
Start the Streamlit web interface to interact with the financial data.
```bash
streamlit run app.py
```
*   The app will open at `http://localhost:8501`.
*   **Note:** If running on low-memory hardware, the app automatically uses `rag_pipeline_lite.py` to ensure stability while demonstrating functionality.

---

## 📊 System Evaluation
The RAG pipeline was evaluated using a set of strategic business questions.

| Question Category | Performance | Observation |
| :--- | :--- | :--- |
| **Broad Trends** | ⭐⭐⭐⭐ | Successfully identifies high-level issues like "Fraud" and "Late Fees". |
| **Specific Features** | ⭐⭐⭐⭐⭐ | Excellent retrieval for specific terms like "Overdraft protection". |
| **Customer Sentiment** | ⭐⭐⭐ | Accurately reflects the negative sentiment inherent in complaint data. |

---

## ⚙️ Technical Details
*   **LLM:** `google/flan-t5-small` (Optimized for local CPU inference).
*   **Embeddings:** `sentence-transformers/all-MiniLM-L6-v2`.
*   **Vector DB:** ChromaDB.
*   **Framework:** LangChain & Streamlit.

## 👥 Contributors
*   **Adem Mekonnen** - Data & AI Engineer

## 📜 License
This project is for educational purposes as part of the 10Academy AI Engineering Challenge.
```