from __future__ import annotations
import typer, os
from .sop3.render import render_bundle
from .qa.checks import audit_path
from .writer import write_from_sourcepack  # NEW

app = typer.Typer(help="Praeparium content automation CLI")

@app.command("bundle-generate")
def bundle_generate(plan: str, out: str = "out"):
    """
    If 'plan' ends with .json, treat it as a Source Pack and generate a single article.
    Otherwise treat as YAML bundle with items[] and render templates.
    """
    ext = os.path.splitext(plan)[1].lower()
    if ext == ".json":
        ok = write_from_sourcepack(plan, out)
    else:
        ok = render_bundle(plan, out)

    if not ok:
        raise typer.Exit(code=1)
    typer.echo(f"✅ Generated to {out}")

@app.command("qa-report")
def qa_report(path: str = "out"):
    """Run QA checks over generated markdown files."""
    failed = audit_path(path)
    if failed:
        typer.echo("❌ QA failures detected:")
        for f, errs in failed.items():
            for e in errs:
                typer.echo(f" - {f}: {e}")
        raise typer.Exit(code=2)
    typer.echo("✅ QA passed")
