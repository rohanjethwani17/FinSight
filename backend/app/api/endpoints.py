"""API endpoints for FinSight."""
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from app.services.rag_engine import get_rag_engine
from app.core.config import get_settings


router = APIRouter()


# Request/Response Models
class ChatMessage(BaseModel):
    """A single chat message."""
    role: str = Field(..., description="Role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str = Field(..., description="User's query", min_length=1)
    ticker: str = Field(..., description="Stock ticker symbol (e.g., 'AAPL')")
    history: List[ChatMessage] = Field(default=[], description="Chat history")


class ContextChunk(BaseModel):
    """A retrieved context chunk."""
    id: str
    score: float
    text_content: str
    section_header: str
    source_url: str
    year: str


class ChatResponse(BaseModel):
    """Response model for non-streaming chat."""
    response: str
    contexts: List[ContextChunk]
    ticker: str


class FilingInfo(BaseModel):
    """Information about available filings."""
    ticker: str
    company_name: str
    available: bool


class FilingsResponse(BaseModel):
    """Response model for filings endpoint."""
    filings: List[FilingInfo]


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    service: str
    version: str


# Endpoints
@router.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        service="FinSight RAG API",
        version="1.0.0"
    )


@router.post("/chat", tags=["Chat"])
async def chat_stream(request: ChatRequest):
    """Chat endpoint with streaming response using Server-Sent Events.
    
    Returns a streaming response with:
    - First message: Retrieved contexts (type: "contexts")
    - Subsequent messages: Response tokens (type: "token")
    - Final message: Completion signal (type: "done")
    """
    settings = get_settings()
    
    # Validate ticker
    ticker = request.ticker.upper()
    if ticker not in settings.supported_tickers:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported ticker: {ticker}. Supported tickers: {settings.supported_tickers}"
        )
    
    # Validate API keys are configured
    if not settings.openai_api_key:
        raise HTTPException(
            status_code=500,
            detail="OpenAI API key not configured"
        )
    if not settings.pinecone_api_key:
        raise HTTPException(
            status_code=500,
            detail="Pinecone API key not configured"
        )
    
    # Convert history to dict format
    history = [msg.model_dump() for msg in request.history]
    
    # Get RAG engine and generate streaming response
    rag_engine = get_rag_engine()
    
    return StreamingResponse(
        rag_engine.generate_response_stream(
            query=request.message,
            ticker=ticker,
            history=history
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.post("/chat/sync", response_model=ChatResponse, tags=["Chat"])
async def chat_sync(request: ChatRequest):
    """Chat endpoint with non-streaming response (for testing/fallback)."""
    settings = get_settings()
    
    # Validate ticker
    ticker = request.ticker.upper()
    if ticker not in settings.supported_tickers:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported ticker: {ticker}. Supported tickers: {settings.supported_tickers}"
        )
    
    # Validate API keys
    if not settings.openai_api_key:
        raise HTTPException(
            status_code=500,
            detail="OpenAI API key not configured"
        )
    if not settings.pinecone_api_key:
        raise HTTPException(
            status_code=500,
            detail="Pinecone API key not configured"
        )
    
    # Convert history to dict format
    history = [msg.model_dump() for msg in request.history]
    
    # Get RAG engine and generate response
    rag_engine = get_rag_engine()
    result = await rag_engine.generate_response(
        query=request.message,
        ticker=ticker,
        history=history
    )
    
    return ChatResponse(
        response=result["response"],
        contexts=[ContextChunk(**ctx) for ctx in result["contexts"]],
        ticker=result["ticker"]
    )


@router.get("/filings", response_model=FilingsResponse, tags=["Filings"])
async def get_available_filings():
    """Get list of available SEC 10-K filings (supported tickers)."""
    settings = get_settings()
    
    # Company names mapping
    company_names = {
        "AAPL": "Apple Inc.",
        "MSFT": "Microsoft Corporation",
        "GOOGL": "Alphabet Inc.",
        "TSLA": "Tesla, Inc.",
        "NVDA": "NVIDIA Corporation",
        "AMZN": "Amazon.com, Inc."
    }
    
    filings = [
        FilingInfo(
            ticker=ticker,
            company_name=company_names.get(ticker, ticker),
            available=True  # Assumes data has been ingested
        )
        for ticker in settings.supported_tickers
    ]
    
    return FilingsResponse(filings=filings)


@router.get("/filings/{ticker}", tags=["Filings"])
async def get_filing_details(ticker: str):
    """Get details for a specific ticker's SEC 10-K filing."""
    settings = get_settings()
    ticker = ticker.upper()
    
    if ticker not in settings.supported_tickers:
        raise HTTPException(
            status_code=404,
            detail=f"Filing not found for ticker: {ticker}"
        )
    
    company_names = {
        "AAPL": "Apple Inc.",
        "MSFT": "Microsoft Corporation",
        "GOOGL": "Alphabet Inc.",
        "TSLA": "Tesla, Inc.",
        "NVDA": "NVIDIA Corporation",
        "AMZN": "Amazon.com, Inc."
    }
    
    return {
        "ticker": ticker,
        "company_name": company_names.get(ticker, ticker),
        "filing_type": "10-K",
        "sections": [
            "Business Overview",
            "Risk Factors",
            "Financial Data",
            "Management's Discussion and Analysis",
            "Market Risk Disclosures"
        ],
        "available": True
    }
