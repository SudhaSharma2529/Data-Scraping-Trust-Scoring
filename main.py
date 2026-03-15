import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))

from scraper.blog_scraper    import scrape_blogs
from scraper.youtube_scraper import scrape_youtube_videos
from scraper.pubmed_scraper  import scrape_pubmed_articles

BLOG_URLS = [
    "https://www.healthline.com/nutrition/gut-microbiome-and-health",
    "https://www.medicalnewstoday.com/articles/325217",
    "https://www.webmd.com/digestive-disorders/what-is-leaky-gut",
]
YOUTUBE_URLS = [
    "https://www.youtube.com/watch?v=aIxNm5aFpGE",
    "https://www.youtube.com/watch?v=1sISguPDlhY",
]
PUBMED_URLS = ["https://pubmed.ncbi.nlm.nih.gov/32619191/"]

def save(data, filename):
    os.makedirs("output", exist_ok=True)
    with open(f"output/{filename}", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"  Saved {len(data)} records -> output/{filename}")

print("\n=== GutBut Scraping Pipeline ===\n")

print("[1/3] Blogs...")
blogs = scrape_blogs(BLOG_URLS)
save(blogs, "blogs.json")

print("\n[2/3] YouTube...")
videos = scrape_youtube_videos(YOUTUBE_URLS)
save(videos, "youtube.json")

print("\n[3/3] PubMed...")
pubmed = scrape_pubmed_articles(PUBMED_URLS)
save(pubmed, "pubmed.json")

all_data = blogs + videos + pubmed
save(all_data, "scraped_data.json")
print(f"\nDone! {len(all_data)} total records saved.")