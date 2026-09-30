"""Launch-ready catalogue application.

The public site deliberately contains no guessed affiliate parameters.  Merchant
links remain ordinary links until each eHUB programme approves the publisher
and provides a generated tracking link.
"""
from __future__ import annotations

import os
from urllib.parse import unquote

from flask import Flask, jsonify, render_template, request

from catalog import CATEGORIES, CATEGORY_IMAGES, PRICE_OBSERVED_AT, PRODUCTS
from merchant_plan import MERCHANTS
from product_images import PRODUCT_IMAGES

app = Flask(__name__)


@app.get("/")
def index():
    category = request.args.get("category", "")
    products = [
        {**item, "image": item.get("image") or PRODUCT_IMAGES[unquote(item["url"].split("desturl=", 1)[1])]}
        for item in PRODUCTS
        if not category or item["category"] == category
    ]
    return render_template(
        "index.html",
        products=products,
        categories=CATEGORIES,
        category_images=CATEGORY_IMAGES,
        selected_category=category,
        total_products=len(PRODUCTS),
        price_observed_at=PRICE_OBSERVED_AT,
        merchants=MERCHANTS,
        affiliate_approved=True,
        evolveo_promo=[
            next(item for item in PRODUCTS if phrase.lower() in item["title"].lower() and item.get("price", 0) > 100)
            for phrase in (
                "StrongVision PRO 4G II",
                "StrongVision LTE MINI",
                "StrongVision Solar 4G",
                "Detective POE8 SMART, kamerový systém",
            )
        ],
    )


@app.get("/healthz")
def healthz():
    """Minimal health endpoint for a future host's health check."""
    return jsonify(status="ok", products=len(PRODUCTS), merchants=len(MERCHANTS))


if __name__ == "__main__":
    # Local-only development default. Hosting platforms supply PORT themselves.
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", "5055")), debug=False)
