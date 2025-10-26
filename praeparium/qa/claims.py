import json, os, re

def check_claims(md: str, sourcepack_path: str) -> list[str]:
    with open(sourcepack_path, "r", encoding="utf-8") as f:
        sp = json.load(f)
    claims = sp.get("claims_checklist", [])
    errs = []
    # naive presence checks – evolve to regexes per claim later
    musts = {
        "time ladder": r"(72h|72 hours).*(2w|two weeks).*(30d|30 days|month)",
        "rotation": r"rotate|rotation|6–12|6-12",
        "ergonomics": r"(55-?gal|55 gallon|208\s?kg|460\s?lb|floor[- ]?load|lb/ft)",
        "citations": r"\[Source:",
    }
    # example: ensure at least one must per category
    for name, pattern in musts.items():
        if not re.search(pattern, md, re.IGNORECASE | re.DOTALL):
            errs.append(f"Missing required concept: {name}")
    return errs
