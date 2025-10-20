from __future__ import annotations
import json
from pathlib import Path
import typer

app = typer.Typer(add_completion=False)

@app.command("bundle-generate")
def bundle_generate(bundle: str, out: str = "out"):
    """
    Minimal placeholder that proves the CLI wiring works.
    Replace with your real implementation once the shell detects 'praeparium'.
    """
    outdir = Path(out)
    outdir.mkdir(parents=True, exist_ok=True)
    manifest = {"bundle": Path(bundle).name, "articles": [], "note": "CLI wiring OK"}
    (outdir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    typer.echo(f"Rendered 0 articles → {outdir}")
    typer.echo("✅ CLI wiring OK (placeholder)")

@app.command("qa-report")
def qa_report(out_dir: str = "out"):
    p = Path(out_dir) / "manifest.json"
    if p.exists():
        typer.echo(p.read_text(encoding="utf-8"))
    else:
        typer.echo("No manifests found.")

if __name__ == "__main__":
    app()