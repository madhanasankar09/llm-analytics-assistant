#  LLM-Powered Analytics Assistant with RAG

##  Project Overview
This project is an AI-powered analytics assistant that allows users to ask natural language questions and get insights from structured (SQL) and unstructured (customer reviews) data.

It combines:
- Natural Language to SQL
- Retrieval-Augmented Generation (RAG)
- Sentiment Analysis
- Interactive Visualization

---

##  Key Features

### 1.  Natural Language to SQL
- Converts user queries into SQL
- Executes queries on SQLite database
- Returns results with explanations

### 2.  RAG Pipeline
- Retrieves relevant customer reviews
- Uses TF-IDF embeddings + cosine similarity
- Provides contextual insights

### 3.  Sentiment Analysis
- Classifies customer feedback into:
  - Positive
  - Negative
  - Mixed

### 4.  Issue Detection
- Identifies key problems:
  - Delivery Delay
  - Product Issues
  - Cancellation Issues

### 5.  Query Routing
- Automatically detects query type:
  - SQL → structured data
  - RAG → review analysis

### 6.  Auto Visualization
- Generates charts using Plotly
- Displays aggregated insights clearly

---

##  Project Structure


rag/
embedder.py
retriever.py

sql/
nl_to_sql.py

app.py
olist.db


##  Technologies Used

- Python
- Streamlit
- SQLite
- Pandas
- Scikit-learn (TF-IDF)
- Plotly

---

## ▶️ How to Run

### 1. Install dependencies
```bash
python -m pip install streamlit pandas scikit-learn plotly
