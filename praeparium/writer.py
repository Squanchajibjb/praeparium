from __future__ import annotations
import json, os, pathlib
from typing import Dict, Any

# OpenAI Python SDK >= 1.0
try:
    from openai import OpenAI  # pip install openai
except Exception:
    OpenAI = None


def _load_sourcepack(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_from_sourcepack(sourcepack_path: str, out_dir: str, slug: str | None = None) -> bool:
    """
    Generate a publishable article from a structured Source Pack (JSON).
    Uses writer_prompt_v2.txt for high-quality reasoning, citations, and EEAT output.
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

    client = OpenAI(api_key=api_key)
    model_name = os.getenv("PRAEPARIUM_MODEL", "gpt-4o")

    # --- STEP 2: Load the new prompt template (writer_prompt_v2.txt) ---
    prompt_path = os.path.join(os.path.dirname(__file__), "writer_prompt_v2.txt")
    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            PROMPT_V2 = f.read()
    except FileNotFoundError:
        print(f"[FAIL] Prompt file not found: {prompt_path}")
        return False
    # ------------------------------------------------------------------

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

    # Write output
    os.makedirs(out_dir, exist_ok=True)
    slug = slug or sp.get("slug") or "best-water-storage-containers"
    out_path = pathlib.Path(out_dir) / f"{slug}.md"

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(text)

    # --- Always append internal links so QA has at least one internal link ---
    with open(out_path, "a", encoding="utf-8") as f:
        f.write(
            "\n**Related:** "
            "[Water Preparedness Time Ladder](/water-preparedness-time-ladder) · "
            "[How to Sanitize Water Containers](/sanitize-water-containers)\n"
        )
    # -------------------------------------------------------------------------

    print(f"[OK] Wrote {out_path}")
    return True
