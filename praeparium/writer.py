from __future__ import annotations
import json, os, pathlib
from typing import Dict, Any

# OpenAI Python SDK >= 1.0
try:
    from openai import OpenAI  # pip install openai
except Exception:
    OpenAI = None

BOXED_PROMPT_TEMPLATE = """You are writing a publishable review article for general readers.
Use ONLY the content provided in <source_pack> for facts/claims.
Do not invent statistics; cite quantitative claims immediately after the sentence [Source: ShortName].

STRUCTURE (exactly, no extra sections):
# H1: Best Water Storage Containers (2025)
> Quick Verdict: (2 sentences)

## Ladder Context
(3–5 sentences tying choices to 72h→2w→30d; include explicit ladder words.)

## Ergonomics & Floor Loading
(2 short paragraphs; must include: 55-gal ≈ 208 kg/460 lb; typical live load ~40–50 lb/ft² / 200–250 kg/m²; distribution advice for upper floors.)

## Container Types
### Stackable 5-gallon cubes — best for apartments
(≥110 words; rotation convenience)
### 55-gallon barrels — best for garages
(≥110 words; pumps; immobility warning)
### Collapsible 20L cubes — flexible overflow
(≥110 words; puncture caveat)
### Inflatable bathtub bladders — 72-hour stopgap
(≥110 words; single-use; stopper warning; disposal)

## Rotation & Maintenance
(1 paragraph: 6–12 months rotation; label, drain/refill; sanitization link)

## Forum Insight
(2–3 sentences paraphrasing ONE lived experience from the pack; attribute as “Prepper forum user”.)

## FAQs
(2 Q&A from the pack)

## Sources
(List the 4–6 provided sources as markdown bullets with titles and URLs)

STYLE GUARDRAILS:
- Plain, active voice. No bullet lists except in Sources.
- Minimum 110 words per subsection under “Container Types”.
- No generic filler (“in conclusion”, “overall”).
- Do not change headings or their order.
- Never summarize or omit required items in the “claims_checklist”.

<source_pack>
{source_pack_json}
</source_pack>
"""

def _load_sourcepack(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def write_from_sourcepack(sourcepack_path: str, out_dir: str, slug: str | None = None) -> bool:
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

    # Choose a solid reasoning/text model you have access to.
    # Adjust model name to your account’s available models (e.g., "gpt-4.1" / "gpt-4o" / "gpt-4o-mini").
    model_name = os.getenv("PRAEPARIUM_MODEL", "gpt-4o")

    source_pack_json = json.dumps(sp, ensure_ascii=False, indent=2)
    system = "Follow the STRUCTURE exactly; deviations are errors. Cite quantitative claims inline."
    user = BOXED_PROMPT_TEMPLATE.format(source_pack_json=source_pack_json)

    try:
        resp = client.chat.completions.create(
            model=model_name,
            temperature=0.25,
            top_p=0.9,
            frequency_penalty=0.1,
            presence_penalty=0.0,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )
    except Exception as e:
        print(f"[FAIL] OpenAI call failed: {e}")
        return False

    text = resp.choices[0].message.content if resp and resp.choices else ""
    if not text or len(text.strip()) < 400:
        print("[FAIL] Model returned empty/too short content.")
        return False

        os.makedirs(out_dir, exist_ok=True)
    # derive a filename
    slug = slug or sp.get("slug") or "best-water-storage-containers"
    out_path = pathlib.Path(out_dir) / f"{slug}.md"

    # Write the model output
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(text)

    # --- NEW: Always append internal links so QA has at least one internal link ---
    with open(out_path, "a", encoding="utf-8") as f:
        f.write("\n**Related:** [Water Preparedness Time Ladder](/water-preparedness-time-ladder) · [How to Sanitize Water Containers](/sanitize-water-containers)\n")
    # ------------------------------------------------------------------------------

    print(f"[OK] Wrote {out_path}")
    return True

    
        
