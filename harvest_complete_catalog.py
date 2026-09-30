"""Create a verified full, currently-orderable Cubenest + EVOLVEO snapshot.

This is intentionally an offline build input. Public static builds never scrape
merchants themselves. Mobilegear is handled separately because its sitemap has
9,182 candidate variants and each needs an availability check.
"""
from __future__ import annotations

import concurrent.futures
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

OUT = Path(__file__).with_name("complete_catalog.json")
AGENT = "Mozilla/5.0 (compatible; MojeVychytavkyCatalogue/1.0)"
SOURCES = (
    ("Cubenest", "https://www.cubenest.cz/sitemap.xml", re.compile(r"https://www\.cubenest\.cz/p-\d+/[^?#]+$")),
    ("EVOLVEO", "https://eshop.evolveo.cz/sitemap.xml", re.compile(r"https://eshop\.evolveo\.cz/evolveo-[^?#]+/$")),
)
META = re.compile(r"<meta\b([^>]+)>", re.I)
ATTR = re.compile(r'''([:\w-]+)\s*=\s*(["'])(.*?)\2''', re.I | re.S)


def fetch(url: str) -> str:
    req = Request(url, headers={"User-Agent": AGENT, "Accept-Language": "cs-CZ,cs;q=0.9"})
    with urlopen(req, timeout=35) as response:
        return response.read().decode("utf-8", errors="replace")


def meta_values(page: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw in META.findall(page):
        attrs = {key.lower(): value.strip() for key, _, value in ATTR.findall(raw)}
        key = attrs.get("property") or attrs.get("itemprop") or attrs.get("name")
        content = attrs.get("content")
        if key and content and key.lower() not in values:
            values[key.lower()] = content
    return values


def number(value: str | None) -> int | None:
    if not value:
        return None
    match = re.search(r"\d+(?:[.,]\d+)?", value)
    return round(float(match.group(0).replace(",", "."))) if match else None


def product(merchant: str, url: str) -> tuple[dict | None, str | None]:
    try:
        page = fetch(url)
        meta = meta_values(page)
        price = number(meta.get("price") or meta.get("product:price:amount"))
        title = meta.get("og:title") or meta.get("twitter:title")
        image = meta.get("og:image")
        availability = (meta.get("availability") or meta.get("product:availability") or "").lower()
        if not title or not image or price is None:
            return None, "missing title, image or structured price"
        if "outofstock" in availability or "out of stock" in availability:
            return None, "out of stock"
        return {
            "merchant": merchant,
            "category": f"{merchant} – kompletní sortiment",
            "title": re.sub(r"\s*[|×].*$", "", title).strip(),
            "url": url,
            "image": image,
            "price": price,
            "currency": meta.get("pricecurrency") or meta.get("product:price:currency") or "CZK",
        }, None
    except Exception as error:
        return None, f"{type(error).__name__}: {error}"


def source_urls(sitemap: str, pattern: re.Pattern[str]) -> list[str]:
    urls = re.findall(r"<loc>(.*?)</loc>", fetch(sitemap), flags=re.I)
    return sorted(set(url for url in urls if pattern.fullmatch(url)))


def main() -> int:
    verified: list[dict] = []
    failed: dict[str, list[dict[str, str]]] = {}
    source_counts: dict[str, int] = {}
    for merchant, sitemap, pattern in SOURCES:
        urls = source_urls(sitemap, pattern)
        source_counts[merchant] = len(urls)
        merchant_products: list[dict] = []
        errors: list[dict[str, str]] = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
            for url, result in zip(urls, pool.map(lambda item: product(merchant, item), urls)):
                item, error = result
                if item:
                    merchant_products.append(item)
                else:
                    errors.append({"url": url, "reason": error or "unknown"})
        print(f"{merchant}: {len(merchant_products)}/{len(urls)} currently orderable, {len(errors)} excluded")
        verified.extend(merchant_products)
        failed[merchant] = errors
    assert len({p['url'] for p in verified}) == len(verified)
    payload = {
        "observed_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source_counts": source_counts,
        "products": verified,
        "excluded": failed,
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(verified)} verified products to {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
