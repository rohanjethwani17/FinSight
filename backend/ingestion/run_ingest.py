"""
FinSight SEC 10-K Ingestion Script

This script fetches SEC 10-K filings and ingests them into Pinecone.
The data is stored with the following schema:
- Namespace: Ticker symbol (e.g., "AAPL")
- Metadata: {
    "source_url": "SEC filing URL",
    "section_header": "Risk Factors", "Business Overview", etc.,
    "year": "2023",
    "text_content": "The actual text content..."
  }

Usage:
    python run_ingest.py --ticker AAPL
    python run_ingest.py --ticker MSFT
    python run_ingest.py --ticker GOOGL
"""

import os
import sys
import argparse
import time
import hashlib
from typing import List, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    from pinecone import Pinecone, ServerlessSpec
    from langchain_openai import OpenAIEmbeddings
    from langchain.text_splitter import RecursiveCharacterTextSplitter
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Please install requirements: pip install -r requirements.txt")
    sys.exit(1)


# Configuration
PINECONE_INDEX_NAME = os.environ.get("PINECONE_INDEX_NAME", "finsight-index")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")

# SEC EDGAR Base URL
SEC_EDGAR_BASE = "https://www.sec.gov/cgi-bin/browse-edgar"

# Company CIK mapping (Central Index Key for SEC EDGAR)
COMPANY_CIK = {
    "AAPL": "0000320193",
    "MSFT": "0000789019",
    "GOOGL": "0001652044"
}

# Text splitter configuration
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200


def get_embeddings() -> OpenAIEmbeddings:
    """Initialize OpenAI embeddings."""
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY environment variable not set")
    return OpenAIEmbeddings(
        model="text-embedding-3-small",
        openai_api_key=OPENAI_API_KEY
    )


def get_pinecone_index():
    """Get or create Pinecone index."""
    if not PINECONE_API_KEY:
        raise ValueError("PINECONE_API_KEY environment variable not set")
    
    pc = Pinecone(api_key=PINECONE_API_KEY)
    
    # Check if index exists
    existing_indexes = [idx.name for idx in pc.list_indexes()]
    
    if PINECONE_INDEX_NAME not in existing_indexes:
        print(f"Creating index: {PINECONE_INDEX_NAME}")
        pc.create_index(
            name=PINECONE_INDEX_NAME,
            dimension=1536,  # text-embedding-3-small dimension
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1"
            )
        )
        # Wait for index to be ready
        time.sleep(10)
    
    return pc.Index(PINECONE_INDEX_NAME)


def generate_vector_id(ticker: str, section: str, chunk_index: int) -> str:
    """Generate a unique vector ID."""
    content = f"{ticker}-{section}-{chunk_index}"
    return hashlib.md5(content.encode()).hexdigest()


def fetch_10k_sections(ticker: str) -> List[Dict[str, Any]]:
    """
    Fetch 10-K filing sections for a ticker.
    
    NOTE: This is a placeholder. In production, you would:
    1. Use the SEC EDGAR API to fetch actual 10-K filings
    2. Parse the HTML/XML documents
    3. Extract sections like Risk Factors, Business, MD&A, etc.
    
    For demo purposes, this returns sample data.
    """
    # Sample sections that would be extracted from real 10-K filings
    sample_sections = {
        "AAPL": [
            {
                "section_header": "Business Overview",
                "year": "2023",
                "source_url": "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0000320193&type=10-K",
                "text_content": """Apple Inc. designs, manufactures, and markets smartphones, personal computers, tablets, wearables, and accessories worldwide. The Company also sells various related services. The Company's products include iPhone, Mac, iPad, and Wearables, Home and Accessories. iPhone is the Company's line of smartphones based on its iOS operating system. Mac is the Company's line of personal computers based on its macOS operating system. iPad is the Company's line of multi-purpose tablets based on its iPadOS operating system."""
            },
            {
                "section_header": "Risk Factors",
                "year": "2023",
                "source_url": "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0000320193&type=10-K",
                "text_content": """The Company's business, reputation, results of operations, financial condition and stock price can be affected by a number of factors, whether currently known or unknown, including those described below. Global and regional economic conditions could materially adversely affect the Company. The Company has international operations with sales outside the U.S. representing a majority of the Company's total net sales. Global markets for the Company's products and services are highly competitive and subject to rapid technological change."""
            },
            {
                "section_header": "Financial Data",
                "year": "2023",
                "source_url": "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0000320193&type=10-K",
                "text_content": """Total net sales decreased 3% or $11.0 billion during 2023 compared to 2022. The weakness in foreign currencies relative to the U.S. dollar had an unfavorable impact on net sales during 2023. iPhone revenue was $200.6 billion, representing 52% of total net sales. Services revenue was $85.2 billion, an increase of 9% year-over-year. The Company's gross margin was 44.1% in 2023 compared to 43.3% in 2022."""
            }
        ],
        "MSFT": [
            {
                "section_header": "Business Overview",
                "year": "2023",
                "source_url": "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0000789019&type=10-K",
                "text_content": """Microsoft Corporation is a technology company. The Company develops and supports software, services, devices and solutions. The Company's segments include Productivity and Business Processes, Intelligent Cloud, and More Personal Computing. Microsoft Cloud is a comprehensive portfolio that includes Microsoft 365, Azure, Dynamics 365, and other cloud services. Azure is a comprehensive set of cloud services that developers and IT professionals use to build, deploy, and manage applications."""
            },
            {
                "section_header": "Risk Factors",
                "year": "2023",
                "source_url": "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0000789019&type=10-K",
                "text_content": """Our business is subject to various risks. Our future growth depends on the success of our Cloud-based services, including Azure and Microsoft 365. We face intense competition across all markets for our products and services. AI-related risks include potential regulatory actions, ethical concerns, and competition. Cybersecurity risks could adversely affect our business and reputation. Economic conditions may adversely affect demand for our products and services."""
            },
            {
                "section_header": "Financial Data",
                "year": "2023",
                "source_url": "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0000789019&type=10-K",
                "text_content": """Revenue was $211.9 billion, an increase of 7% compared to fiscal year 2022. Microsoft Cloud revenue was $111.6 billion, up 22%. Operating income was $88.5 billion, and net income was $72.4 billion. Intelligent Cloud revenue increased 17% driven by Azure and other cloud services revenue growth of 27%. Azure AI services continue to show strong growth with significant enterprise adoption."""
            }
        ],
        "GOOGL": [
            {
                "section_header": "Business Overview",
                "year": "2023",
                "source_url": "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001652044&type=10-K",
                "text_content": """Alphabet Inc. is a holding company. The Company's segments include Google Services, Google Cloud, and Other Bets. Google Services includes products and services such as ads, Android, Chrome, hardware, Google Maps, Google Play, Search, and YouTube. Google Cloud includes infrastructure and data analytics platforms, collaboration tools, and other services for enterprise customers. Google's mission is to organize the world's information and make it universally accessible and useful."""
            },
            {
                "section_header": "Risk Factors",
                "year": "2023",
                "source_url": "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001652044&type=10-K",
                "text_content": """We face significant competition and may not be able to compete effectively. Our revenues are highly dependent on advertising, which may be adversely affected by various factors. AI development presents risks including ethical, legal, and regulatory challenges. We are subject to complex and changing privacy and data protection laws. Antitrust investigations and enforcement actions could adversely affect our business. Our intellectual property rights are valuable, and failure to protect them could harm our business."""
            },
            {
                "section_header": "Financial Data",
                "year": "2023",
                "source_url": "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001652044&type=10-K",
                "text_content": """Total revenues were $307.4 billion, an increase of 9% year-over-year. Google Search and other advertising revenues were $175.0 billion. YouTube advertising revenues were $31.5 billion. Google Cloud revenues were $33.1 billion, an increase of 26%. Operating income was $84.3 billion, representing an operating margin of 27%. Net income was $73.8 billion, an increase of 23% compared to the prior year."""
            }
        ]
    }
    
    return sample_sections.get(ticker, [])


