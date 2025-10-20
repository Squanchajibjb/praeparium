import requests

def publish_markdown(site_url:str, user:str, app_password:str, title:str, content_md:str, slug:str, status:str="draft"):
    r = requests.post(
        f"{site_url}/wp-json/wp/v2/posts",
        auth=(user, app_password),
        json={"title": title, "content": content_md, "slug": slug, "status": status},
        timeout=30
    )
    r.raise_for_status()
    return r.json().get("link")
