from __future__ import annotations

def validate_pfas_claim(article_md: str, bundle_vars: dict) -> list[str]:
    errors = []
    mentions_pfas = "PFAS" in article_md.upper()
    mentions_cert = ("NSF/ANSI 53" in article_md.upper()) or ("NSF/ANSI 401" in article_md.upper())
    if mentions_pfas and not mentions_cert:
        errors.append("PFAS claim present but missing NSF/ANSI 53 or 401 reference.")
    return errors