def ingest_ticker(ticker: str) -> int:
    """Ingest SEC 10-K data for a specific ticker."""
    print(f"\n{'='*50}")
    print(f"Ingesting data for {ticker}")
    print(f"{'='*50}")
    
    # Initialize components
    embeddings = get_embeddings()
    index = get_pinecone_index()
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    
    # Fetch sections
    sections = fetch_10k_sections(ticker)
    if not sections:
        print(f"No data found for {ticker}")
        return 0
    
    vectors_to_upsert = []
    total_chunks = 0
    
    for section in sections:
        section_header = section["section_header"]
        text_content = section["text_content"]
        year = section["year"]
        source_url = section["source_url"]
        
        # Split text into chunks
        chunks = text_splitter.split_text(text_content)
        print(f"  Section '{section_header}': {len(chunks)} chunks")
        
        for i, chunk in enumerate(chunks):
            # Generate embedding
            embedding = embeddings.embed_query(chunk)
            
            # Create vector
            vector_id = generate_vector_id(ticker, section_header, i)
            vectors_to_upsert.append({
                "id": vector_id,
                "values": embedding,
                "metadata": {
                    "text_content": chunk,
                    "section_header": section_header,
                    "year": year,
                    "source_url": source_url,
                    "ticker": ticker,
                    "chunk_index": i
                }
            })
            total_chunks += 1
    
    # Upsert vectors to Pinecone (namespace = ticker)
    if vectors_to_upsert:
        # Upsert in batches of 100
        batch_size = 100
        for i in range(0, len(vectors_to_upsert), batch_size):
            batch = vectors_to_upsert[i:i + batch_size]
            index.upsert(vectors=batch, namespace=ticker)
            print(f"  Upserted batch {i//batch_size + 1}: {len(batch)} vectors")
    
    print(f"  Total vectors upserted for {ticker}: {total_chunks}")
    return total_chunks


def main():
    """Main entry point for ingestion script."""
    parser = argparse.ArgumentParser(description="Ingest SEC 10-K filings into Pinecone")
    parser.add_argument(
        "--ticker",
        type=str,
        choices=["AAPL", "MSFT", "GOOGL", "ALL"],
        default="ALL",
        help="Ticker symbol to ingest (or ALL for all tickers)"
    )
    args = parser.parse_args()
    
    print("FinSight SEC 10-K Ingestion Script")
    print("=" * 50)
    print(f"Pinecone Index: {PINECONE_INDEX_NAME}")
    print(f"OpenAI API Key: {'Set' if OPENAI_API_KEY else 'NOT SET'}")
    print(f"Pinecone API Key: {'Set' if PINECONE_API_KEY else 'NOT SET'}")
    
    if not OPENAI_API_KEY or not PINECONE_API_KEY:
        print("\nERROR: Missing required API keys!")
        print("Please set OPENAI_API_KEY and PINECONE_API_KEY environment variables.")
        sys.exit(1)
    
    tickers = ["AAPL", "MSFT", "GOOGL"] if args.ticker == "ALL" else [args.ticker]
    
    total_vectors = 0
    for ticker in tickers:
        vectors = ingest_ticker(ticker)
        total_vectors += vectors
    
    print("\n" + "=" * 50)
    print(f"Ingestion complete! Total vectors: {total_vectors}")
    print("=" * 50)


if __name__ == "__main__":
    main()
