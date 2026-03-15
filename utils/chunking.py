import re

def chunk_by_paragraph(text, min_length=80):
    raw_chunks = re.split(r'\n{2,}', text.strip())
    return [c.strip() for c in raw_chunks if len(c.strip()) >= min_length]

def chunk_by_sentence(text, chunk_size=3):
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    sentences = [s.strip() for s in sentences if s.strip()]
    chunks = []
    for i in range(0, len(sentences), chunk_size):
        group = ' '.join(sentences[i:i+chunk_size])
        if group:
            chunks.append(group)
    return chunks

def chunk_text(text, source_type="blog"):
    if not text or not text.strip():
        return []
    if source_type in ("blog", "pubmed"):
        chunks = chunk_by_paragraph(text)
        if len(chunks) < 2:
            chunks = chunk_by_sentence(text)
    else:
        chunks = chunk_by_sentence(text)
    return chunks