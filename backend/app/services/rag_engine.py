"""RAG Engine for FinSight - Handles retrieval and generation."""
import json
from typing import AsyncGenerator, List, Dict, Any, Optional
from pinecone import Pinecone
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from app.core.config import get_settings


class RAGEngine:
    """Retrieval-Augmented Generation engine for SEC 10-K filings."""
    
    def __init__(self):
        self.settings = get_settings()
        self._pinecone_client: Optional[Pinecone] = None
        self._index = None
        self._embeddings: Optional[OpenAIEmbeddings] = None
        self._llm: Optional[ChatOpenAI] = None
    
    def _get_pinecone_client(self) -> Pinecone:
        """Initialize Pinecone client lazily."""
        if self._pinecone_client is None:
            self._pinecone_client = Pinecone(api_key=self.settings.pinecone_api_key)
        return self._pinecone_client
    
    def _get_index(self):
        """Get Pinecone index lazily."""
        if self._index is None:
            pc = self._get_pinecone_client()
            self._index = pc.Index(self.settings.pinecone_index_name)
        return self._index
    
    def _get_embeddings(self) -> OpenAIEmbeddings:
        """Initialize OpenAI embeddings lazily."""
        if self._embeddings is None:
            self._embeddings = OpenAIEmbeddings(
                model=self.settings.openai_embedding_model,
                openai_api_key=self.settings.openai_api_key
            )
        return self._embeddings
    
    def _get_llm(self) -> ChatOpenAI:
        """Initialize ChatOpenAI lazily."""
        if self._llm is None:
            self._llm = ChatOpenAI(
                model=self.settings.openai_chat_model,
                openai_api_key=self.settings.openai_api_key,
                temperature=0.1,
                streaming=True
            )
        return self._llm
    
    async def embed_query(self, query: str) -> List[float]:
        """Embed a query string using OpenAI embeddings."""
        embeddings = self._get_embeddings()
        return await embeddings.aembed_query(query)
    
    async def retrieve_context(
        self, 
        query: str, 
        ticker: str, 
        top_k: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve relevant context from Pinecone for a given query and ticker."""
        if top_k is None:
            top_k = self.settings.top_k_results
        
        # Embed the query
        query_embedding = await self.embed_query(query)
        
        # Query Pinecone with the ticker as namespace
        index = self._get_index()
        results = index.query(
            vector=query_embedding,
            namespace=ticker.upper(),
            top_k=top_k,
            include_metadata=True
        )
        
        # Format results
        contexts = []
        for match in results.get("matches", []):
            metadata = match.get("metadata", {})
            contexts.append({
                "id": match.get("id", ""),
                "score": match.get("score", 0.0),
                "text_content": metadata.get("text_content", ""),
                "section_header": metadata.get("section_header", "Unknown Section"),
                "source_url": metadata.get("source_url", ""),
                "year": metadata.get("year", "")
            })
        
        return contexts
    
    def _build_system_prompt(self, contexts: List[Dict[str, Any]], ticker: str) -> str:
        """Build the system prompt with retrieved context."""
        context_text = "\n\n".join([
            f"[Source: {ctx['section_header']} | Year: {ctx['year']}]\n{ctx['text_content']}"
            for ctx in contexts
        ])
        
        return f"""You are a senior financial analyst specializing in SEC 10-K filings analysis for {ticker}.

Your task is to provide accurate, insightful analysis based ONLY on the provided context from official SEC filings.

## CRITICAL RULES:
1. Answer based ONLY on the context provided below. Do not use external knowledge.
2. You MUST cite the 'section_header' (e.g., "Risk Factors", "Business Overview") for EVERY claim you make.
3. Use citation format: [Section: Risk Factors, 2023]
4. If the context doesn't contain enough information to answer, say "Based on the available SEC filings, I don't have sufficient information to answer this question."
5. Be precise with financial figures and dates.
6. Maintain a professional, analytical tone appropriate for institutional investors.

## CONTEXT FROM SEC 10-K FILINGS:
{context_text}

## RESPONSE FORMAT:
- Start with a direct answer to the question
- Support each point with citations from the context
- If relevant, highlight key risks or opportunities
- Keep responses concise but comprehensive"""
    
    def _format_chat_history(
        self, 
        history: List[Dict[str, str]]
    ) -> List[Any]:
        """Convert chat history to LangChain message format."""
        messages = []
        for msg in history:
            role = msg.get("role", "")
            content = msg.get("content", "")
            if role == "user":
                messages.append(HumanMessage(content=content))
            elif role == "assistant":
                messages.append(AIMessage(content=content))
        return messages
    
    async def generate_response_stream(
        self,
        query: str,
        ticker: str,
        history: Optional[List[Dict[str, str]]] = None
    ) -> AsyncGenerator[str, None]:
        """Generate a streaming response for the given query."""
        if history is None:
            history = []
        
        # Retrieve relevant context
        contexts = await self.retrieve_context(query, ticker)
        
        # Build messages
        system_prompt = self._build_system_prompt(contexts, ticker)
        messages = [SystemMessage(content=system_prompt)]
        
        # Add chat history
        messages.extend(self._format_chat_history(history))
        
        # Add current query
        messages.append(HumanMessage(content=query))
        
        # First yield the contexts as metadata
        yield json.dumps({"type": "contexts", "data": contexts}) + "\n"
        
        # Stream the response
        llm = self._get_llm()
        async for chunk in llm.astream(messages):
            if chunk.content:
                yield json.dumps({"type": "token", "data": chunk.content}) + "\n"
        
        # Signal completion
        yield json.dumps({"type": "done"}) + "\n"
    
    async def generate_response(
        self,
        query: str,
        ticker: str,
        history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """Generate a non-streaming response (for testing/fallback)."""
        if history is None:
            history = []
        
        # Retrieve relevant context
        contexts = await self.retrieve_context(query, ticker)
        
        # Build messages
        system_prompt = self._build_system_prompt(contexts, ticker)
        messages = [SystemMessage(content=system_prompt)]
        messages.extend(self._format_chat_history(history))
        messages.append(HumanMessage(content=query))
        
        # Generate response
        llm = self._get_llm()
        response = await llm.ainvoke(messages)
        
        return {
            "response": response.content,
            "contexts": contexts,
            "ticker": ticker
        }


# Singleton instance
_rag_engine: Optional[RAGEngine] = None


def get_rag_engine() -> RAGEngine:
    """Get the RAG engine singleton instance."""
    global _rag_engine
    if _rag_engine is None:
        _rag_engine = RAGEngine()
    return _rag_engine
