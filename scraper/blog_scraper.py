import json, re, sys, os
import requests
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.chunking import chunk_text
from utils.tagging import tag_content
from scoring.trust_score import calculate_trust_score

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122.0"}

def fetch(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()
        return BeautifulSoup(r.text, "html.parser")
    except Exception as e:
        print(f"  Error: {e}")
        return None

def get_author(soup):
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string or "")
            if isinstance(data, list): data = data[0]
            a = data.get("author", {})
            if isinstance(a, dict) and a.get("name"): return a["name"]
        except: pass
    for attr in [{"name": "author"}, {"property": "article:author"}]:
        tag = soup.find("meta", attrs=attr)
        if tag and tag.get("content"): return tag["content"].strip()
    for cls in ["author", "byline", "post-author"]:
        el = soup.find(class_=re.compile(cls, re.I))
        if el: return el.get_text(strip=True)
    return "Unknown"

def get_date(soup):
    t = soup.find("time")
    if t: return (t.get("datetime") or t.get_text(strip=True))[:10]
    for attr in [{"property": "article:published_time"}, {"itemprop": "datePublished"}]:
        tag = soup.find("meta", attrs=attr)
        if tag and tag.get("content"): return tag["content"][:10]
    return ""

def get_text(soup):
    for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
        tag.decompose()
    for sel in ["article", "main", ".post-content", ".entry-content"]:
        c = soup.select_one(sel)
        if c: return c.get_text(separator="\n\n", strip=True)
    return soup.get_text(separator="\n\n", strip=True)

def detect_lang(text):
    try:
        from langdetect import detect
        return detect(text[:500])
    except: return "en"

def scrape_blog(url):
    print(f"  Scraping: {url}")
    soup = fetch(url)
    if not soup:
        return {"source_url": url, "source_type": "blog", "error": "Fetch failed"}
    title  = soup.title.string.strip() if soup.title else ""
    author = get_author(soup)
    date   = get_date(soup)
    text   = get_text(soup)
    trust  = calculate_trust_score(url, "blog", author=author,
                                   published_date=date, full_text=text)
    return {
        "source_url": url, "source_type": "blog", "title": title,
        "author": author, "published_date": date,
        "language": detect_lang(text), "region": "Global",
        "topic_tags": tag_content(text, title),
        "trust_score": trust["trust_score"],
        "trust_detail": trust,
        "content_chunks": chunk_text(text, "blog"),
    }

def scrape_blogs(urls):
    return [scrape_blog(u) for u in urls]