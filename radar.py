"""Core price extraction and alert decisions for Slevový radar."""
from __future__ import annotations

import json
import re
from html import unescape
from html.parser import HTMLParser
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


class _JsonLdScripts(HTMLParser):
    def __init__(self):
        super().__init__()
        self._inside = False
        self._chunks: list[str] = []
        self.documents: list[object] = []

    def handle_starttag(self, tag, attrs):
        if tag == "script" and dict(attrs).get("type", "").lower() == "application/ld+json":
            self._inside = True
            self._chunks = []

    def handle_data(self, data):
        if self._inside:
            self._chunks.append(data)

    def handle_endtag(self, tag):
        if tag == "script" and self._inside:
            self._inside = False
            try:
                self.documents.append(json.loads("".join(self._chunks)))
            except json.JSONDecodeError:
                pass


def _walk(value):
    if isinstance(value, list):
        for item in value:
            yield from _walk(item)
    elif isinstance(value, dict):
        yield value
        if "@graph" in value:
            yield from _walk(value["@graph"])


def extract_offer(html: str, source_url: str) -> dict:
    """Extract an item with a CZK price from public schema.org JSON-LD."""
    parser = _JsonLdScripts()
    parser.feed(html)
    for document in parser.documents:
        for item in _walk(document):
            kinds = item.get("@type", [])
            if isinstance(kinds, str):
                kinds = [kinds]
            if "Product" not in kinds:
                continue
            offers = item.get("offers", [])
            if not isinstance(offers, list):
                offers = [offers]
            for offer in offers:
                if not isinstance(offer, dict):
                    continue
                if str(offer.get("priceCurrency", "")).upper() != "CZK":
                    continue
                try:
                    price = float(str(offer["price"]).replace(",", "."))
                except (KeyError, TypeError, ValueError):
                    continue
                availability = str(offer.get("availability", "")).lower()
                return {
                    "title": item.get("name") or source_url,
                    "price_czk": price,
                    "in_stock": "instock" in availability,
                    "source_url": source_url,
                }

    # Consumer product pages can publish wholesale tiers and an ex-VAT amount.
    # Prefer the explicit one-unit VAT-inclusive retail price whenever present.
    retail_match = re.search(r'Cena\s+s\s+DPH:\s*</[^>]+>\s*<[^>]*>\s*(?:<[^>]*>\s*)?([0-9][0-9\s.,]*)', html, re.I)
    if retail_match:
        raw_price = retail_match.group(1).replace(" ", "").replace(",", ".")
        try:
            price = float(raw_price)
        except ValueError:
            price = None
        if price is not None:
            title_match = re.search(r'<title[^>]*>(.*?)</title>', html, re.I | re.S)
            title = re.sub(r'\s*\|\s*[^|]+$', '', unescape(re.sub(r'<[^>]+>', '', title_match.group(1))).strip()) if title_match else source_url
            return {"title": title, "price_czk": price, "in_stock": True, "source_url": source_url}

    # Conservative fallback for shops exposing a visible Czech price cell.
    match = re.search(r'<(?:span|td)[^>]*(?:id=["\']cena["\']|class=["\'][^"\']*\bcena\b[^"\']*)[^>]*>\s*([0-9][0-9\s.,]*)', html, re.I)
    if match:
        raw_price = match.group(1).replace(" ", "").replace(",", ".")
        try:
            price = float(raw_price)
        except ValueError:
            price = None
        if price is not None:
            title_match = re.search(r'<title[^>]*>(.*?)</title>', html, re.I | re.S)
            title = re.sub(r'\s*\|\s*[^|]+$', '', unescape(re.sub(r'<[^>]+>', '', title_match.group(1))).strip()) if title_match else source_url
            return {"title": title, "price_czk": price, "in_stock": True, "source_url": source_url}
    raise ValueError("Na stránce nebyla nalezena veřejná cena v CZK (schema.org JSON-LD).")


def affiliate_url(url: str, partner_parameter: str) -> str:
    """Attach a configured partner parameter; blank keeps the original link."""
    if not partner_parameter or "=" not in partner_parameter:
        return url
    key, value = partner_parameter.split("=", 1)
    parts = urlsplit(url)
    query = dict(parse_qsl(parts.query, keep_blank_values=True))
    query[key] = value
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment))


def choose_alert(previous_price: float | None, current_price: float, target_price: float) -> bool:
    """Alert once when a price crosses down into its target threshold."""
    return current_price <= target_price and (previous_price is None or previous_price > target_price)
