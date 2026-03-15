import json, re, sys, os, time, requests
from xml.etree import ElementTree as ET

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.chunking import chunk_text
from utils.tagging import tag_content
from scoring.trust_score import calculate_trust_score

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

def get_pmid(url):
    m = re.search(r"(\d{7,9})", url)
    return m.group(1) if m else None

def fetch_xml(pmid):
    try:
        r = requests.get(f"{EUTILS}/efetch.fcgi?db=pubmed&id={pmid}&rettype=xml", timeout=20)
        return ET.fromstring(r.text)
    except Exception as e:
        print(f"  EFetch error: {e}")
        return None

def txt(el, path, default=""):
    if el is None: return default
    n = el.find(path)
    return "".join(n.itertext()).strip() if n is not None else default

def parse_article(root):
    article = root.find(".//PubmedArticle")
    if not article: return {}
    title = txt(article, ".//ArticleTitle")
    abstract_parts = []
    for ab in article.findall(".//AbstractText"):
        label = ab.get("Label", "")
        t = "".join(ab.itertext()).strip()
        abstract_parts.append(f"{label}: {t}" if label else t)
    abstract = "\n\n".join(abstract_parts)
    authors  = [f"{txt(a,'ForeName')} {txt(a,'LastName')}".strip()
                for a in article.findall(".//Author") if txt(a, "LastName")]
    months   = {"Jan":"01","Feb":"02","Mar":"03","Apr":"04","May":"05","Jun":"06",
                "Jul":"07","Aug":"08","Sep":"09","Oct":"10","Nov":"11","Dec":"12"}
    pd = article.find(".//PubDate")
    y, mo, d = txt(pd, "Year"), txt(pd, "Month"), txt(pd, "Day")
    pub_date = f"{y}-{months.get(mo,mo).zfill(2)}-{d.zfill(2)}" if y and mo and d else y
    return {"title": title, "abstract": abstract, "authors": authors,
            "author_str": ", ".join(authors), "published_date": pub_date}

def fetch_citations(pmid):
    try:
        r = requests.get(f"https://icite.od.nih.gov/api/pubs?pmids={pmid}", timeout=10)
        pubs = r.json().get("data", [])
        return pubs[0].get("citation_count") if pubs else None
    except: return None

def scrape_pubmed(url):
    print(f"  Scraping: {url}")
    pmid = get_pmid(url)
    if not pmid:
        return {"source_url": url, "source_type": "pubmed", "error": "No PMID"}
    canonical = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
    root = fetch_xml(pmid)
    if root is None:
        return {"source_url": canonical, "source_type": "pubmed", "error": "XML failed"}
    meta      = parse_article(root)
    citations = fetch_citations(pmid)
    text      = f"{meta.get('title','')} {meta.get('abstract','')}".strip()
    trust     = calculate_trust_score(canonical, "pubmed", author=meta.get("author_str"),
                                      authors=meta.get("authors"),
                                      published_date=meta.get("published_date"),
                                      citation_count=citations, full_text=text)
    return {
        "source_url": canonical, "source_type": "pubmed",
        "title": meta.get("title", ""), "author": meta.get("author_str", ""),
        "published_date": meta.get("published_date", ""), "language": "en", "region": "Global",
        "topic_tags": tag_content(text, meta.get("title", "")),
        "trust_score": trust["trust_score"],
        "trust_detail": trust,
        "content_chunks": chunk_text(meta.get("abstract", ""), "pubmed"),
        "citation_count": citations,
    }

def scrape_pubmed_articles(urls):
    results = []
    for url in urls:
        results.append(scrape_pubmed(url))
        time.sleep(0.4)
    return results