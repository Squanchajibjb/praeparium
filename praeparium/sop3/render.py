from __future__ import annotations
import importlib

def _resolve_render():
    candidates = (
        "praeparium.sop2.render",   # common layout: sop2/render.py
        "praeparium.sop2",          # render_article exposed at package level
        "praeparium.post.render",   # legacy layout some repos used
    )
    last_err = None
    for modname in candidates:
        try:
            mod = importlib.import_module(modname)
            if hasattr(mod, "render_article"):
                return getattr(mod, "render_article")
        except Exception as e:  # keep trying
            last_err = e
    msg = "Could not locate SOP2 render_article in any of: " + ", ".join(candidates)
    if last_err:
        msg += f" (last error: {last_err})"
    raise ImportError(msg)

_render_sop2 = _resolve_render()

def render_article(bundle, article, outline):
    """SOP3 shim → delegate to whichever SOP2 renderer is available."""
    return _render_sop2(bundle, article, outline)