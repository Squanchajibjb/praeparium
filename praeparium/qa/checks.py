from __future__ import annotations
import os, re
from typing import Dict, List

FILLER = [r"\bIn conclusion\b", r"\bIn summary\b", r"\bAt the end of the day\b"]

def _read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def _check_headings(md: str) -> List[str]:
    errs: List[str] = []
    if not md.strip().startswith("# "):
        errs.append("Missing H1 at top")
    h2s = [l for l in md.splitlines() if l.startswith("## ")]
    if len(h2s) < 3:
        errs.append("Fewer than 3 H2s")
    return errs

def _check_links(md: str) -> List[str]:
    errs: List[str] = []
    internal = len(re.findall(r"\]\(/", md))
    external = len(re.findall(r"\]\(https?://", md))
    if external < 2:
        errs.append("Fewer than 2 external links")
    if internal < 1:
        errs.append("Fewer than 1 internal link")
    return errs

def _check_citations(md: str) -> List[str]:
    errs: List[str] = []
    # Inline citations like [Source: CDC]
    if md.count("[Source:") < 3:
        errs.append("Fewer than 3 inline citations [Source: ...]")
    if "## Sources" not in md:
        errs.append("Missing Sources section")
    # Require at least 2 unique titles/links in Sources list
    src_lines = [l for l in md.splitlines() if l.strip().startswith("- [")]
    if len(src_lines) < 2:
        errs.append("Fewer than 2 sources listed")
    return errs

def _check_tables(md: str) -> List[str]:
    # Markdown table heuristic: header divider present
    if "|---" not in md and "| --" not in md:
        return ["No comparison table found"]
    return []

def _check_eeat(md: str) -> List[str]:
    errs: List[str] = []
    if "Preparedness Notes" not in md:
        errs.append("Missing Preparedness Notes section")
    return errs

def _check_ladder_mentions(md: str) -> List[str]:
    # Expect explicit ladder thinking across water pillar
    needles = ["72h", "72 hours", "2w", "two weeks", "30d", "30 days", "ladder"]
    if not any(n.lower() in md.lower() for n in needles):
        return ["No explicit time-ladder references (72h → 2w → 30d+)"]
    return []

def _check_filler(md: str) -> List[str]:
    errs: List[str] = []
    for pat in FILLER:
        if re.search(pat, md, flags=re.I):
            errs.append(f"Contains filler phrase: /{pat}/")
    return errs

def audit_path(path: str) -> Dict[str, List[str]]:
    failed: Dict[str, List[str]] = {}
    for fn in os.listdir(path):
        if not fn.endswith(".md"):
            continue
        p = os.path.join(path, fn)
        md = _read_text(p)
        errs: List[str] = []
        errs += _check_headings(md)
        errs += _check_links(md)
        errs += _check_citations(md)
        errs += _check_tables(md)
        errs += _check_eeat(md)
        errs += _check_ladder_mentions(md)
        errs += _check_filler(md)
        if errs:
            failed[p] = errs
    return failed
