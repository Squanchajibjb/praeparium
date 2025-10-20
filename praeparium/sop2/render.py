from __future__ import annotations
from typing import Any, Dict

def _as_dict(x: Any) -> dict:
    if isinstance(x, dict):
        return x
    if hasattr(x, "model_dump"):
        return x.model_dump()
    return getattr(x, "__dict__", {}) or {}

def render_article(bundle: Any, article: Any, outline: Dict[str, Any] | None = None) -> str:
    a = _as_dict(article)
    slug = a.get("slug", "untitled")
    title = a.get("title") or slug.replace("-", " ").title()
    md = f"""# {title}

## TL;DR
Short, plain summary in simple sentences.

## Why
Why this topic matters and who it’s for.

## How
How we approached this (criteria, constraints, quick method), explained in short sentences.

## Top picks
- Item 1 — one-sentence benefit.
- Item 2 — one-sentence benefit.

## Related
Links or references to related guides or tools.

## FAQ
**Common question?** One-sentence, plain answer.
"""
    return md