from __future__ import annotations
from pathlib import Path
import yaml

def load_authors(registry_dir: str | Path) -> list[dict]:
    """Load all authors from data/registry/authors/*.yaml"""
    registry_dir = Path(registry_dir)
    authors_dir = registry_dir / "authors"
    authors = []
    if authors_dir.exists():
        for f in authors_dir.glob("*.y*ml"):
            with open(f, "r", encoding="utf-8") as fh:
                data = yaml.safe_load(fh) or {}
                data.setdefault("author_id", f.stem)
                data.setdefault("display_name", data.get("name") or f.stem)
                data.setdefault("credentials", [])
                data.setdefault("expertise_domains", [])
                data.setdefault("bio", None)
                authors.append(data)
    return authors
