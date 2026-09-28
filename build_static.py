"""Build a static, no-cost GitHub Pages version of the catalogue."""
from datetime import date
from pathlib import Path

from app import app

OUT = Path(__file__).parent / "docs"
OUT.mkdir(exist_ok=True)
PUBLIC_URL = "https://moje-vychytavky.pages.dev/"

with app.test_request_context("/"):
    html = app.view_functions["index"]()
# Root-relative policy links would point to the wrong GitHub Pages site root.
html = html.replace('href="/affiliate.html"', 'href="affiliate.html"')
html = html.replace('href="/privacy.html"', 'href="privacy.html"')
(OUT / "index.html").write_text(html, encoding="utf-8")

(OUT / "robots.txt").write_text(
    "User-agent: *\nAllow: /\nSitemap: " + PUBLIC_URL + "sitemap.xml\n",
    encoding="utf-8",
)
(OUT / "sitemap.xml").write_text(
    "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
    "<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">\n"
    f"  <url><loc>{PUBLIC_URL}</loc><lastmod>{date.today().isoformat()}</lastmod></url>\n"
    f"  <url><loc>{PUBLIC_URL}affiliate.html</loc><lastmod>{date.today().isoformat()}</lastmod></url>\n"
    f"  <url><loc>{PUBLIC_URL}privacy.html</loc><lastmod>{date.today().isoformat()}</lastmod></url>\n"
    "</urlset>\n",
    encoding="utf-8",
)

(OUT / "privacy.html").write_text("""<!doctype html><meta charset=\"utf-8\"><title>Soukromí | Moje vychytávky</title><main><h1>Soukromí</h1><p>Tento katalog sám neobsahuje formuláře, uživatelské účty ani vlastní analytické cookies.</p><p>Při otevření odkazu na produkt přechází návštěvník na web daného obchodníka; jeho zásady soukromí platí samostatně.</p><p>Kontaktní e-mail bude doplněn před spuštěním partnerských odkazů.</p></main>""", encoding="utf-8")

(OUT / "affiliate.html").write_text("""<!doctype html><meta charset=\"utf-8\"><title>Partnerské odkazy | Moje vychytávky</title><main><h1>Partnerské odkazy</h1><p>Aktuálně tento web používá jen běžné odkazy na obchody, bez provizního měření.</p><p>Po schválení příslušných partnerských programů budou provizní odkazy zřetelně označeny. Nákup tím kupujícímu nezdraží.</p></main>""", encoding="utf-8")

# Cloudflare Pages is configured with the repository root as the output folder.
# Keep the generated public assets there as well as in docs/ (for GitHub Pages).
ROOT = Path(__file__).parent
for name in ("index.html", "privacy.html", "affiliate.html", "robots.txt", "sitemap.xml"):
    (ROOT / name).write_text((OUT / name).read_text(encoding="utf-8"), encoding="utf-8")

print(f"static build: {OUT / 'index.html'}")
