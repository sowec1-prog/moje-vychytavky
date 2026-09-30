"""Validate Mobilegear's public sitemap candidates into an active-product snapshot.

The public sitemap has no availability state. Each detail page is therefore
checked before a card can be added. Progress is append-only and resumable.
"""
from __future__ import annotations

import concurrent.futures
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).parent
PROGRESS = ROOT / "mobilegear_harvest_progress.jsonl"
OUT = ROOT / "mobilegear_products.json"
SITEMAPS = (
    "https://mobilegear-eshop.s3.eu-central-1.amazonaws.com/prod/sitemap/variants-1-cs.xml",
    "https://mobilegear-eshop.s3.eu-central-1.amazonaws.com/prod/sitemap/variant-items-1-cs.xml",
)
AGENT = "Mozilla/5.0 (compatible; MojeVychytavkyCatalogue/1.0)"
META = re.compile(r"<meta\b([^>]+)>", re.I)
ATTR = re.compile(r'''([:\w-]+)\s*=\s*(["'])(.*?)\2''', re.I | re.S)
TAG = re.compile(r"<[^>]+>")
PRICE_BOX = re.compile(r"<[^>]*class=[\"'][^\"']*sale-box__price[^\"']*[\"'][^>]*>(.*?)</[^>]+>", re.I | re.S)


def get(url: str) -> str:
    request = Request(url, headers={"User-Agent": AGENT, "Accept-Language": "cs-CZ,cs;q=0.9"})
    with urlopen(request, timeout=35) as response:
        return response.read().decode("utf-8", errors="replace")


def meta(page: str, key: str) -> str | None:
    for raw in META.findall(page):
        attrs = {k.lower(): v.strip() for k, _, v in ATTR.findall(raw)}
        if (attrs.get("property") or attrs.get("name")) == key:
            return attrs.get("content")
    return None


def price(page: str) -> int | None:
    match = PRICE_BOX.search(page)
    if match:
        text = TAG.sub(" ", match.group(1)).replace("&nbsp;", " ")
        digits = re.search(r"(?:\d[\d\s\xa0]*)", text)
        if digits:
            return int(re.sub(r"\D", "", digits.group(0)))
    # Some accessory variants populate the visible price client-side but expose
    # the same current price in the server-rendered commerce analytics payload.
    fallback = re.search(r'"price"\s*:\s*(\d+(?:[.,]\d+)?)', page)
    return round(float(fallback.group(1).replace(",", "."))) if fallback else None


def validate(url: str) -> dict[str, object]:
    try:
        page = get(url)
        title = meta(page, "og:title") or meta(page, "twitter:title")
        if not title:
            title_match = re.search(r"<title[^>]*>(.*?)</title>", page, re.I | re.S)
            title = TAG.sub(" ", title_match.group(1)).strip() if title_match else None
        image = meta(page, "og:image")
        current = price(page)
        # Stock is checked from the product detail, never inferred from sitemap
        # membership. Mobilegear labels the detail field itself "Skladem".
        in_stock = "Skladem" in page and "Vyprodáno" not in page
        if not in_stock:
            return {"url": url, "status": "excluded", "reason": "not explicitly in stock"}
        if not title or not image or not current:
            return {"url": url, "status": "error", "reason": "missing title, image or current price"}
        return {
            "url": url,
            "status": "ok",
            "merchant": "Mobilegear",
            "category": "Mobilegear – kompletní sortiment",
            "title": re.sub(r"\s*[|×].*$", "", title).strip(),
            "image": image,
            "price": current,
            "currency": "CZK",
        }
    except Exception as error:
        return {"url": url, "status": "error", "reason": f"{type(error).__name__}: {error}"}


def candidates() -> list[str]:
    urls: set[str] = set()
    for sitemap in SITEMAPS:
        urls.update(re.findall(r"<loc>(.*?)</loc>", get(sitemap), flags=re.I))
    return sorted(urls)


def prior() -> dict[str, dict]:
    if not PROGRESS.exists():
        return {}
    rows = {}
    for line in PROGRESS.read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        rows[row["url"]] = row
    return rows


def main() -> int:
    urls = candidates()
    done = prior()
    # Retry network/parse errors on every run; previously verified outcomes stay cached.
    pending = [url for url in urls if url not in done or done[url]["status"] == "error"]
    print(f"Mobilegear candidates={len(urls)} already_checked={len(done)} pending={len(pending)}", flush=True)
    with PROGRESS.open("a", encoding="utf-8") as log, concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        for number, row in enumerate(pool.map(validate, pending), start=1):
            log.write(json.dumps(row, ensure_ascii=False) + "\n")
            log.flush()
            if number % 100 == 0 or number == len(pending):
                print(f"checked {len(done) + number}/{len(urls)}", flush=True)
    rows = prior()
    if len(rows) != len(urls):
        print("incomplete progress; rerun to continue", file=sys.stderr)
        return 1
    products = [rows[url] for url in urls if rows[url]["status"] == "ok"]
    payload = {
        "observed_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source_candidates": len(urls),
        "products": products,
        "excluded": sum(row["status"] == "excluded" for row in rows.values()),
        "errors": sum(row["status"] == "error" for row in rows.values()),
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"verified in-stock Mobilegear products={len(products)} errors={payload['errors']}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
