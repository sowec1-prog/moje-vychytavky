"""Curated public product catalogue.

URLs were selected from Cubenest.cz's public sitemap on 2026-09-28.
They are ordinary merchant links until eHUB approves the programme and
provides generated tracking links. No price or availability is asserted here.
"""
from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
from urllib.parse import quote, unquote

MERCHANT_BASE = "https://www.cubenest.cz"
EHUB_CLICK_BASE = "https://ehub.cz/system/scripts/click.php?a_aid=391b26f8&a_bid=231eaccc&desturl="


def tracked_cubenest_url(path: str) -> str:
    """Verified eHUB deeplink format for an approved Cubenest product URL."""
    return EHUB_CLICK_BASE + quote(MERCHANT_BASE + path, safe="")

# (category, product-page path).  Every item has a distinct real product page.
PRODUCT_PATHS = [
    # MagSafe & Qi2
    ("MagSafe a Qi2", "/p-753/3v1-magsafe-nabijecka-s312"),
    ("MagSafe a Qi2", "/p-757/2v1-magsafe-nabijecka-k200"),
    ("MagSafe a Qi2", "/p-763/3v1-magsafe-nabijecka-e310"),
    ("MagSafe a Qi2", "/p-778/magsafe-powerbanka-s1b1"),
    ("MagSafe a Qi2", "/p-795/magsafe-powerbanka-s1b1"),
    ("MagSafe a Qi2", "/p-818/2v1-magsafe-nabijecka-k200"),
    ("MagSafe a Qi2", "/p-841/magsafe-nabijecka-3v1-e311"),
    ("MagSafe a Qi2", "/p-850/qi2-skladaci-magsafe-nabijecka-s312pro"),
    ("MagSafe a Qi2", "/p-902/3v1-qi2-magsafe-nabijecka-sq312pro-cerna"),
    ("MagSafe a Qi2", "/p-904/qi2-3v1-magsafe-nabijecka-sq312pro-samsung"),
    ("MagSafe a Qi2", "/p-954/3v1-qi22-magsafe-nabijecka-sq312ultra"),
    ("MagSafe a Qi2", "/p-966/qi2-magsafe-nabijecka-3v1-eq310"),
    ("MagSafe a Qi2", "/p-967/3v1-qi22-skladaci-magsafe-nabijecka-sq312-ultra-oranzova"),
    ("MagSafe a Qi2", "/p-968/qi2-magsafe-nabijecka-3v1-eq310-seda"),
    ("MagSafe a Qi2", "/p-970/qi2-magsafe-powerbanka-slimdual-sq1b3d-stribrna"),
    ("MagSafe a Qi2", "/p-971/qi2-magsafe-powerbanka-slimdual-sq1b3d-cerna"),
    ("MagSafe a Qi2", "/p-972/qi2-magsafe-powerbanka-slimdual-5000-mah-sq1b3d-oranzova"),
    ("MagSafe a Qi2", "/p-974/3v1-qi22-magsafe-nabijecka-sq312-ultra-cerna"),
    ("MagSafe a Qi2", "/p-975/3v1-qi22-magsafe-nabijecka-sq314-seda"),
    ("MagSafe a Qi2", "/p-979/3v1-qi22-magsafe-nabijecka-sq314-oranzova"),
    ("MagSafe a Qi2", "/p-989/bezdratova-nabijecka-samsung-sqs314"),
    ("MagSafe a Qi2", "/p-1002/qi22-nabijecka-garmin-sq314"),
    ("MagSafe a Qi2", "/p-1017/3v1-qi2-magsafe-nabijecka-sq312-pro-titanova"),
    ("MagSafe a Qi2", "/p-1018/3v1-qi2-magsafe-nabijecka-sq312-cerna"),
    ("MagSafe a Qi2", "/p-1019/3v1-qi2-magsafe-nabijecka-sqs312-pro-samsung-watch"),
    # Nabíječky a cestování
    ("Nabíječky a cestování", "/p-696/pd-gan-nabijecka-65w-s3d0"),
    ("Nabíječky a cestování", "/p-723/pd-adapter-gan-140w-s5d0"),
    ("Nabíječky a cestování", "/p-751/cestovni-gan-adapter-65w-s3d1"),
    ("Nabíječky a cestování", "/p-787/pd-gan-nabijecka-35w-s2d1"),
    ("Nabíječky a cestování", "/p-805/cubenest-pd-gan-adapter-65w-s3d0-bily"),
    ("Nabíječky a cestování", "/p-806/cubenest-pd-gan-adapter-35w-s2d1"),
    ("Nabíječky a cestování", "/p-842/pd-gan-adapter-240w-s6d0"),
    ("Nabíječky a cestování", "/p-961/pd-gan-nabijecka-65w-s3d2"),
    ("Nabíječky a cestování", "/p-980/pd-gan-nabijecka-30w"),
    ("Nabíječky a cestování", "/p-985/nano-adapter-ubc-c-45w-n1d45"),
    ("Nabíječky a cestování", "/p-986/nano-adapter-usb-c-65w-n1d65"),
    ("Nabíječky a cestování", "/p-987/nano-adapter-2x-usb-c-65w-n2d65"),
    ("Nabíječky a cestování", "/p-988/nano-adapter-2xusb-c-100w-n2d100"),
    ("Nabíječky a cestování", "/p-995/gan-adapter-45w-e1d3"),
    ("Nabíječky a cestování", "/p-1031/pd-gan-nano-adapter-usb-c-65w-a1d65"),
    # Do auta
    ("Do auta", "/p-746/cubenest-nabijecka-do-auta-e2c0"),
    ("Do auta", "/p-755/drzak-do-auta-s-prisavkou"),
    ("Do auta", "/p-808/cubenest-pd-nabijecka-do-auta-e2c0"),
    ("Do auta", "/p-962/qi22-chladici-magsafe-nabijeci-drzak-do-auta-sq1c2"),
    ("Do auta", "/p-963/qi22-chladici-magsafe-nabijeci-drzak-do-auta-25-w-sq1c3"),
    ("Do auta", "/p-981/qi22-magsafe-nabijecka-do-auta-sq1c4"),
    # Apple Watch
    ("Apple Watch", "/p-748/sportovni-reminek-na-apple-watch"),
    ("Apple Watch", "/p-750/reminek-na-apple-watch-trailovy-tah"),
    ("Apple Watch", "/p-809/cubenest-reminek-na-apple-watch-trailovy-tah-modro-oranzovy"),
    ("Apple Watch", "/p-810/cubenest-reminek-na-apple-watch-trailovy-tah-modro-oranzovy"),
    ("Apple Watch", "/p-811/cubenest-reminek-na-apple-watch-trailovy-tah-modro-oranzovy"),
    ("Apple Watch", "/p-812/cubenest-sportovni-reminek-na-apple-watch"),
    ("Apple Watch", "/p-813/cubenest-sportovni-reminek-na-apple-watch"),
    ("Apple Watch", "/p-814/cubenest-sportovni-reminek-na-apple-watch"),
    ("Apple Watch", "/p-815/cubenest-sportovni-reminek-na-apple-watch"),
    ("Apple Watch", "/p-816/cubenest-sportovni-reminek-na-apple-watch"),
    ("Apple Watch", "/p-855/reminek-na-apple-watch-bily"),
    ("Apple Watch", "/p-861/sportovni-reminek-na-apple-watch-cerny"),
    ("Apple Watch", "/p-862/sportovni-reminek-na-apple-watch-oranzovy"),
    ("Apple Watch", "/p-863/cubenest-premiovy-sportovni-reminek-na-apple-watch-modry"),
    ("Apple Watch", "/p-864/sportovni-reminek-na-apple-watch-zluto-sedy"),
    ("Apple Watch", "/p-865/sportovni-reminek-na-apple-watch-modro-sedy"),
    ("Apple Watch", "/p-866/sportovni-reminek-na-apple-watch-cerno-sedy"),
    ("Apple Watch", "/p-867/cubenest-premiovy-sportovni-reminek-na-apple-watch-zluto-sedy"),
    ("Apple Watch", "/p-868/cubenest-premiovy-sportovni-reminek-na-apple-watch-cerno-modry"),
    ("Apple Watch", "/p-869/cubenest-premiovy-sportovni-reminek-na-apple-watch-cerno-oranzovy"),
    ("Apple Watch", "/p-870/cubenest-premiovy-sportovni-reminek-na-apple-watch-cerno-oranzovy"),
    # Zásuvky a organizace kabelů
    ("Zásuvky a kabely", "/p-752/powercube-original-usb-ac-pd-20w"),
    ("Zásuvky a kabely", "/p-756/powercube-extended-usb-ac"),
    ("Zásuvky a kabely", "/p-761/powercube-original"),
    ("Zásuvky a kabely", "/p-965/pd-gan-powerstrip-slimsline-7v1-extended-usb-33w"),
    ("Zásuvky a kabely", "/p-1020/pd-gan-powerstrip-7v1-extended-usb-70w"),
]


