---
title: InsureLLM RAG Assistant
emoji: 🚀
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 7860
---



# 🛡️ InsureLLM – AI-Powered Insurance RAG Assistant

## Overview

InsureLLM is a full-stack AI-powered Retrieval-Augmented Generation (RAG) application designed for the insurance domain. The system combines a structured insurance knowledge base with user-uploaded PDF documents to provide accurate, contextual, and source-backed responses.

The platform enables users to interact with insurance-related information through a conversational interface powered by semantic search, vector embeddings, and Large Language Models (LLMs).

---

## Features

### Authentication & User Management

* Secure User Signup and Login
* JWT-based Authentication
* Protected Routes
* User-specific Chat Sessions

### Knowledge Base Question Answering

* Company Information Retrieval
* Employee Information Lookup
* Insurance Product Information
* Contract and Agreement Search
* Semantic Search using Vector Embeddings

### PDF Document Intelligence

* Upload PDF Documents
* Automatic Text Extraction
* Intelligent Document Chunking
* Embedding Generation
* Contextual Question Answering over Uploaded PDFs
* User-specific Document Isolation

### AI Chat System

* Retrieval-Augmented Generation (RAG)
* Context-Aware Responses
* Conversation History Management
* AI-Generated Chat Titles
* Source Attribution for Responses
* Multi-Session Chat Support

### Document Management

* Uploaded Document Tracking
* Document History
* Source Reference Display
* PDF-based Knowledge Retrieval

### Export Functionality

* Export Chat Conversations as PDF
* Preserve Chat History for Future Reference

---

## Project Architecture

```text
User Query
      │
      ▼
FastAPI Backend
      │
      ▼
Query Classification
      │
      ├── Knowledge Base Search
      │         │
      │         ▼
      │     ChromaDB
      │
      └── PDF Search
                │
                ▼
           ChromaDB
                │
                ▼
          Relevant Context
                │
                ▼
           LLM Response
                │
                ▼
             Frontend
```

---

## Tech Stack

### Frontend

* React.js
* Vite
* JavaScript
* HTML
* CSS

### Backend

* FastAPI
* SQLAlchemy
* JWT Authentication
* Python

### AI & Machine Learning

* Retrieval-Augmented Generation (RAG)
* Sentence Transformers
* Semantic Search
* Vector Embeddings

### Vector Database

* ChromaDB

### Database

* SQLite

### Deployment

* Render
* Hugging Face Spaces (Optional)

---

## Project Structure

```text
insurellm-rag-assistant/
│
├── backend/
│   ├── app/
│   │   ├── routes/
│   │   ├── services/
│   │   ├── models/
│   │   ├── db/
│   │   ├── dependencies/
│   │   └── main.py
│
├── frontend/
│   ├── src/
│   ├── public/
│   └── package.json
│
├── knowledge_base/
│   ├── company/
│   ├── employees/
│   ├── products/
│   └── contracts/
│
├── chroma_db/
├── requirements.txt
└── README.md
```

---

## Knowledge Base Categories

### Company

* About InsureLLM
* Company Overview
* Careers Information

### Employees

* Employee Profiles
* Roles and Responsibilities

### Products

* PolicyLLM
* ClaimsLLM
* FraudLLM
* HomeLLM
* CarLLM
* ReLLM

### Contracts

* Insurance Partnerships
* Business Agreements
* Customer Contracts

---

## How It Works

### Knowledge Base Queries

Example:

```text
Tell me about InsureLLM
```

```text
Who is Emily Wright?
```

```text
What products does InsureLLM provide?
```

The system retrieves relevant information from the structured knowledge base and generates contextual responses.

---

### PDF Queries

Upload a PDF and ask:

```text
Summarize this document
```

```text
What are the key points in the uploaded PDF?
```

The system extracts text, creates embeddings, retrieves relevant chunks, and generates answers based on the uploaded document.

---

## Installation

### Clone Repository

```bash
git clone https://github.com/Md-shahnawaj0001/insurellm-rag-assistant.git
cd insurellm-rag-assistant
```

### Create Virtual Environment

```bash
python -m venv .venv
```

### Activate Environment

Windows:

```bash
.venv\Scripts\activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Run Backend

```bash
cd backend
uvicorn app.main:app --reload
```

Backend URL:

```text
http://127.0.0.1:8000
```

---

## Run Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend URL:

```text
http://localhost:5173
```

---

## Future Enhancements

* Multi-PDF Querying
* Streaming Responses
* Role-Based Access Control
* PostgreSQL Integration
* Cloud Storage Integration
* Advanced Document Analytics
* Hybrid Search (Keyword + Semantic Search)

---

## Author

**MD Shahnawaj**

* GitHub: https://github.com/Md-shahnawaj0001
* LinkedIn: Add Your LinkedIn Profile Here

---

## License

This project is developed for educational, research, and portfolio purposes.