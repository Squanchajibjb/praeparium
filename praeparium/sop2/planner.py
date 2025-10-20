from praeparium.data.models import Bundle, ArticlePlan

def build_outline(bundle: Bundle, article: ArticlePlan) -> dict:
    personas = ", ".join(article.personas) if article.personas else "readers"
    return {
        "outline_md": f"# {article.title}\n\n## TL;DR\n- Key takeaways\n\n## Who this helps\n- {personas}\n"
    }
