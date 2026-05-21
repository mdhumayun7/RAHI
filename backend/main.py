"""
RAHI FastAPI Backend
=====================
Main application entry point.

Run with:
    uvicorn backend.main:app --reload --port 8000

Then visit:
    http://localhost:8000/docs  ← Auto-generated API docs
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from backend.routers import chat, users, memory, health


# ── Lifespan (startup + shutdown) ────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Runs on startup and shutdown."""
    print("🚀 RAHI Backend starting...")
    print("📦 Loading embedding model...")

    # Pre-load embedding model so first request isn't slow
    from memory.embeddings import get_model
    get_model()

    print("✅ RAHI Backend ready!")
    print("📖 API docs: http://localhost:8000/docs")
    yield
    print("👋 RAHI Backend shutting down...")


# ── App Setup ─────────────────────────────────────────────────────────────────
app = FastAPI(
    title="RAHI API",
    description="Responsive Autonomous Human-like Intelligent Interface — API",
    version="0.1.0",
    lifespan=lifespan,
)

# Allow frontend (Next.js) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register Routers ──────────────────────────────────────────────────────────
app.include_router(health.router,  prefix="/health",  tags=["Health"])
app.include_router(users.router,   prefix="/users",   tags=["Users"])
app.include_router(chat.router,    prefix="/chat",    tags=["Chat"])
app.include_router(memory.router,  prefix="/memory",  tags=["Memory"])


@app.get("/")
async def root():
    return {
        "message": "RAHI is online",
        "version": "0.1.0",
        "docs":    "http://localhost:8000/docs"
    }