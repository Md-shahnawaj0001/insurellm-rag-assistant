from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import (
    chat,
    upload,
    reset,
    history,
    documents,
    auth
)

from app.db.database import engine, Base
from app.db import models

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="InsureLLM Backend",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
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