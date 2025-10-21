from __future__ import annotations
import os, pathlib, yaml
from typing import Dict, List
from jinja2 import Environment, FileSystemLoader, StrictUndefined

TEMPLATE_REQUIRED_H2 = {
    "hub":   ["TL;DR","Who this is for","Timeframe ladder","Core decisions","Spokes","FAQs"],
    "review":["Quick verdict","Who it’s for","How we tested","Mini-reviews","Buying factors","Common concerns","FAQs"],
    "guide": ["TL;DR","Step-by-step","Cost, time & tools","Mistakes to avoid","FAQs"],
    "faq":   ["FAQs"],
}

def _load_yaml(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def _env(template_dir: str):
    return Environment(
        loader=FileSystemLoader(template_dir),
        undefined=StrictUndefined,
        autoescape=False,
        trim_blocks=True,
        lstrip_blocks=True,
    )

def _required_h2s_ok(md_text: str, required: list[str]) -> bool:
    found = [line.strip("# ").strip() for line in md_text.splitlines() if line.startswith("## ")]
    s = set(found)
    return all(h in s for h in required)

def _mk_link(title: str, slug: str) -> Dict[str, str]:
    return {"title": title, "slug": slug, "href": f"/{slug}"}

def render_bundle(bundle_yaml: str, out_dir: str) -> bool:
    plan = _load_yaml(bundle_yaml)
    items: List[Dict] = plan.get("items", [])

    # Build lookups
    by_slug = {i["slug"]: i for i in items}
    hubs = [i for i in items if i.get("type") == "hub"]
    spokes = [i for i in items if i.get("type") in {"guide","review","faq"}]

    # Defaults (optional) at bundle root so you don’t repeat yourself
    default_external_links = plan.get("defaults", {}).get("external_links", [])
    default_external_source = plan.get("defaults", {}).get("external_source", "")

    # Precompute link groups
    hub_links_all = [_mk_link(h["title"], h["slug"]) for h in hubs]
    siblings_by_hub: Dict[str, List[Dict[str,str]]] = {}
    for h in hubs:
        hslug = h["slug"]
        siblings_by_hub[hslug] = [
            _mk_link(x["title"], x["slug"])
            for x in spokes
            if x.get("hub_slug") == hslug
        ]

    # Render
    base_dir = pathlib.Path(__file__).parent
    tdir = base_dir / "templates"
    env = _env(str(tdir))
    os.makedirs(out_dir, exist_ok=True)

    ok = True
    template_map = {"hub":"hub.md.j2","review":"review.md.j2","guide":"guide.md.j2","faq":"faq.md.j2"}

    for item in items:
        atype = item["type"]
        slug  = item["slug"]
        tmpl  = template_map.get(atype)
        if not tmpl:
            print(f"[WARN] Unknown type {atype} for {slug}")
            ok = False
            continue

        # Inject auto-links (no manual YAML work)
        ctx = dict(item)

        # Provide external links fallbacks so QA passes without rework
        ctx.setdefault("external_links", default_external_links)
        ctx.setdefault("external_source", default_external_source)

        if atype == "hub":
            # hub cross-refs: all other hubs + its own spokes
            ctx["other_hubs"] = [l for l in hub_links_all if l["slug"] != slug]
            ctx["bundle_spokes"] = siblings_by_hub.get(slug, [])
        else:
            # spoke cross-refs: link back to its hub + sibling spokes
            hslug = item.get("hub_slug")
            if hslug and hslug in by_slug:
                ctx["hub_link"] = _mk_link(by_slug[hslug]["title"], hslug)
                ctx["sibling_spokes"] = [
                    l for l in siblings_by_hub.get(hslug, []) if l["slug"] != slug
                ]
            else:
                ctx["hub_link"] = None
                ctx["sibling_spokes"] = []

        md = env.get_template(tmpl).render(**ctx)

        if not _required_h2s_ok(md, TEMPLATE_REQUIRED_H2.get(atype, [])):
            print(f"[FAIL] Missing required H2(s) in {slug}.md")
            ok = False

        out_path = pathlib.Path(out_dir) / f"{slug}.md"
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(md)
        print(f"[OK] Wrote {out_path}")

    return ok
