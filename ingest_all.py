#!/usr/bin/env python3
"""
One-shot script to ingest all content into the RAG database
Run this after deploying to Render to populate the database
"""
import os
import sys
import requests

def main():
    # Get API URL from environment or command line
    api_url = os.environ.get('RAG_API_URL') or (sys.argv[1] if len(sys.argv) > 1 else None)
    
    if not api_url:
        print("Usage: python ingest_all.py <api_url>")
        print("   or: RAG_API_URL=<url> python ingest_all.py")
        sys.exit(1)
    
    print(f"Ingesting content to: {api_url}")
    
    # 1. Load orthopedics PDF content
    print("\n=== Loading Orthopedics PDF ===")
    from pdf_loader import load_orthopedics_content
    result = load_orthopedics_content(api_url)
    print(f"Result: {result}")
    
    # 2. Scrape SIWF website
    print("\n=== Scraping SIWF Website ===")
    from scraper import scrape_to_api
    scrape_to_api(api_url)
    
    # 3. Check stats
    print("\n=== Final Stats ===")
    stats = requests.get(f"{api_url}/api/stats").json()
    print(f"Total chunks: {stats.get('total_chunks', 0)}")
    print(f"Sources: {stats.get('sources', 0)}")
    print(f"Documents: {stats.get('documents', 0)}")
    print("\nBy source:")
    for s in stats.get('by_source', []):
        print(f"  - {s['source']}: {s['chunks']} chunks")
    
    print("\n✅ Ingestion complete!")

if __name__ == '__main__':
    main()

