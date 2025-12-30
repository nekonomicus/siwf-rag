"""
SIWF RAG Tool - Brutally simple knowledge base querying
Like NotebookLM but stripped down to essentials
"""
import os
import json
import hashlib
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import psycopg
from psycopg.rows import dict_row
import google.generativeai as genai

app = Flask(__name__)
CORS(app)

# Config
DATABASE_URL = os.environ.get('DATABASE_URL')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def get_db():
    """Get database connection"""
    conn = psycopg.connect(DATABASE_URL, row_factory=dict_row)
    return conn

def init_db():
    """Initialize database tables"""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id SERIAL PRIMARY KEY,
            source TEXT NOT NULL,
            source_url TEXT,
            title TEXT,
            content TEXT NOT NULL,
            content_hash TEXT UNIQUE,
            chunk_index INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE INDEX IF NOT EXISTS idx_documents_source ON documents(source);
        CREATE INDEX IF NOT EXISTS idx_documents_content_gin ON documents USING gin(to_tsvector('german', content));
        CREATE INDEX IF NOT EXISTS idx_documents_content_gin_simple ON documents USING gin(to_tsvector('simple', content));
    """)
    conn.commit()
    cur.close()
    conn.close()

def chunk_text(text, chunk_size=1500, overlap=200):
    """Split text into overlapping chunks"""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        # Try to break at sentence boundary
        if end < len(text):
            last_period = chunk.rfind('.')
            last_newline = chunk.rfind('\n')
            break_point = max(last_period, last_newline)
            if break_point > chunk_size // 2:
                chunk = chunk[:break_point + 1]
                end = start + break_point + 1
        chunks.append(chunk.strip())
        start = end - overlap
    return chunks

def store_document(source, content, source_url=None, title=None):
    """Store document chunks in database"""
    conn = get_db()
    cur = conn.cursor()
    
    chunks = chunk_text(content)
    stored = 0
    
    for i, chunk in enumerate(chunks):
        content_hash = hashlib.md5(chunk.encode()).hexdigest()
        try:
            cur.execute("""
                INSERT INTO documents (source, source_url, title, content, content_hash, chunk_index)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (content_hash) DO NOTHING
            """, (source, source_url, title, chunk, content_hash, i))
            if cur.rowcount > 0:
                stored += 1
        except Exception as e:
            print(f"Error storing chunk: {e}")
    
    conn.commit()
    cur.close()
    conn.close()
    return stored

def search_fulltext(query, limit=20):
    """Full-text search - deterministic, exact matches"""
    conn = get_db()
    cur = conn.cursor()
    
    # Try German first, then simple for technical terms
    cur.execute("""
        SELECT DISTINCT ON (content_hash) 
            id, source, source_url, title, content, chunk_index,
            ts_rank(to_tsvector('german', content), plainto_tsquery('german', %s)) +
            ts_rank(to_tsvector('simple', content), plainto_tsquery('simple', %s)) as rank
        FROM documents
        WHERE to_tsvector('german', content) @@ plainto_tsquery('german', %s)
           OR to_tsvector('simple', content) @@ plainto_tsquery('simple', %s)
           OR content ILIKE %s
        ORDER BY content_hash, rank DESC
        LIMIT %s
    """, (query, query, query, query, f'%{query}%', limit))
    
    results = cur.fetchall()
    cur.close()
    conn.close()
    return results

def search_semantic(query, limit=10):
    """Search for semantically relevant chunks (keyword-based for now)"""
    # Extract key terms
    terms = query.lower().split()
    
    conn = get_db()
    cur = conn.cursor()
    
    # Combine full-text and ILIKE for better recall
    conditions = " OR ".join(["content ILIKE %s" for _ in terms])
    params = [f'%{term}%' for term in terms if len(term) > 2]
    
    if not params:
        return []
    
    cur.execute(f"""
        SELECT id, source, source_url, title, content, chunk_index
        FROM documents
        WHERE {conditions}
        ORDER BY LENGTH(content) DESC
        LIMIT %s
    """, params + [limit])
    
    results = cur.fetchall()
    cur.close()
    conn.close()
    return results

def ask_gemini(question, context_chunks):
    """Ask Gemini with context - MUST return quotes"""
    if not GEMINI_API_KEY:
        return {"error": "Gemini API key not configured", "answer": None, "quotes": []}
    
    # Build context
    context = "\n\n---\n\n".join([
        f"[Source: {c['source']}]\n{c['content']}" 
        for c in context_chunks
    ])
    
    prompt = f"""Du bist ein Experte für das SIWF e-Logbuch und die Weiterbildung in der Schweiz.
Beantworte die folgende Frage NUR basierend auf dem gegebenen Kontext.

