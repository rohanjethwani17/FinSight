"""Main FastAPI application entry point for FinSight."""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from app.api.endpoints import router as api_router
from app.core.config import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    settings = get_settings()
    print("Starting FinSight RAG API...")
    print(f"Supported tickers: {settings.supported_tickers}")
    print(f"Pinecone index: {settings.pinecone_index_name}")
    print(f"OpenAI model: {settings.openai_chat_model}")
    
    # Validate critical settings
    if not settings.openai_api_key:
        print("WARNING: OPENAI_API_KEY not set!")
    if not settings.pinecone_api_key:
        print("WARNING: PINECONE_API_KEY not set!")
    
    yield
    
    # Shutdown
    print("Shutting down FinSight RAG API...")


# Create FastAPI application
app = FastAPI(
    title="FinSight RAG API",
    description="High-frequency trading grade RAG platform for SEC 10-K filings analysis",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Include API routes with /api prefix
app.include_router(api_router, prefix="/api")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "FinSight RAG API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/api/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
