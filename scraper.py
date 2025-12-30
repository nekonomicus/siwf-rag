"""
SIWF Website Scraper
Scrapes e-Logbuch FAQ and related pages
"""
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import re

BASE_URL = "https://siwf.ch"
START_URLS = [
    "https://siwf.ch/elogbuch/faq/was-ist-das-e-logbuch.cfm",
    "https://siwf.ch/elogbuch/faq.cfm",
    "https://siwf.ch/weiterbildung/allgemeines.cfm",
]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
}

def clean_text(text):
    """Clean extracted text"""
    # Remove excessive whitespace
    text = re.sub(r'\n\s*\n', '\n\n', text)
    text = re.sub(r' +', ' ', text)
    return text.strip()

def extract_content(soup, url):
    """Extract main content from page"""
    # Remove scripts, styles, nav
    for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
        tag.decompose()
    
    # Try to find main content
    main = soup.find('main') or soup.find('article') or soup.find('div', class_=re.compile(r'content|main|article'))
    
    if main:
        text = main.get_text(separator='\n')
    else:
        text = soup.get_text(separator='\n')
    
    return clean_text(text)

def get_title(soup):
    """Extract page title"""
    title = soup.find('h1')
    if title:
        return title.get_text().strip()
    title = soup.find('title')
    if title:
        return title.get_text().strip()
    return None

def find_links(soup, base_url):
    """Find related links on page"""
    links = []
    for a in soup.find_all('a', href=True):
        href = a['href']
        full_url = urljoin(base_url, href)
        
        # Only follow SIWF links
        if 'siwf.ch' in full_url:
            # Filter for relevant sections
            if any(x in full_url.lower() for x in ['elogbuch', 'weiterbildung', 'faq', 'logbuch']):
                links.append(full_url)
    
    return list(set(links))

def scrape_page(url):
    """Scrape a single page"""
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        return {
            'url': url,
            'title': get_title(soup),
            'content': extract_content(soup, url),
            'links': find_links(soup, url)
        }
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None

def crawl_siwf(max_pages=50):
    """Crawl SIWF website starting from FAQ"""
    visited = set()
    to_visit = list(START_URLS)
    results = []
    
    while to_visit and len(visited) < max_pages:
        url = to_visit.pop(0)
        
        # Normalize URL
        url = url.split('#')[0].split('?')[0]
        
        if url in visited:
            continue
        
        print(f"Scraping: {url}")
        visited.add(url)
        
        result = scrape_page(url)
        if result and result['content'] and len(result['content']) > 100:
            results.append(result)
            
            # Add new links to queue
            for link in result['links']:
                if link not in visited:
                    to_visit.append(link)
        
        # Be nice to the server
        time.sleep(0.5)
    
    print(f"Scraped {len(results)} pages")
    return results

def scrape_to_api(api_url):
    """Scrape and send to RAG API"""
    results = crawl_siwf()
    
    for r in results:
        try:
            response = requests.post(
                f"{api_url}/api/ingest",
                json={
                    'source': 'siwf-web',
                    'source_url': r['url'],
                    'title': r['title'],
                    'content': r['content']
                }
            )
            print(f"Ingested: {r['title']} - {response.json()}")
        except Exception as e:
            print(f"Error ingesting {r['url']}: {e}")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        api_url = sys.argv[1]
        scrape_to_api(api_url)
    else:
        # Just scrape and print
        results = crawl_siwf(max_pages=30)
        for r in results:
            print(f"\n{'='*60}")
            print(f"URL: {r['url']}")
            print(f"Title: {r['title']}")
            print(f"Content length: {len(r['content'])}")
            print(r['content'][:500])

