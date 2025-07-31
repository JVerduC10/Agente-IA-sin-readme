from ddgs import DDGS


async def search_web(query: str, k: int = 8) -> list[dict]:
    """
    Devuelve la lista [{url,title,snippet}] usando DuckDuckGo.
    Sin claves ni límites estrictos. k = número de resultados.
    """
    hits: list[dict] = []
    with DDGS() as ddg:
        for r in ddg.text(query, safesearch="off", max_results=k):
            hits.append(
                {
                    "url": r["href"],
                    "title": r["title"],
                    "snippet": r["body"],
                }
            )
    return hits
