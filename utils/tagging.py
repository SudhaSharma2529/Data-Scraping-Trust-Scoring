import re

TAXONOMY = {
    "AI":            ["artificial intelligence","machine learning","deep learning","neural network","llm"],
    "Healthcare":    ["health","medical","medicine","clinical","patient","disease","diagnosis"],
    "Gut Health":    ["gut","microbiome","probiotic","prebiotic","intestinal","digestive","ibs"],
    "Nutrition":     ["diet","nutrition","food","vitamin","supplement","protein","fiber","fibre"],
    "Data Science":  ["data","scraping","pipeline","dataset","analytics","python"],
    "Mental Health": ["mental health","anxiety","depression","stress","mindfulness"],
    "Research":      ["study","research","trial","meta-analysis","abstract","journal"],
    "Technology":    ["software","api","cloud","app","platform"],
}

def tag_content(text, title="", source_type="blog", max_tags=5):
    combined = re.sub(r'\s+', ' ', f"{title} {text}".lower())
    scores = {}
    for category, keywords in TAXONOMY.items():
        count = sum(combined.count(kw) for kw in keywords)
        if count > 0:
            scores[category] = count
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    tags = [tag for tag, _ in ranked[:max_tags]]
    return tags if tags else [source_type.capitalize()]