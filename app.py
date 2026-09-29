"""Launch-ready catalogue application.

The public site deliberately contains no guessed affiliate parameters.  Merchant
links remain ordinary links until each eHUB programme approves the publisher
and provides a generated tracking link.
"""
from __future__ import annotations

import os
from urllib.parse import unquote

from flask import Flask, jsonify, render_template, request

from catalog import CATEGORIES, CATEGORY_IMAGES, PRODUCTS
from merchant_plan import MERCHANTS
from product_images import PRODUCT_IMAGES

app = Flask(__name__)


@app.get("/")
def index():
    category = request.args.get("category", "")
    products = [
        {**item, "image": PRODUCT_IMAGES[unquote(item["url"].split("desturl=", 1)[1])]}
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
        merchants=MERCHANTS,
        affiliate_approved=False,
    )


@app.get("/healthz")
def healthz():
    """Minimal health endpoint for a future host's health check."""
    return jsonify(status="ok", products=len(PRODUCTS), merchants=len(MERCHANTS))


if __name__ == "__main__":
    # Local-only development default. Hosting platforms supply PORT themselves.
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", "5055")), debug=False)
