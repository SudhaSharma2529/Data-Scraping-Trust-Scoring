import json, re, sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.chunking import chunk_text
from utils.tagging import tag_content
from scoring.trust_score import calculate_trust_score

def get_video_id(url):
    m = re.search(r"(?:v=|youtu\.be/)([A-Za-z0-9_-]{11})", url)
    return m.group(1) if m else None

def get_metadata(url):
    try:
        import yt_dlp
        with yt_dlp.YoutubeDL({"quiet": True, "skip_download": True}) as ydl:
            info = ydl.extract_info(url, download=False)
        d = info.get("upload_date", "")
        date = f"{d[:4]}-{d[4:6]}-{d[6:8]}" if len(d) == 8 else d
        return {
            "title": info.get("title", ""),
            "channel": info.get("uploader", ""),
            "date": date,
            "description": info.get("description", ""),
        }
    except Exception as e:
        print(f"  yt-dlp error: {e}")
        return {}

def get_transcript(video_id):
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        ytt = YouTubeTranscriptApi()
        transcript_list = ytt.fetch(video_id)
        text = " ".join([t.text for t in transcript_list])
        return text
    except Exception as e:
        print(f"  Transcript unavailable: {e}")
        return ""

def scrape_youtube(url):
    print(f"  Scraping: {url}")
    vid_id = get_video_id(url)
    if not vid_id:
        return {"source_url": url, "source_type": "youtube", "error": "Bad URL"}
    meta       = get_metadata(url)
    transcript = get_transcript(vid_id)
    text       = f"{meta.get('description', '')}\n\n{transcript}".strip()
    trust      = calculate_trust_score(url, "youtube", author=meta.get("channel"),
                                       published_date=meta.get("date"), full_text=text)
    return {
        "source_url": url, "source_type": "youtube",
        "title": meta.get("title", ""), "author": meta.get("channel", ""),
        "published_date": meta.get("date", ""), "language": "en", "region": "Global",
        "topic_tags": tag_content(text, meta.get("title", "")),
        "trust_score": trust["trust_score"],
        "trust_detail": trust,
        "content_chunks": chunk_text(text, "youtube"),
    }

def scrape_youtube_videos(urls):
    return [scrape_youtube(u) for u in urls]