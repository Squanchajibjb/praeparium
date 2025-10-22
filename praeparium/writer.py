from __future__ import annotations
import json, os, pathlib, re
from typing import Dict, Any, List

# OpenAI Python SDK >= 1.0
try:
    from openai import OpenAI  # pip install openai
except Exception:
    OpenAI = None


def _load_sourcepack(path: str) -> Dict[str, Any]:
    # utf-8-sig will transparently strip a BOM if present
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)

def _fix_encoding_glitches(text: str) -> str:
    # Common cp1252/UTF-8 artifacts seen in outputs
    replacements = {
        "â€“": "–",
        "â€”": "—",
        "â€˜": "‘",
        "â€™": "’",
        "â€œ": "“",
        "â€\x9d": "”",
        "â€": "”",
        "â€¢": "•",
        "â€¦": "…",
        "â„¢": "™",
        "â†’": "→",
        "Ã—": "×",
        "Â·": "·",
        "Â": "",
    }
    for bad, good in replacements.items():
        text = text.replace(bad, good)
    return text

def _has_markdown_table(text: str) -> bool:
    return ("|---" in text) or ("| --" in text)

def _build_comparison_table(products: List[dict], columns: List[str]) -> str:
    if not products or not columns:
        return ""
    # Header
    header = "| " + " | ".join(columns) + " |"
    divider = "| " + " | ".join("---" for _ in columns) + " |"
    rows = []
    for p in products:
        row = []
        for c in columns:
            val = p.get(c, "")
            if isinstance(val, list):
                val = ", ".join(str(v) for v in val)
            row.append(str(val))
        rows.append("| " + " | ".join(row) + " |")
    return "\n".join([header, divider, *rows])

def _ensure_sources_section(text: str, sources: List[dict]) -> str:
    if "## Sources" in text:
        return text
    if not sources:
        return text
    lines = ["\n## Sources\n"]
    for s in sources:
        title = s.get("title") or s.get("id") or "Source"
        url = s.get("url", "")
        pub = s.get("publisher")
        label = f"{title}" + (f" ({pub})" if pub else "")
        if url:
            lines.append(f"- [{label}]({url})")
        else:
            lines.append(f"- {label}")
    return text.rstrip() + "\n" + "\n".join(lines) + "\n"

def _inject_byline(text: str, default_author: str = "Praeparium Editorial") -> str:
    # If the doc already has an author line, leave it.
    if re.search(r"(?im)^by\s+.+$", text) or "By " in text[:200]:
        return text
    # Insert after the H1 if present
    lines = text.splitlines()
    if lines and lines[0].startswith("# "):
        title = lines[0]
        rest = lines[1:]
        return "\n".join([title, f"\n*By {default_author}*\n", *rest])
    return f"*By {default_author}*\n\n{text}"

def write_from_sourcepack(sourcepack_path: str, out_dir: str, slug: str | None = None) -> bool:
    """
    Generate a publishable article from a structured Source Pack (JSON).
    Uses writer_prompt_v2.txt for high-quality reasoning, citations, and EEAT output.
    Also enforces:
      - Comparison table (if missing) from products/comparison_columns
      - Sources section from sources[]
      - Minimal byline and encoding cleanup
    """
    sp = _load_sourcepack(sourcepack_path)
    if not sp or "sources" not in sp or "claims_checklist" not in sp:
        print("[FAIL] Source Pack missing mandatory keys: 'sources', 'claims_checklist'")
        return False

    if OpenAI is None:
        print("[FAIL] OpenAI SDK not installed. Run: pip install openai")
        return False

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("[FAIL] OPENAI_API_KEY not set in environment.")
        return False

    org_id = os.getenv("OPENAI_ORG_ID")
    client = OpenAI(api_key=api_key, organization=org_id) if org_id else OpenAI(api_key=api_key)
    model_name = os.getenv("PRAEPARIUM_MODEL", "gpt-4o")

    # --- Prompt template ---
    prompt_path = os.path.join(os.path.dirname(__file__), "writer_prompt_v2.txt")
    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            PROMPT_V2 = f.read()
    except FileNotFoundError:
        print(f"[FAIL] Prompt file not found: {prompt_path}")
        return False

    # Build the user message by embedding the Source Pack JSON
    source_pack_json = json.dumps(sp, ensure_ascii=False, indent=2)
    user_msg = PROMPT_V2.replace("{source_pack_json}", source_pack_json)

    system_msg = (
        "You are Praeparium’s senior preparedness writer. "
        "Follow the STRUCTURE exactly; cite quantitative claims inline. "
        "Return only final Markdown, no commentary."
    )

    try:
        resp = client.chat.completions.create(
            model=model_name,
            temperature=0.25,
            top_p=0.9,
            frequency_penalty=0.1,
            presence_penalty=0.0,
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg},
            ],
        )
    except Exception as e:
        print(f"[FAIL] OpenAI call failed: {e}")
        return False

    text = resp.choices[0].message.content if resp and resp.choices else ""
    if not text or len(text.strip()) < 400:
        print("[FAIL] Model returned empty or too-short content.")
        return False

    # --- Post-process to satisfy QA & EEAT ---
    text = _fix_encoding_glitches(text)
    text = _inject_byline(text)

    products = sp.get("products", [])
    columns  = sp.get("comparison_columns", [])

    if not _has_markdown_table(text) and products and columns:
        table_md = _build_comparison_table(products, columns)
        if table_md:
            text = text.rstrip() + "\n\n## Comparison Table\n" + table_md + "\n"

    text = _ensure_sources_section(text, sp.get("sources", []))

    # --- Always append internal links so QA has at least one internal link ---
    text += (
        "\n**Related:** "
        "[Water Preparedness Time Ladder](/water-preparedness-time-ladder) · "
        "[How to Sanitize Water Containers](/sanitize-water-containers)\n"
    )

    # Write output
    os.makedirs(out_dir, exist_ok=True)
    slug = slug or sp.get("slug") or "best-water-storage-containers"
    out_path = pathlib.Path(out_dir) / f"{slug}.md"

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(text)

    print(f"[OK] Wrote {out_path}")
    return True
