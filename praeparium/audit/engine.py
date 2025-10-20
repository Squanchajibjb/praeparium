from __future__ import annotations
from pathlib import Path
from typing import Dict, Any, List
import yaml

# Method pack filenames expected to live in the same folder as the bundle
REQUIRED_METHOD_FILES: Dict[str, str] = {
    "objectives": "objectives.yaml",
    "requirements": "requirements.yaml",
    "design": "design.md",
    "deployment": "deployment.yaml",
}


def _read_yaml(p: Path) -> Dict[str, Any]:
    """
    Read YAML with BOM tolerance and return {} on empty files.
    Return {"__error__": "..."} on parse errors so callers can report nicely.
    """
    try:
        # utf-8-sig will strip a UTF-8 BOM if present
        text = p.read_text(encoding="utf-8-sig")
        return yaml.safe_load(text) or {}
    except Exception as e:
        return {"__error__": str(e)}


def find_methodology_files(bundle_path: str | Path) -> Dict[str, Path]:
    """Locate methodology files in the same folder as the bundle."""
    bundle_path = Path(bundle_path).resolve()
    root = bundle_path.parent
    found: Dict[str, Path] = {}
    for key, fname in REQUIRED_METHOD_FILES.items():
        fp = root / fname
        if fp.exists():
            found[key] = fp
    return found


def audit_bundle(bundle_path: str | Path) -> Dict[str, Any]:
    """
    Audit that the methodology files exist and have minimally sane content
    for pre-publication checks.
    """
    results: Dict[str, Any] = {
        "bundle": str(Path(bundle_path).resolve()),
        "files": {},
        "errors": [],
        "warnings": [],
        "pass": True,
    }

    files = find_methodology_files(bundle_path)
    results["files"] = {k: str(v) for k, v in files.items()}

    # ---- Presence checks
    for key in REQUIRED_METHOD_FILES.keys():
        if key not in files:
            results["errors"].append(f"Missing {key} file: {REQUIRED_METHOD_FILES[key]}")
    if results["errors"]:
        results["pass"] = False  # keep auditing for more feedback

    # ---- objectives.yaml sanity
    if "objectives" in files:
        obj = _read_yaml(files["objectives"])
        if "__error__" in obj:
            results["errors"].append(f"objectives.yaml unreadable: {obj['__error__']}")
        else:
            if not obj.get("goal"):
                results["warnings"].append("objectives.yaml: missing 'goal'")
            if not obj.get("personas"):
                results["warnings"].append("objectives.yaml: missing 'personas'")

    # ---- requirements.yaml sanity
    if "requirements" in files:
        req = _read_yaml(files["requirements"])
        if "__error__" in req:
            results["errors"].append(f"requirements.yaml unreadable: {req['__error__']}")
        else:
            et = (req.get("editorial_targets") or {})
            if not et:
                results["warnings"].append("requirements.yaml: editorial_targets missing")
            else:
                # Very loose guardrail; FK > 10 is often too hard for broad audiences
                try:
                    if float(et.get("fk_max", 8.0)) > 10.0:
                        results["warnings"].append("requirements.yaml: fk_max unusually high (>10)")
                except Exception:
                    results["warnings"].append("requirements.yaml: fk_max not a number")

            # Encourage explicit pack list even if empty
            if "domain_validation_packs" not in req:
                results["warnings"].append("requirements.yaml: domain_validation_packs missing")

    # ---- deployment.yaml sanity
    if "deployment" in files:
        dep = _read_yaml(files["deployment"])
        if "__error__" in dep:
            results["errors"].append(f"deployment.yaml unreadable: {dep['__error__']}")
        else:
            # Support both the new structure (review: reviewer_signoff: {...})
            # and a legacy top-level reviewer_signoff for compatibility.
            review = dep.get("review") if isinstance(dep.get("review"), dict) else {}
            signoff = review.get("reviewer_signoff") or dep.get("reviewer_signoff")

            if not (isinstance(signoff, dict) and signoff.get("name") and signoff.get("date")):
                results["errors"].append("deployment.yaml: reviewer_signoff missing name/date")
            else:
                # Optional niceties
                required_roles = review.get("required_roles")
                if not required_roles:
                    results["warnings"].append("deployment.yaml: review.required_roles missing")
                else:
                    role = signoff.get("role")
                    if role and role not in required_roles:
                        results["warnings"].append(
                            "deployment.yaml: signoff role not in review.required_roles"
                        )

            # Checklist helpfulness (warn if some common items are missing)
            checklist = dep.get("checklist") or []
            expected_flags = [
                "interlinks_validated",
                "style_passed",
                "fk_within_target",
                "narrative_flow_present",
                "reviewer_signoff_recorded",
            ]
            for flag in expected_flags:
                if flag not in checklist:
                    results["warnings"].append(f"deployment.yaml: checklist missing '{flag}'")

            # Targets block optional but useful for downstream steps
            targets = dep.get("targets") or {}
            if not targets:
                results["warnings"].append("deployment.yaml: targets missing (preview/out dirs)")
            else:
                if not targets.get("markdown_out_dir"):
                    results["warnings"].append("deployment.yaml: targets.markdown_out_dir missing")
                if not targets.get("preview_dir"):
                    results["warnings"].append("deployment.yaml: targets.preview_dir missing")

    # Final PASS/FAIL
    if results["errors"]:
        results["pass"] = False

    return results
