# praeparium/data/loader.py
from __future__ import annotations
from pathlib import Path
import yaml, json
from .author_registry import load_authors
from .models import Bundle, EditorialTargets

def load_bundle(bundle_path: str | Path) -> Bundle:
    bundle_path = Path(bundle_path)
    with open(bundle_path, "r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) if bundle_path.suffix in (".yml", ".yaml") else json.load(fh)

    # Attach authors from registry
    root = Path(__file__).resolve().parent.parent.parent
    registry_dir = root / "praeparium" / "data" / "registry"
    data["authors"] = load_authors(registry_dir)

    # Coerce editorial_targets (if present) into the model; else default applies
    if "editorial_targets" in data and isinstance(data["editorial_targets"], dict):
        data["editorial_targets"] = EditorialTargets(**data["editorial_targets"])

    return Bundle(**data)
