from ddgs import DDGS

def real_search(query: str, max_results: int = 5):
    results = []

    with DDGS() as ddgs:
        for r in ddgs.text(query, max_results=max_results):
            results.append({
                "title": r.get("title", ""),
                "snippet": r.get("body", ""),  # DDGS 用 body
                "url": r.get("href", "")
            })

    return results