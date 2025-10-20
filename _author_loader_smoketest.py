from praeparium.data.author_registry import load_authors
from praeparium.data.loader import load_bundle

authors = load_authors("praeparium/data/registry")
print("Authors loaded:", len(authors))
if authors:
    print("First author:", authors[0].get("author_id"), "-", authors[0].get("display_name"))

bundle = load_bundle("praeparium/data/bundles/mini.yaml")
print("Bundle slug:", bundle.get("bundle_slug"))
print("Articles:", len(bundle.get("article_plan", [])))
print("Authors injected:", len(bundle.get("authors", [])))
