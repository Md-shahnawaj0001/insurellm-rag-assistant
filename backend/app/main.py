from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.routes import chat, upload, reset, history, documents, auth
from backend.app.db.database import engine, Base
from backend.app.db import models

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="InsureLLM Backend",
    version="1.0.0"
)

# CORS FIX
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)
app.include_router(upload.router)
app.include_router(reset.router)
app.include_router(history.router)
app.include_router(documents.router)
app.include_router(auth.router)


@app.get("/")
def home():
    return {
        "message": "FastAPI backend is running"
    }