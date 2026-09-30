"""Create a verified, static Salente product snapshot for the approved Czech campaign."""
from __future__ import annotations

import concurrent.futures
import html
import json
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

OUT = Path(__file__).with_name("salente_products.json")
SITEMAP = "https://eshop.salente.cz/sitemap.xml"
AGENT = "Mozilla/5.0 (compatible; MojeVychytavkyCatalogue/1.0)"
META = re.compile(r"<meta\b([^>]+)>", re.I)
ATTR = re.compile(r'''([:\w-]+)\s*=\s*(["'])(.*?)\2''', re.I | re.S)


def fetch(url: str) -> str:
    request = Request(url, headers={"User-Agent": AGENT, "Accept-Language": "cs-CZ,cs;q=0.9"})
    with urlopen(request, timeout=35) as response:
        return response.read().decode("utf-8", errors="replace")


def metas(page: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for raw in META.findall(page):
        attrs = {key.lower(): html.unescape(value.strip()) for key, _, value in ATTR.findall(raw)}
        key = (attrs.get("property") or attrs.get("itemprop") or attrs.get("name") or "").lower()
        if key and attrs.get("content") and key not in out:
            out[key] = attrs["content"]
    return out


def price(value: str | None) -> int | None:
    if not value:
        return None
    match = re.search(r"\d+(?:[.,]\d+)?", value.replace("\xa0", ""))
    return round(float(match.group(0).replace(",", "."))) if match else None


def product(url: str) -> tuple[dict | None, str | None]:
    try:
        page = fetch(url)
        meta = metas(page)
        title = meta.get("og:title") or meta.get("twitter:title")
        image = meta.get("og:image")
        amount = price(meta.get("product:price:amount") or meta.get("price"))
        # Salente's current Shoptet details expose availability in the rendered page,
        # but not in an Open Graph availability meta field.
        in_stock = "Skladem" in page and "Momentálně nedostupné" not in page and "Vyprodáno" not in page
        if not (title and image and amount is not None):
            return None, "missing title, image or price"
        if amount <= 1:
            return None, "placeholder or missing current price"
        if title.strip().lower().startswith("!bazar!"):
            return None, "used/bazaar item excluded"
        if not in_stock:
            return None, "not currently in stock"
        return {
            "merchant": "Salente",
            "category": "Salente – kompletní sortiment",
            "title": re.sub(r"\s*[|×].*$", "", title).strip(),
            "url": url,
            "image": image,
            "price": amount,
            "currency": meta.get("product:price:currency") or meta.get("pricecurrency") or "CZK",
        }, None
    except Exception as error:
        return None, f"{type(error).__name__}: {error}"


def source_urls() -> list[str]:
    root = ET.fromstring(fetch(SITEMAP))
    ns = {"sm": "http://www.google.com/schemas/sitemap/0.9"}
    urls = []
    for element in root.findall("sm:url", ns):
        loc = element.findtext("sm:loc", namespaces=ns)
        priority = element.findtext("sm:priority", namespaces=ns)
        if loc and priority == "0.9" and loc.startswith("https://eshop.salente.cz/"):
            urls.append(loc)
    return sorted(set(urls))


def main() -> int:
    urls = source_urls()
    products: list[dict] = []
    excluded: list[dict] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        for url, result in zip(urls, pool.map(product, urls)):
            item, reason = result
            if item:
                products.append(item)
            else:
                excluded.append({"url": url, "reason": reason or "unknown"})
    assert len(products) == len({item["url"] for item in products})
    payload = {"observed_at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "source_count": len(urls), "products": products, "excluded": excluded}
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Salente: {len(products)}/{len(urls)} currently orderable; {len(excluded)} excluded")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
