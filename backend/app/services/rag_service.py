from app.db.database import SessionLocal
from app.db.models import ChatSession, Message, Document

import os
import glob
import uuid

from app.services.embedding_service import get_embeddings
from app.services.vector_store import collection
from app.services.pdf_service import read_pdf
from app.services.llm_service import (
    generate_response,
    generate_chat_title
)


def chunk_text(text, source, chunk_size=1000, overlap=200):
    chunks = []
    sources = []

    if not text or not text.strip():
        return chunks, sources

    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)
            sources.append(source)

        start += (chunk_size - overlap)

    return chunks, sources


def load_documents():

    base_path = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "../../../knowledge_base"
        )
    )

    print("LOADING FROM =", base_path)
    print("EXISTS =", os.path.exists(base_path))

    if not os.path.exists(base_path):
        print("Knowledge base folder not found!")
        return

    for section in os.listdir(base_path):
        section_path = os.path.join(base_path, section)

        if not os.path.isdir(section_path):
            continue

        for file_path in glob.glob(f"{section_path}/*.md"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    text = f.read()

                chunks, _ = chunk_text(
                    text,
                    file_path
                )

                if chunks:
                    embeddings = get_embeddings(chunks)

                    ids = [
                        str(uuid.uuid4())
                        for _ in chunks
                    ]

                    collection.add(
                        ids=ids,
                        documents=chunks,
                        embeddings=embeddings.tolist(),
                        metadatas=[
                            {
                                "user_id": 0,
                                "source": file_path
                            }
                            for _ in chunks
                        ]
                    )

            except Exception as e:
                print(f"Error loading docs: {e}")


def retrieve_context(
    query,
    user_id,
    k=5,
    pdf_only=False
):
    try:
        query_embedding = get_embeddings([query])

        results = collection.query(
            query_embeddings=query_embedding.tolist(),
            n_results=20
        )

        documents = results["documents"][0]
        metadatas = results["metadatas"][0]

        contexts = []
        sources = []
        scores = []

        for doc, meta in zip(documents, metadatas):

            source = meta.get("source", "")
            doc_user_id = meta.get("user_id")

            # Allow:
            # 1. Global knowledge base docs
            # 2. Current user's uploaded PDFs
            # Block:
            # Other users' documents

            if (
                doc_user_id != user_id
                and doc_user_id != 0
            ):
                continue

            if (
                pdf_only
                and not source.lower().endswith(".pdf")
            ):
                continue

            contexts.append(doc)
            sources.append(source)
            scores.append(1.0)

            if len(contexts) >= k:
                break

        return contexts, sources, scores

    except Exception as e:
        print(f"Retrieve error: {e}")

        return [], [], []


def upload_pdf(file, user_id):
    try:
        text = read_pdf(file.file)

        if not text or not text.strip():
            return {
                "message": "Could not read PDF content."
            }

        chunks, sources = chunk_text(
            text,
            file.filename
        )

        if not chunks:
            return {
                "message": "No readable content found."
            }

        embeddings = get_embeddings(chunks)

        ids = [
            str(uuid.uuid4())
            for _ in chunks
        ]

        collection.add(
            ids=ids,
            documents=chunks,
            embeddings=embeddings.tolist(),
            metadatas=[
                {
                    "user_id": user_id,
                    "source": file.filename
                }
                for _ in chunks
            ]
        )

        db = SessionLocal()

        document = Document(
            user_id=user_id,
            filename=file.filename,
            chunk_count=len(chunks)
        )

        db.add(document)

        db.commit()
        db.close()

        return {
            "message": "PDF successfully added to knowledge base"
        }

    except Exception as e:
        print(f"Upload PDF error: {e}")

        return {
            "message": "Failed to upload PDF"
        }


def chat(
    user_message,
    history=None,
    user_id=None,
    session_id=None
):
    if history is None:
        history = []

    if not user_message or not user_message.strip():
        return {
            "response": "Please enter a valid message."
        }

    pdf_keywords = [
        "pdf",
        "uploaded pdf",
        "document",
        "uploaded file",
        "summarize",
        "summary"
    ]

    pdf_question = any(
        k in user_message.lower()
        for k in pdf_keywords
    )

    if pdf_question:

        db = SessionLocal()

        uploaded_docs = db.query(Document).filter(
            Document.user_id == user_id
        ).all()

        db.close()

        if not uploaded_docs:
            return {
                "response": "No PDF has been uploaded yet. Please upload a PDF first.",
                "sources": []
            }

        contexts, sources, scores = retrieve_context(
            user_message,
            user_id,
            pdf_only=True
        )

        if len(contexts) == 0:
            return {
                "response": "No PDF content was found for your uploaded documents.",
                "sources": []
            }

    else:

        contexts, sources, scores = retrieve_context(
            user_message,
            user_id
        )

        if len(contexts) == 0:
            return {
                "response": "No relevant documents found."
            }

    context_text = "\n\n".join(contexts)

    messages = [
        {
            "role": "system",
            "content": """
You are an AI assistant for InsureLLM.

ONLY answer from provided context.
"""
        }
    ]

    for msg in history:
        if isinstance(msg, dict):
            messages.append(msg)

    messages.append({
        "role": "user",
        "content": f"""
DOCUMENT CONTEXT:
{context_text}

QUESTION:
{user_message}
"""
    })

    try:
        answer = generate_response(messages)

        if isinstance(answer, dict):
            answer = answer.get(
                "response",
                str(answer)
            )

        db = SessionLocal()

        # Existing chat
        if session_id:

            session = db.query(ChatSession).filter(
                ChatSession.id == session_id,
                ChatSession.user_id == user_id
            ).first()

            if not session:
                db.close()

                return {
                    "response": "Chat session not found."
                }

        # New chat
        else:

            smart_title = generate_chat_title(
                user_message
            )

            session = ChatSession(
                user_id=user_id,
                title=smart_title
            )

            db.add(session)
            db.commit()
            db.refresh(session)

        # Save user message
        db.add(Message(
            session_id=session.id,
            role="user",
            content=user_message
        ))

        # Save AI response
        db.add(Message(
            session_id=session.id,
            role="assistant",
            content=answer
        ))

        chat_session_id = session.id

        db.commit()
        db.close()

        unique_sources = list(set(sources))

        return {
            "response": answer,
            "sources": unique_sources,
            "session_id": chat_session_id
        }

    except Exception as e:
        print(f"Chat error: {e}")

        return {
            "response": "Something went wrong."
        }


if collection.count() == 0:
    load_documents()

print("DOC COUNT =", collection.count())