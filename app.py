import os
import glob
import gradio as gr
import numpy as np
from dotenv import load_dotenv
from openai import OpenAI
from sentence_transformers import SentenceTransformer
import faiss
from pypdf import PdfReader

# -----------------------------
# Load environment variables
# -----------------------------
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = "gpt-4o-mini"

# -----------------------------
# Embedding model
# -----------------------------
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# -----------------------------
# Global storage
# -----------------------------
document_chunks = []
chunk_sources = []
uploaded_pdfs = []

# -----------------------------
# Chunk text
# -----------------------------
def chunk_text(text, source, chunk_size=500):

    chunks = []
    sources = []

    for i in range(0, len(text), chunk_size):

        chunks.append(text[i:i + chunk_size])
        sources.append(source)

    return chunks, sources


# -----------------------------
# Load markdown documents
# -----------------------------
def load_documents():

    base_path = "knowledge_base"

    for section in os.listdir(base_path):

        section_path = os.path.join(base_path, section)

        if not os.path.isdir(section_path):
            continue

        for file_path in glob.glob(f"{section_path}/*.md"):

            with open(file_path, "r", encoding="utf-8") as f:

                text = f.read()

                chunks, sources = chunk_text(text, file_path)

                document_chunks.extend(chunks)
                chunk_sources.extend(sources)


# -----------------------------
# Load knowledge base
# -----------------------------
load_documents()

# -----------------------------
# Create embeddings + FAISS
# -----------------------------
embeddings = embedding_model.encode(document_chunks)

dimension = len(embeddings[0])

index = faiss.IndexFlatL2(dimension)

index.add(np.array(embeddings))


# -----------------------------
# Retrieve context (UPDATED)
# -----------------------------
def retrieve_context(query, k=5, pdf_only=False):

    query_embedding = embedding_model.encode([query])

    distances, indices = index.search(np.array(query_embedding), k)

    contexts = []
    sources = []
    scores = []

    for i, d in zip(indices[0], distances[0]):

        src = chunk_sources[i]

        # If PDF only search required
        if pdf_only and not src.endswith(".pdf"):
            continue

        contexts.append(document_chunks[i])
        sources.append(src)

        score = 1 / (1 + d)
        scores.append(round(score, 3))

    return contexts, sources, scores


# -----------------------------
# Read PDF
# -----------------------------
def read_pdf(file):

    reader = PdfReader(file)

    text = ""

    for page in reader.pages:
        text += page.extract_text()

    return text


# -----------------------------
# Upload PDF
# -----------------------------
def upload_pdf(file):

    global uploaded_pdfs

    text = read_pdf(file.name)

    chunks, sources = chunk_text(text, file.name)

    new_embeddings = embedding_model.encode(chunks)

    index.add(np.array(new_embeddings))

    document_chunks.extend(chunks)
    chunk_sources.extend(sources)

    uploaded_pdfs.append(file.name)

    return "PDF successfully added to knowledge base"


# -----------------------------
# Chat function
# -----------------------------
def chat(user_message, history):

    pdf_keywords = [
        "pdf",
        "uploaded pdf",
        "uploaded document",
        "this pdf"
    ]

    pdf_question = any(k in user_message.lower() for k in pdf_keywords)

    # -----------------------------
    # PDF guard
    # -----------------------------
    if pdf_question and len(uploaded_pdfs) == 0:
        return "No uploaded document found. Please upload a PDF first."

    # -----------------------------
    # Retrieval routing
    # -----------------------------
    if pdf_question:
        contexts, sources, scores = retrieve_context(
            user_message,
            pdf_only=True
        )
    else:
        contexts, sources, scores = retrieve_context(user_message)

    context_text = "\n\n".join(contexts)

    messages = [
        {
            "role": "system",
            "content": (
                "You are an AI assistant for Insurellm employees. "
                "Answer ONLY using the provided documents."
            ),
        }
    ]

    # -----------------------------
    # Chat memory
    # -----------------------------
    for message in history:

        if message["role"] == "user":
            messages.append(
                {"role": "user", "content": message["content"]}
            )

        elif message["role"] == "assistant":
            messages.append(
                {"role": "assistant", "content": message["content"]}
            )

    messages.append({
        "role": "user",
        "content": f"""
Question:
{user_message}

Relevant documents:
{context_text}
"""
    })

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages
    )

    answer = response.choices[0].message.content

    # -----------------------------
    # Snippet preview
    # -----------------------------
    if len(contexts) > 0:

        snippet = contexts[0][:200]

        answer += "\n\nRelevant snippet:\n" + snippet

    # -----------------------------
    # Retrieval scores
    # -----------------------------
    answer += "\n\nRetrieval Scores:\n"

    for src, sc in zip(sources, scores):

        answer += f"{os.path.basename(src)} (score: {sc})\n"

    return answer


# -----------------------------
# Gradio UI
# -----------------------------
with gr.Blocks() as demo:

    gr.Markdown("# 🤖 Insurellm AI Knowledge Assistant")

    chatbot = gr.ChatInterface(chat)

    gr.Markdown("### Upload PDF to Knowledge Base")

    pdf_file = gr.File(file_types=[".pdf"])

    upload_btn = gr.Button("Upload PDF")

    status = gr.Textbox(label="Status")

    upload_btn.click(upload_pdf, inputs=pdf_file, outputs=status)


# -----------------------------
# Launch app
# -----------------------------
demo.launch()