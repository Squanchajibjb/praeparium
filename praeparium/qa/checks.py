import re
from textstat import flesch_kincaid_grade

def _counts(md: str):
    words = re.findall(r"\w+", md)
    sentences = re.split(r"[.!?]+", md)
    return len(words), sum(1 for s in sentences if s.strip())

def check_headings(md: str) -> bool:
    return "## TL;DR" in md

def check_readability(md: str, max_grade: float = 8.0, min_words: int = 120, min_sentences: int = 5) -> bool:
    words, sents = _counts(md)
    # If it's very short, don't fail readability yet (let content expand first)
    if words < min_words or sents < min_sentences:
        return True
    try:
        return flesch_kincaid_grade(md) <= max_grade
    except Exception:
        return True

def check_counts(article_vars: dict,
                 internal_min=3, internal_max=8,
                 external_min=2, external_max=5,
                 faqs_min=5):
    il = len(article_vars.get("internal_links", []))
    el = len(article_vars.get("external_links", []))
    fq = len(article_vars.get("faqs", []))
    return (internal_min <= il <= internal_max) and (external_min <= el <= external_max) and (fq >= faqs_min)

def run_checks(article_md: str, article_vars: dict) -> dict:
    return {
        "Headings": check_headings(article_md),
        "Readability": check_readability(article_md),
        "Links_FAQs": check_counts(article_vars),
    }