def _display_name(path: str) -> str:
    slug = path.rsplit("/", 1)[-1].replace("-", " ")
    return slug.replace("qi2", "Qi2").replace("qi22", "Qi2.2").replace("gan", "GaN").replace("pd", "PD").replace("usb", "USB").title().replace("Usb", "USB").replace("Gan", "GaN").replace("Pd", "PD").replace("Qi2", "Qi2").replace("Qi22", "Qi2.2")


EVOLVEO_CLICK_BASE = "https://ehub.cz/system/scripts/click.php?a_aid=391b26f8&a_bid=f89ce7c7&desturl="


def tracked_evolveo_url(path: str) -> str:
    """Verified eHUB deeplink format for an approved EVOLVEO product URL."""
    return EVOLVEO_CLICK_BASE + quote("https://eshop.evolveo.cz" + path, safe="")


# Live products selected from the public EVOLVEO catalogue on 2026-09-29.
EVOLVEO_PRODUCTS = (
    ("Fotopasti a bezpečnost", "EVOLVEO StrongVision LTE CLOUD – 4G fotopast s Cloud/Email", "/evolveo-strongvision-lte-cloud-fotopast-s-4g--cloud-email--32gb/", "https://cdn.myshoptet.com/usr/eshop.evolveo.cz/user/shop/related/7441-1_evolveo-strongvision-lte-cloud-fotopast-s-4g--cloud-email--32gb.jpg?ff=1&x=100&y=100&q=85&ts=688c4708&sg=8dda0505"),
    ("Fotopasti a bezpečnost", "EVOLVEO StrongVision LTE MINI – 4G fotopast se solárním napájením", "/evolveo-strongvision-lte-mini---4g-fotopast-s-cloud-email-prenosem-a-solarnim-napajenim/", "https://cdn.myshoptet.com/usr/eshop.evolveo.cz/user/shop/related/8411_evolveo-strongvision-lte-mini-8211--4g-fotopast-s-cloud-email-p--345-enosem-a-solarnim-napajenim.jpg?ff=1&x=100&y=100&q=85&ts=69dc947a&sg=8dda0505"),
    ("Fotopasti a bezpečnost", "EVOLVEO StrongVision Compact 4K fotopast", "/evolveo-strongvision-compact-4k--fotopast-casosberna-kamera-32gb/", "https://cdn.myshoptet.com/usr/eshop.evolveo.cz/user/shop/related/7567_evolveo-strongvision-compact-4k--fotopast-269-asosb--283-rna-kamera-32gb.jpg?ff=1&x=100&y=100&q=85&ts=688c4708&sg=8dda0505"),
    ("Fotopasti a bezpečnost", "EVOLVEO StrongVision LTE POWER – 4G fotopast", "/evolveo-strongvision-lte-power---4g-fotopast-s-cloud-email-prenosem-a-vymennymi-21700-bateriemi/", "https://cdn.myshoptet.com/usr/eshop.evolveo.cz/user/shop/related/8414_evolveo-strongvision-lte-power-8211--4g-fotopast-s-cloud-email-p--345-enosem-a-vym--283-nnymi-21700-bateriemi.jpg?ff=1&x=100&y=100&q=85&ts=69dc947f&sg=8dda0505"),
    ("Fotopasti a bezpečnost", "EVOLVEO StrongVision Dual PRO 4G fotopast", "/evolveo-strongvision-dual-pro-4g--fotopast-s-odesilanim-na-cloud-a-email/", "https://cdn.myshoptet.com/usr/eshop.evolveo.cz/user/shop/related/7372_evolveo-strongvision-dual-pro-4g--fotopast-s-odesilanim-na-cloud-a-email.jpg?ff=1&x=100&y=100&q=85&ts=6a361b83&sg=8dda0505"),
    ("Mobilní telefony", "EVOLVEO MaxPhone A1 – tlačítkový Dual SIM telefon", "/evolveo-maxphone-a1--tlacitkovy-dual-sim-telefon--cerny/", "https://cdn.myshoptet.com/usr/eshop.evolveo.cz/user/shop/related/7426_evolveo-maxphone-a1--tla--269-itkovy-dual-sim-telefon--269-erny.jpg?ff=1&x=100&y=100&q=85&ts=688c470b&sg=8dda0505"),
    ("Audio", "EVOLVEO XSleep – polštářový Bluetooth reproduktor", "/evolveo-xsleep--polstarovy-bluetooth-reproduktor-na-spani--cerny/", "https://cdn.myshoptet.com/usr/eshop.evolveo.cz/user/shop/related/8446_evolveo-xsleep--pol--353-ta--345-ovy-bluetooth-reproduktor-na-spani--269-erny.jpg?ff=1&x=100&y=100&q=85&ts=6a33985c&sg=8dda0505"),
    ("Fotopasti a bezpečnost", "EVOLVEO StrongVision BAT3 V2 8000 mAh baterie", "/evolveo-strongvision-bat3--v2-8000mah-nahradni-baterie-pro-strongvision-usb-c/", "https://cdn.myshoptet.com/usr/eshop.evolveo.cz/user/shop/related/7061-1_evolveo-strongvision-bat3--v2-8000mah-nahradni-baterie-pro-strongvision-usb-c.jpg?ff=1&x=100&y=100&q=85&ts=688c4708&sg=8dda0505"),
    ("Fotopasti a bezpečnost", "EVOLVEO StrongVision adaptér 12 V / 2 A", "/evolveo-strongvision-adapter-12v2a/", "https://cdn.myshoptet.com/usr/eshop.evolveo.cz/user/shop/related/5034-1_evolveo-strongvision-adapter-12v2a.jpg?ff=1&x=100&y=100&q=85&ts=688c4707&sg=8dda0505"),
)

