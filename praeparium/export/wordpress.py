# praeparium/export/wordpress.py
from __future__ import annotations
import argparse, datetime as dt, html, json, os, pathlib, re, sys

# Optional dependency: python-markdown
try:
    import markdown  # pip install markdown
except Exception:
    markdown = None

HTML_SHELL = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{title}</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  {jsonld}
  <style>
    body{{max-width:820px;margin:2rem auto;font-family:system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif;line-height:1.6;padding:0 1rem;}}
    pre,code{{background:#f6f8fa}}
    pre{{padding:1rem;overflow:auto}}
    table{{border-collapse:collapse;width:100%}}
    th,td{{border:1px solid #e5e7eb;padding:.5rem;text-align:left}}
    blockquote{{border-left:4px solid #e5e7eb;padding-left:1rem;color:#444}}
  </style>
</head>
<body>
{body}
</body>
</html>
"""

def _read_text(p: pathlib.Path) -> str:
    return p.read_text(encoding="utf-8")

def _first_h1(md: str) -> str | None:
    for line in md.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return None

def _md_to_html(md: str) -> str:
    if markdown is None:
        # Fallback: minimal escaping so you still get an .html file
        esc = html.escape(md).replace("\n", "<br>\n")
        return f"<pre>{esc}</pre>"
    # Reasonable defaults; add more extensions later if needed
    return markdown.markdown(
        md,
        extensions=["extra", "toc", "sane_lists", "tables", "fenced_code"]
    )

def _mk_jsonld(headline: str, slug: str, base_url: str | None,
               author: str | None, publish_date: str | None) -> str:
    url = f"{base_url.rstrip('/')}/{slug}" if base_url else None
    ld = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": headline,
        "author": author or "Praeparium Editorial",
        "publisher": "Praeparium",
        "datePublished": publish_date or dt.date.today().isoformat(),
    }
    if url:
        ld["url"] = url
    return '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + "</script>"

def export_dir(src: str, out: str, base_url: str | None = None) -> int:
    src_p = pathlib.Path(src)
    out_p = pathlib.Path(out)
    out_p.mkdir(parents=True, exist_ok=True)

    md_files = [p for p in src_p.glob("*.md")]
    if not md_files:
        print(f"[WARN] No .md files found in {src_p}")
        return 0

    written = 0
    for md_path in md_files:
        md_text = _read_text(md_path)

        # Title & slug
        title = _first_h1(md_text) or md_path.stem.replace("-", " ").title()
        slug = md_path.stem

        # Optional author/published from footer patterns (non-fatal if missing)
        author = None
        published = None

        # Look for a simple “By NAME” line:
        m_author = re.search(r"^_?By\s+(.+?)[._]?$", md_text, flags=re.I | re.M)
        if m_author:
            author = m_author.group(1).strip()

        # ISO date in the doc (first match)
        m_date = re.search(r"\b(20\d{2}-\d{2}-\d{2})\b", md_text)
        if m_date:
            published = m_date.group(1)

        body_html = _md_to_html(md_text)
        jsonld = _mk_jsonld(title, slug, base_url, author, published)
        html_text = HTML_SHELL.format(title=html.escape(title), jsonld=jsonld, body=body_html)

        out_file = out_p / f"{slug}.html"
        out_file.write_text(html_text, encoding="utf-8")
        print(f"[OK] {out_file}")
        written += 1

    return written

def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Export Markdown to static HTML with JSON-LD.")
    parser.add_argument("--src", required=True, help="Source directory containing .md files")
    parser.add_argument("--out", required=True, help="Output directory for .html files")
    parser.add_argument("--base-url", default=None, help="Base site URL for canonical (e.g., https://www.praeparium.com)")
    args = parser.parse_args(argv)

    try:
        count = export_dir(args.src, args.out, base_url=args.base_url)
    except Exception as e:
        print(f"[FAIL] Export failed: {e}")
        return 1

    print(f"✅ Exported {count} file(s) to {args.out}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
