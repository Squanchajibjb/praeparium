from __future__ import annotations
import os, re
from typing import Dict, List

FILLER = [r"\bIn conclusion\b", r"\bIn summary\b", r"\bAt the end of the day\b"]

def _read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def _check_headings(md: str) -> List[str]:
    errs = []
    if not md.strip().startswith("# "):
        errs.append("Missing H1 at top")
    h2s = [l for l in md.splitlines() if l.startswith("## ")]
    if len(h2s) < 3:
        errs.append("Fewer than 3 H2s")
    return errs

def _check_links(md: str) -> List[str]:
    errs = []
    internal = len(re.findall(r"\]\(/", md))
    external = len(re.findall(r"\]\(https?://", md))
    if external < 2: errs.append("Fewer than 2 external links")
    if internal < 1: errs.append("Fewer than 1 internal link")
    return errs

def _check_filler(md: str) -> List[str]:
    errs = []
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
        errs = []
        errs += _check_headings(md)
        errs += _check_links(md)
        errs += _check_filler(md)
        if errs:
            failed[p] = errs
    return failed