# Complete public phone range from EVOLVEO, captured 2026-09-30.
# Kept as a checked-in snapshot so the static site builds without live scraping.
EVOLVEO_PHONE_PRODUCTS = tuple(
    ("Mobilní telefony", item["title"], item["path"], item["image"])
    for item in json.loads((Path(__file__).with_name("evolveo_phones.json")).read_text(encoding="utf-8"))
)

PRICE_SNAPSHOT = json.loads((Path(__file__).with_name("product_prices.json")).read_text(encoding="utf-8"))
PRICE_OBSERVED_AT = PRICE_SNAPSHOT["observed_at"]
PRICES = PRICE_SNAPSHOT["prices"]


def _price_for(url: str) -> int:
    """Return a verified CZK price from the checked snapshot."""
    return PRICES[url]


PRODUCTS = (
    tuple(
        {
            "category": category,
            "title": _display_name(path),
            "url": tracked_cubenest_url(path),
            "price": _price_for(MERCHANT_BASE + path),
        }
        for category, path in PRODUCT_PATHS
    )
    + tuple(
        {
            "category": category,
            "title": title,
            "url": tracked_evolveo_url(path),
            "image": image,
            "price": _price_for("https://eshop.evolveo.cz" + path),
        }
        for category, title, path, image in (EVOLVEO_PRODUCTS + EVOLVEO_PHONE_PRODUCTS)
    )
)
# Full current catalogue snapshot, verified against public product pages.
# The old curated categories remain wherever a product already belonged to one;
# all other products are discoverable under a merchant-wide complete catalogue.
CURATED_CATEGORIES = {
    unquote(item["url"].split("desturl=", 1)[1]): item["category"]
    for item in PRODUCTS
}
COMPLETE_SNAPSHOT = json.loads((Path(__file__).with_name("complete_catalog.json")).read_text(encoding="utf-8"))
PRICE_OBSERVED_AT = COMPLETE_SNAPSHOT["observed_at"]


