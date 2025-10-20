from __future__ import annotations
import re
from textstat import flesch_kincaid_grade

BAD_PHRASES = [
    r"\bAs an AI\b",
    r"\bAs a language model\b",
    r"\bIn conclusion\b",
    r"\bcutting-edge\b",
]

def compute_fk_grade(text: str) -> float:
    try:
        return float(flesch_kincaid_grade(text))
    except Exception:
        return 12.0

def active_voice_ratio(text: str) -> float:
    # Heuristic: penalize passive markers
    sents = re.split(r"[.!?]\s+", text.strip())
    if not sents: return 1.0
    passive = sum(1 for s in sents if re.search(r"\b(be|been|being|is|was|were|are)\b\s+\w+ed\b", s, re.I))
    return max(0.0, 1.0 - (passive / max(1, len(sents))))

def bad_phrase_count(text: str) -> int:
    total = 0
    for p in BAD_PHRASES:
        total += len(re.findall(p, text))
    return total

def compute_style_score(text: str) -> float:
    fk = compute_fk_grade(text)
    av = active_voice_ratio(text)
    bad = bad_phrase_count(text)
    # Simple blend: 0–1
    score = 0.5 * max(0, (8.0 - min(fk, 16.0)) / 8.0) + 0.5 * av
    if bad > 0: score -= 0.1 * bad
    return max(0.0, min(1.0, score))

def run_style_checks(text: str) -> dict:
    fk = compute_fk_grade(text)
    av = active_voice_ratio(text)
    bad = bad_phrase_count(text)
    score = compute_style_score(text)
    return {
        "fk_grade": fk,
        "active_voice_ratio": av,
        "bad_phrase_count": bad,
        "narrative_style_score": score,
        "qa_pass": (fk <= 8.0 and score >= 0.85 and bad == 0),
        "notes": [
            *(["Readability too hard (FK > 8.0)"] if fk > 8.0 else []),
            *(["Style score < 0.85"] if score < 0.85 else []),
            *(["Filler/AI phrasing present"] if bad > 0 else []),
        ]
    }
