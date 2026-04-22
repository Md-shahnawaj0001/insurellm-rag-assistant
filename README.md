## 🚀 InsureLLM RAG Assistant

An AI-powered assistant that uses Retrieval-Augmented Generation (RAG) 
to answer user queries based on a custom knowledge base.

## 🔧 Features
- Semantic search using embeddings
- Document-based question answering
- PDF knowledge ingestion
- Chat interface using Gradio

## ⚙️ How it works
1. Documents are converted into embeddings
2. Stored in FAISS vector database
3. User query is embedded
4. Top relevant chunks retrieved
5. Passed to LLM (OpenAI) for final answer

## 🛠 Tech Stack
- Python
- OpenAI API
- FAISS
- Sentence Transformers
- Gradio

## ▶️ Run locally
pip install -r requirements.txt  
python app.py