def tracked_public_url(merchant: str, url: str) -> str:
    if merchant == "Cubenest":
        return EHUB_CLICK_BASE + quote(url, safe="")
    if merchant == "EVOLVEO":
        return EVOLVEO_CLICK_BASE + quote(url, safe="")
    raise ValueError(f"Unsupported merchant: {merchant}")


PRODUCTS = tuple(
    {
        "category": CURATED_CATEGORIES.get(item["url"], item["category"]),
        "title": item["title"],
        "url": tracked_public_url(item["merchant"], item["url"]),
        "image": item["image"],
        "price": item["price"],
    }
    for item in COMPLETE_SNAPSHOT["products"]
)
CATEGORIES = tuple(category for category, _ in Counter(item["category"] for item in PRODUCTS).items())

# Official merchant imagery only identifies filters; every product card has its own image.
CATEGORY_IMAGES = {
    "MagSafe a Qi2": "https://www.cubenest.cz/resize/e/800/800/files/cubenestproducts/e310/ctverec/20.jpg",
    "Nabíječky a cestování": "https://www.cubenest.cz/resize/af/400/400/files/cubenestproducts/3.s3d0/cerna-nove-logo/2.jpg",
    "Do auta": "https://www.cubenest.cz/resize/e/800/800/files/cubenestproducts/sq1c2/1.1.webp",
    "Apple Watch": "https://www.cubenest.cz/resize/e/800/800/files/cubenestproducts/reminky/orange-with-grey.png",
    "Zásuvky a kabely": "https://www.cubenest.cz/resize/e/800/800/files/cubenestproducts/powerstrip/1.jpg",
    "Fotopasti a bezpečnost": "https://cdn.myshoptet.com/usr/eshop.evolveo.cz/user/shop/related/7567_evolveo-strongvision-compact-4k--fotopast-269-asosb--283-rna-kamera-32gb.jpg?ff=1&x=100&y=100&q=85&ts=688c4708&sg=8dda0505",
    "Mobilní telefony": "https://cdn.myshoptet.com/usr/eshop.evolveo.cz/user/shop/related/7426_evolveo-maxphone-a1--tla--269-itkovy-dual-sim-telefon--269-erny.jpg?ff=1&x=100&y=100&q=85&ts=688c470b&sg=8dda0505",
    "Audio": "https://cdn.myshoptet.com/usr/eshop.evolveo.cz/user/shop/related/8446_evolveo-xsleep--pol--353-ta--345-ovy-bluetooth-reproduktor-na-spani--269-erny.jpg?ff=1&x=100&y=100&q=85&ts=6a33985c&sg=8dda0505",
    "Cubenest – kompletní sortiment": "https://www.cubenest.cz/resize/e/800/800/files/cubenestproducts/e310/ctverec/20.jpg",
    "EVOLVEO – kompletní sortiment": "https://cdn.myshoptet.com/usr/eshop.evolveo.cz/user/shop/related/7426_evolveo-maxphone-a1--tla--269-itkovy-dual-sim-telefon--269-erny.jpg?ff=1&x=100&y=100&q=85&ts=688c470b&sg=8dda0505",
}

assert set(CATEGORY_IMAGES) == set(CATEGORIES)
assert len({item["url"] for item in PRODUCTS}) == len(PRODUCTS)
