import json, yaml
from .models import Bundle

def load_bundle(path: str) -> Bundle:
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) if path.endswith((".yml",".yaml")) else json.load(f)
    return Bundle(**data)
