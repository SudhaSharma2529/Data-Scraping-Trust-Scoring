# Data-Scraping-Trust-Scoring
Multi-source web scraper that collects health articles from blogs, YouTube, and PubMed, with an automatic trust scoring algorithm to evaluate source reliability.

# Data Scraping & Trust Scoring Pipeline
A multi-source web scraping pipeline that collects health articles from blogs, YouTube, and PubMed, and evaluates the reliability of each source using a trust scoring algorithm.

## Tools and Libraries Used
- `requests` — sends HTTP requests to websites
- `beautifulsoup4` — reads and extracts content from HTML pages
- `yt-dlp` — extracts metadata from YouTube videos
- `youtube-transcript-api` — fetches transcripts from YouTube videos
- `langdetect` — detects the language of the content
- `lxml` — helps parse HTML faster

## Scraping Approach
- Blogs — uses BeautifulSoup to extract author, date, and article text from health websites like Healthline, WebMD, and MedicalNewsToday
- YouTube — uses yt-dlp to get channel name, upload date, and description, and youtube-transcript-api to get the video transcript
- PubMed — uses the NCBI EFetch API to extract title, authors, journal, abstract, and publication date from medical research papers

## Trust Score Design

Each source is scored between 0 and 1 based on 5 factors:

- Author credibility (25%) — checks if the author has credentials like a PhD, MD, or RD
- Citation count (15%) — how many times the article has been cited
- Domain authority (25%) — how reputable the website is
- Recency (20%) — how recent the article is
- Medical disclaimer (15%) — whether the article says "consult your doctor."

## Edge Cases Handled

- Missing author — score defaults to 0.3
- Missing date — recency defaults to 0.3
- No YouTube transcript — falls back to description only
- Multiple authors — average credibility score is used
- Spam content — penalty is applied to reduce trust score

## Limitations

- JavaScript-heavy websites cannot be scraped
- YouTube transcripts are not available for all videos
- Domain authority is based on a heuristic list, not a real API

## How to Run

1. Install dependencies:
```
pip install requests beautifulsoup4 lxml langdetect yt-dlp youtube-transcript-api
```

2. Run the pipeline:
```
python main.py
```

3. Results will be saved in the `output/` folder as JSON files.

## Output Files

- `output/blogs.json` — 3 scraped blog posts
- `output/youtube.json` — 2 scraped YouTube videos
- `output/pubmed.json` — 1 scraped PubMed article
- `output/scraped_data.json` — all 6 sources combined
