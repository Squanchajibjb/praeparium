from __future__ import annotations
import re

SECTION_ORDER = [
    "TL;DR",
    "Why this matters",
    "How to do it",
    "Related",
    "FAQ",
]

_SCAFFOLD = {
    "TL;DR": (
        "## TL;DR\n"
        "- Keep 4 L / 1 gal per person per day.\n"
        "- Build capacity in steps (3d → 2w → 30d → 90d).\n"
        "- Store in food-grade containers; cool, dark, and labeled.\n\n"
    ),
    "Why this matters": (
        "## Why this matters\n"
        "Water access fails more often than we expect. A small buffer protects hydration, cooking, and hygiene through short outages or boil orders.\n\n"
    ),
    "How to do it": (
        "## How to do it\n"
        "1. Count people and days. Aim for at least 2 weeks.\n"
        "2. Start with sealed bottles or clean, food-grade jugs.\n"
        "3. Add a gravity filter and unscented bleach for disinfection.\n"
        "4. Label and rotate every 6–12 months.\n\n"
    ),
    "Related": (
        "## Related\n"
        "- (Add internal links or leave for renderer’s interlinks.)\n\n"
    ),
    "FAQ": (
        "## FAQ\n"
        "**Do I need a filter if I have bleach?** Filter improves taste and removes particulates; bleach inactivates microbes. Both together are best.\n\n"
    ),
}

def _has_heading(md: str, title: str) -> bool:
    pattern = rf"(?mi)^##\s+{re.escape(title)}\s*$"
    return re.search(pattern, md) is not None

def ensure_scaffold(md: str) -> str:
    """Ensure the five narrative sections exist, append missing ones in canonical order at the end."""
    missing = [t for t in SECTION_ORDER if not _has_heading(md, t)]
    if not missing:
        return md
    # Ensure the doc ends with a blank line, then append missing blocks.
    if not md.endswith("\n"):
        md += "\n"
    md += "\n"
    for t in missing:
        md += _SCAFFOLD[t]
    return md

def _split_overlong_sentence(s: str, limit: int = 28) -> list[str]:
    words = s.split()
    if len(words) <= limit:
        return [s]
    # Try soft splits on ';' and em dashes first
    s = s.replace(" — ", ". ").replace("–", "-").replace(";", ". ")
    # If still long, attempt to split before common joiners.
    joiners = r"\b(and|but|which|that|because|so)\b"
    parts = re.split(f"({joiners})", s)
    if len(" ".join(s.split())) <= limit:
        return [s]
    # Rebuild with stops inserted around joiners to shorten clauses.
    rebuilt = []
    clause = ""
    for chunk in parts:
        if re.fullmatch(joiners, chunk or ""):
            clause = clause.strip()
            if clause:
                rebuilt.append(clause)
            clause = ""
        else:
            clause += (" " if clause else "") + chunk.strip()
    clause = clause.strip()
    if clause:
        rebuilt.append(clause)
    # Fallback if we failed to split meaningfully
    if not rebuilt:
        return [s]
    return [c.strip() for c in rebuilt if c.strip()]

def nudge_fk(md: str) -> str:
    """Light-touch edits that tend to lower FK without changing meaning."""
    lines = md.splitlines()
    out: list[str] = []
    for ln in lines:
        # Leave headings and lists alone
        if ln.startswith("#") or ln.lstrip().startswith(("-", "*", "1.", "2.", "3.")):
            out.append(ln)
            continue
        # Normalize em dashes / semicolons into sentence stops
        ln_norm = ln.replace(" — ", ". ").replace("–", "-").replace(";", ". ")
        # Split into sentences and shorten overlong ones
        sentences = re.split(r"(?<=[.?!])\s+", ln_norm.strip())
        shorter: list[str] = []
        for s in sentences:
            if not s:
                continue
            pieces = _split_overlong_sentence(s)
            for p in pieces:
                p = p.strip()
                if p and not p.endswith((".", "?", "!")):
                    p += "."
                shorter.append(p)
        out.append(" ".join(shorter) if shorter else ln)
    return "\n".join(out)