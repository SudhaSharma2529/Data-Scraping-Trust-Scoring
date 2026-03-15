import math, re
from datetime import date, datetime
from urllib.parse import urlparse

WEIGHTS = {
    "author_credibility":          0.25,
    "citation_count":              0.15,
    "domain_authority":            0.25,
    "recency":                     0.20,
    "medical_disclaimer_presence": 0.15,
}

HIGH_AUTHORITY = {
    "pubmed.ncbi.nlm.nih.gov","nih.gov","who.int","cdc.gov",
    "nature.com","thelancet.com","nejm.org","bmj.com","youtube.com"
}
MID_AUTHORITY = {
    "healthline.com","medicalnewstoday.com","webmd.com",
    "mayoclinic.org","harvard.edu","stanford.edu","medium.com"
}
CREDIBLE_SIGNALS = ["dr.","md","phd","professor","rdn","harvard","stanford","mayo","nih","who"]
SPAM_PATTERNS    = [r"earn \$", r"miracle cure", r"doctors hate", r"one weird trick"]
DISCLAIMER_PATS  = [
    r"not (a )?medical advice",
    r"consult (a |your )?(doctor|physician)",
    r"for (informational|educational) purposes only",
    r"always seek (professional|medical) (advice|help)",
]

def score_author(author, authors=None):
    if not author and not authors:
        return 0.3
    names = authors if authors else [author]
    scores = []
    for a in names:
        a_lower = a.lower()
        if any(re.search(p, a_lower) for p in SPAM_PATTERNS):
            scores.append(0.0)
        else:
            hits = sum(1 for kw in CREDIBLE_SIGNALS if kw in a_lower)
            scores.append(min(0.5 + hits * 0.2, 1.0))
    return sum(scores) / len(scores)

def score_citations(citations, source_type="blog"):
    if citations is None:
        return 0.4 if source_type == "pubmed" else 0.2
    if citations == 0:
        return 0.1
    return min(math.log10(citations + 1) / 2.0, 1.0)

def score_domain(url):
    try:
        domain = urlparse(url).netloc.lower().lstrip("www.")
    except:
        return 0.2
    if any(h in domain for h in HIGH_AUTHORITY): return 1.0
    if any(m in domain for m in MID_AUTHORITY):  return 0.7
    if re.search(r"blogspot|wix\.com|weebly|tumblr", domain): return 0.1
    return 0.4

def score_recency(pub_date):
    if not pub_date:
        return 0.3
    for fmt in ["%Y-%m-%d", "%B %d, %Y", "%Y"]:
        try:
            parsed = datetime.strptime(pub_date.strip(), fmt).date()
            age_years = (date.today() - parsed).days / 365.25
            return max(round(math.exp(-0.46 * age_years), 4), 0.05)
        except:
            continue
    return 0.3

def score_disclaimer(text, source_type="blog"):
    if source_type in ("tech", "data"):
        return 0.5
    return 1.0 if any(re.search(p, text.lower()) for p in DISCLAIMER_PATS) else 0.0

def abuse_penalty(text, url):
    penalty = 1.0
    if any(re.search(p, text.lower()) for p in SPAM_PATTERNS):
        penalty -= 0.20
    if score_domain(url) < 0.2:
        penalty -= 0.10
    return max(round(penalty, 4), 0.05)

def calculate_trust_score(source_url, source_type, author=None, authors=None,
                           published_date=None, citation_count=None, full_text=""):
    flags = []
    a  = score_author(author, authors)
    c  = score_citations(citation_count, source_type)
    d  = score_domain(source_url)
    r  = score_recency(published_date)
    m  = score_disclaimer(full_text, source_type)
    ap = abuse_penalty(full_text, source_url)

    if not author and not authors: flags.append("Missing author")
    if not published_date:         flags.append("Missing publish date")
    if citation_count is None:     flags.append("Citation count unavailable")
    if m == 0.0:                   flags.append("No medical disclaimer found")
    if ap < 0.9:                   flags.append("Spam signals detected")

    raw = (WEIGHTS["author_credibility"]          * a +
           WEIGHTS["citation_count"]              * c +
           WEIGHTS["domain_authority"]            * d +
           WEIGHTS["recency"]                     * r +
           WEIGHTS["medical_disclaimer_presence"] * m)

    score = round(min(raw * ap, 1.0), 4)
    return {
        "trust_score": score,
        "components":  {"author": a, "citations": c, "domain": d, "recency": r, "disclaimer": m},
        "abuse_penalty": ap,
        "flags": flags,
    }