"""Refresh source image URLs from Cubenest's public image sitemap.

Run manually when the editorial catalogue changes; this script is never run by
the public web server.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from catalog import BASE, PRODUCT_PATHS, CATEGORY_IMAGES

SITEMAP_URL = "https://www.cubenest.cz/imagesitemap.xml"
OUT = ROOT / "product_images.py"

request = Request(SITEMAP_URL, headers={"User-Agent": "MojeVychytavky/1.0 (+editorial catalogue)"})
with urlopen(request, timeout=45) as response:
    sitemap = response.read().decode("utf-8", "replace")

entries = re.findall(r"<url>\s*<loc>(.*?)</loc>\s*<image:image>\s*<image:loc>(.*?)</image:loc>", sitemap, re.S)
images = {url: image for url, image in entries}
selected = {
    BASE + path: images.get(BASE + path, CATEGORY_IMAGES[category])
    for category, path in PRODUCT_PATHS
}

body = '"""Public product-image URLs sourced from the merchant image sitemap."""\n\nPRODUCT_IMAGES = ' + repr(selected) + "\n"
OUT.write_text(body, encoding="utf-8")
print(f"wrote {len(selected)} image mappings to {OUT}")
