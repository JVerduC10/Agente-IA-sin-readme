import re
import statistics

import aiohttp
import trafilatura


async def scrape_pct(url: str, keyword: str = "mujer") -> list[float]:
    """Descarga la página y extrae porcentajes precedidos por la palabra clave."""
    async with aiohttp.ClientSession() as sess:
        async with sess.get(url, timeout=20) as resp:
            html = await resp.text()
    text = trafilatura.extract(html) or ""
    pattern = rf"(\d{{1,2}}(?:[.,]\d)?)\s?%[^\n]{{0,20}}\b{keyword}"
    return [float(p.replace(",", ".")) for p in re.findall(pattern, text, flags=re.I)]


def aggregate(values: list[float]) -> float | None:
    return statistics.median(values) if values else None
