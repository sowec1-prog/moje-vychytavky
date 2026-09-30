"""Fetch a checked price snapshot for every public product link.

Run before static builds whenever catalogue prices need to be refreshed. It writes
product_prices.json only when a product page returns a valid structured CZK price.
"""
from __future__ import annotations

import concurrent.futures
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote
from urllib.request import Request, urlopen

from catalog import PRODUCTS

OUT = Path(__file__).with_name("product_prices.json")
USER_AGENT = "Mozilla/5.0 (compatible; MojeVychytavkyPriceRefresh/1.0)"
PRICE_META = re.compile(
    r'<meta\b[^>]*(?:itemprop=["\']price["\']|property=["\']product:price:amount["\'])[^>]*\bcontent=["\']([0-9]+(?:[.,][0-9]+)?)["\']',
    re.I,
)
CURRENCY_META = re.compile(
    r'<meta\b[^>]*(?:itemprop=["\']priceCurrency["\']|property=["\']product:price:currency["\'])[^>]*\bcontent=["\']([A-Z]{3})["\']',
    re.I,
)


def destination(item: dict[str, str]) -> str:
    return unquote(item["url"].split("desturl=", 1)[1])


def fetch_price(url: str) -> tuple[str, int | None, str | None]:
    try:
        request = Request(url, headers={"User-Agent": USER_AGENT, "Accept-Language": "cs-CZ,cs;q=0.9"})
        with urlopen(request, timeout=30) as response:
            page = response.read().decode("utf-8", errors="replace")
        price_match = PRICE_META.search(page)
        currency_match = CURRENCY_META.search(page)
        if not price_match:
            return url, None, "structured price not found"
        currency = currency_match.group(1).upper() if currency_match else "CZK"
        if currency != "CZK":
            return url, None, f"unexpected currency {currency}"
        amount = float(price_match.group(1).replace(",", "."))
        if amount <= 0:
            return url, None, "non-positive price"
        return url, round(amount), None
    except Exception as error:  # preserve existing snapshot rather than invent a price
        return url, None, f"{type(error).__name__}: {error}"


def main() -> int:
    urls = [destination(item) for item in PRODUCTS]
    assert len(urls) == len(set(urls)), "duplicate destinations"
    prices: dict[str, int] = {}
    failures: list[tuple[str, str]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        for url, price, error in pool.map(fetch_price, urls):
            if price is None:
                failures.append((url, error or "unknown error"))
            else:
                prices[url] = price
    if failures:
        print("Price refresh failed; snapshot not replaced:")
        for url, error in failures:
            print(f"- {url}: {error}")
        return 1
    payload = {
        "observed_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "currency": "CZK",
        "prices": prices,
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"price snapshot: {len(prices)} products -> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
