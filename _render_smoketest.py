from praeparium.sop3.render import render_article

bundle = {"article_plan": [{"slug":"filters-for-preppers","title":"Filters for Preppers"}]}
article = {
    "title": "Test Hub Article",
    "primary_keyword": "water storage",
    "personas": ["urban preppers","families"],
    "template": "hub.md.j2",
    "interlink_out": ["filters-for-preppers"],
}
outline = {"why": "Because hydration matters more than anything else."}

md = render_article(bundle, article, outline)
print(md)
