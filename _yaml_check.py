import yaml, sys
with open(r"praeparium\data\bundles\water.yaml","r",encoding="utf-8") as f:
    data = yaml.safe_load(f)
print("bundle_slug:", data.get("bundle_slug"))
print("articles:", len(data.get("article_plan", [])))