WICHTIGE REGELN:
1. Jede Aussage MUSS mit einem direkten Zitat aus dem Kontext belegt werden
2. Formatiere Zitate als: «Zitat hier» (Quelle: [Quellenname])
3. Wenn die Information nicht im Kontext ist, sage klar "Diese Information ist nicht in den verfügbaren Dokumenten enthalten"
4. Sei präzise und faktisch

KONTEXT:
{context}

FRAGE: {question}

ANTWORT (mit Zitaten):"""

    try:
        model = genai.GenerativeModel('gemini-2.5-pro-preview-06-05')
        response = model.generate_content(prompt)
        return {
            "answer": response.text,
            "sources_used": len(context_chunks),
            "context_chunks": [{"source": c['source'], "preview": c['content'][:200] + "..."} for c in context_chunks]
        }
    except Exception as e:
        return {"error": str(e), "answer": None}

# HTML Frontend - brutally simple
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SIWF RAG Tool</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { 
            font-family: 'SF Mono', 'Consolas', monospace; 
            background: #0a0a0a; 
            color: #e0e0e0; 
            padding: 20px;
            max-width: 1200px;
            margin: 0 auto;
        }
        h1 { color: #00ff88; margin-bottom: 10px; font-size: 1.5em; }
        .subtitle { color: #666; margin-bottom: 30px; font-size: 0.9em; }
        .tabs { display: flex; gap: 10px; margin-bottom: 20px; }
        .tab { 
            padding: 10px 20px; 
            background: #1a1a1a; 
            border: 1px solid #333; 
            color: #888;
            cursor: pointer;
            transition: all 0.2s;
        }
        .tab.active { background: #00ff88; color: #000; border-color: #00ff88; }
        .tab:hover { border-color: #00ff88; }
        .panel { display: none; }
        .panel.active { display: block; }
        input, textarea { 
            width: 100%; 
            padding: 15px; 
            background: #111; 
            border: 1px solid #333; 
            color: #fff;
            font-family: inherit;
            font-size: 1em;
            margin-bottom: 10px;
        }
        input:focus, textarea:focus { outline: none; border-color: #00ff88; }
        button { 
            padding: 15px 30px; 
            background: #00ff88; 
            border: none; 
            color: #000;
            font-weight: bold;
            cursor: pointer;
            font-family: inherit;
        }
        button:hover { background: #00cc6a; }
        button:disabled { background: #333; color: #666; cursor: not-allowed; }
        .results { 
            margin-top: 20px; 
            background: #111; 
            border: 1px solid #333;
            max-height: 70vh;
            overflow-y: auto;
        }
        .result-item { 
            padding: 15px; 
            border-bottom: 1px solid #222;
        }
        .result-item:last-child { border-bottom: none; }
        .source { color: #00ff88; font-size: 0.8em; margin-bottom: 5px; }
        .content { white-space: pre-wrap; line-height: 1.6; }
        .answer { 
            padding: 20px; 
            background: #0d1f0d; 
            border-left: 3px solid #00ff88;
            white-space: pre-wrap;
            line-height: 1.8;
        }
        .loading { color: #00ff88; padding: 20px; }
        .error { color: #ff4444; padding: 20px; }
        .stats { color: #666; font-size: 0.8em; padding: 10px 20px; background: #0a0a0a; }
        mark { background: #00ff8833; color: #00ff88; }
        .quote { 
            background: #1a1a0a; 
            border-left: 2px solid #ffcc00;
            padding: 10px;
            margin: 10px 0;
        }
    </style>
</head>
<body>
    <h1>⚡ SIWF RAG Tool</h1>
    <p class="subtitle">e-Logbuch Knowledge Base | Gemini 2.5 Pro | Full-text Search</p>
    
    <div class="tabs">
        <div class="tab active" onclick="switchTab('ask')">🤖 Ask (RAG)</div>
        <div class="tab" onclick="switchTab('search')">🔍 Search (Exact)</div>
        <div class="tab" onclick="switchTab('stats')">📊 Stats</div>
    </div>
    
    <div id="ask-panel" class="panel active">
        <textarea id="question" rows="3" placeholder="Stelle eine Frage über das e-Logbuch, Weiterbildung, etc..."></textarea>
        <button onclick="askQuestion()">Fragen (mit Zitaten)</button>
        <div id="ask-results" class="results"></div>
    </div>
    
    <div id="search-panel" class="panel">
        <input type="text" id="search-query" placeholder="Suchbegriff eingeben (exakte Suche)...">
        <button onclick="searchDocs()">Suchen</button>
        <div id="search-results" class="results"></div>
    </div>
    
    <div id="stats-panel" class="panel">
        <button onclick="loadStats()">Load Stats</button>
        <div id="stats-results" class="results"></div>
    </div>

    <script>
        function switchTab(tab) {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
            event.target.classList.add('active');
            document.getElementById(tab + '-panel').classList.add('active');
        }
        
        async function askQuestion() {
            const q = document.getElementById('question').value;
            const results = document.getElementById('ask-results');
            results.innerHTML = '<div class="loading">⏳ Searching & generating answer with quotes...</div>';
            
            try {
                const res = await fetch('/api/ask', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({question: q})
                });
                const data = await res.json();
                
                if (data.error) {
                    results.innerHTML = `<div class="error">Error: ${data.error}</div>`;
                } else {
                    let html = `<div class="answer">${data.answer}</div>`;
                    html += `<div class="stats">Sources searched: ${data.sources_used || 0} chunks</div>`;
                    if (data.context_chunks) {
                        html += '<div style="padding: 10px; color: #666; font-size: 0.8em;">Context used:</div>';
                        data.context_chunks.forEach(c => {
                            html += `<div class="result-item"><div class="source">${c.source}</div><div class="content" style="font-size: 0.8em; color: #888;">${c.preview}</div></div>`;
                        });
                    }
                    results.innerHTML = html;
                }
            } catch (e) {
                results.innerHTML = `<div class="error">Error: ${e.message}</div>`;
            }
        }
        
        async function searchDocs() {
            const q = document.getElementById('search-query').value;
            const results = document.getElementById('search-results');
            results.innerHTML = '<div class="loading">⏳ Searching...</div>';
            
            try {
                const res = await fetch(`/api/search?q=${encodeURIComponent(q)}`);
                const data = await res.json();
                
                if (data.results.length === 0) {
                    results.innerHTML = '<div class="result-item">No results found</div>';
                } else {
                    let html = `<div class="stats">${data.count} results found</div>`;
                    data.results.forEach(r => {
                        const highlighted = r.content.replace(new RegExp(q, 'gi'), '<mark>$&</mark>');
                        html += `<div class="result-item">
                            <div class="source">[${r.source}] ${r.title || ''}</div>
                            <div class="content">${highlighted}</div>
                        </div>`;
                    });
                    results.innerHTML = html;
                }
            } catch (e) {
                results.innerHTML = `<div class="error">Error: ${e.message}</div>`;
            }
        }
        
        async function loadStats() {
            const results = document.getElementById('stats-results');
            try {
                const res = await fetch('/api/stats');
                const data = await res.json();
                results.innerHTML = `<div class="result-item"><pre>${JSON.stringify(data, null, 2)}</pre></div>`;
            } catch (e) {
                results.innerHTML = `<div class="error">Error: ${e.message}</div>`;
            }
        }
        
        // Enter key handlers
        document.getElementById('question').addEventListener('keydown', e => {
            if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); askQuestion(); }
        });
        document.getElementById('search-query').addEventListener('keydown', e => {
            if (e.key === 'Enter') searchDocs();
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/search')
def api_search():
    """Full-text search endpoint - deterministic, exact matches"""
    query = request.args.get('q', '')
    if not query:
        return jsonify({"error": "No query provided", "results": []})
    
    results = search_fulltext(query)
    return jsonify({
        "query": query,
        "count": len(results),
        "results": [dict(r) for r in results]
    })

@app.route('/api/ask', methods=['POST'])
def api_ask():
    """RAG endpoint - Gemini with mandatory quotes"""
    data = request.get_json()
    question = data.get('question', '')
    
    if not question:
        return jsonify({"error": "No question provided"})
    
    # Get relevant chunks
    chunks = search_semantic(question, limit=8)
    if not chunks:
        chunks = search_fulltext(question, limit=8)
    
    if not chunks:
        return jsonify({
            "answer": "Keine relevanten Dokumente gefunden. Bitte versuche andere Suchbegriffe.",
            "sources_used": 0
        })
    
    # Ask Gemini
    result = ask_gemini(question, chunks)
    return jsonify(result)

@app.route('/api/stats')
def api_stats():
    """Database statistics"""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT 
            COUNT(*) as total_chunks,
            COUNT(DISTINCT source) as sources,
            COUNT(DISTINCT title) as documents
        FROM documents
    """)
    stats = dict(cur.fetchone())
    
    cur.execute("""
        SELECT source, COUNT(*) as chunks 
        FROM documents 
        GROUP BY source 
        ORDER BY chunks DESC
    """)
    stats['by_source'] = [dict(r) for r in cur.fetchall()]
    
    cur.close()
    conn.close()
    return jsonify(stats)

@app.route('/api/ingest', methods=['POST'])
def api_ingest():
    """Ingest new content"""
    data = request.get_json()
    source = data.get('source', 'manual')
    content = data.get('content', '')
    source_url = data.get('source_url')
    title = data.get('title')
    
    if not content:
        return jsonify({"error": "No content provided"})
    
    stored = store_document(source, content, source_url, title)
    return jsonify({"stored_chunks": stored})

@app.route('/health')
def health():
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    # Initialize DB on startup
    if DATABASE_URL:
        try:
            init_db()
            print("Database initialized")
        except Exception as e:
            print(f"DB init error: {e}")
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

