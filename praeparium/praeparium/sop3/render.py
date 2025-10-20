from __future__ import annotations

# Temporary shim: reuse SOP2 renderer until SOP3 is ready.
from praeparium.sop2.render import render_article as _render_sop2

def render_article(bundle, article, outline):
    """
    SOP3 shim: call SOP2 implementation.
    """
    return _render_sop2(bundle, article, outline)