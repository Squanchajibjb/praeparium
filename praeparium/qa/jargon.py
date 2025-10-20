import re

BANNED = [
    "boil the ocean","move the needle","low-hanging fruit","paradigm shift",
    "win-win","synergy","circle back","KPIs and OKRs","touch base","leverage (as verb)",
    "mission-critical","cutting-edge","next-gen","state-of-the-art",
]

def find_jargon(md: str):
    low = md.lower()
    hits = [p for p in BANNED if p in low]
    return sorted(set(hits))
