# SIWF RAG Tool

Brutally simple knowledge base for Swiss medical training (e-Logbuch) documentation.
Like NotebookLM but stripped down to essentials.

## Features

- **RAG Queries**: Ask questions, get answers with mandatory quotes/citations
- **Full-text Search**: Deterministic access to primary sources
- **Multi-source**: SIWF website + PDF documents
- **Any LLM**: Uses Gemini 2.5 Pro, but context can be exported

## Quick Start

### Deploy to Render

1. Push to GitHub
2. Create PostgreSQL database on Render
3. Create Web Service with:
   - Build: `pip install -r requirements.txt`
   - Start: `gunicorn app:app --bind 0.0.0.0:$PORT`
   - Environment variables:
     - `DATABASE_URL`: Your Render PostgreSQL URL
     - `GEMINI_API_KEY`: Your Google AI API key

### Ingest Content

After deployment, run:

```bash
python ingest_all.py https://your-service.onrender.com
```

Or run individual loaders:

```bash
# Scrape SIWF website
python scraper.py https://your-service.onrender.com

# Load orthopedics PDF
python pdf_loader.py https://your-service.onrender.com --ortho
```

## API Endpoints

### `GET /` 
Web interface

### `GET /api/search?q=<query>`
Full-text search - deterministic, exact matches

### `POST /api/ask`
RAG query with Gemini - returns answer with quotes

```json
{
  "question": "Wie lange dauert die Weiterbildung?"
}
```

### `POST /api/ingest`
Add new content

```json
{
  "source": "manual",
  "title": "Document Title",
  "content": "Content here...",
  "source_url": "https://..."
}
```

### `GET /api/stats`
Database statistics

## Environment Variables

- `DATABASE_URL`: PostgreSQL connection string
- `GEMINI_API_KEY`: Google AI API key
- `PORT`: Server port (default: 5000)

