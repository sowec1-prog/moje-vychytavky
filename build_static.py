"""Build a static, no-cost GitHub Pages version of the catalogue."""
from pathlib import Path

from app import app

OUT = Path(__file__).parent / "docs"
OUT.mkdir(exist_ok=True)

with app.test_request_context("/"):
    html = app.view_functions["index"]()
(OUT / "index.html").write_text(html, encoding="utf-8")

(OUT / "privacy.html").write_text("""<!doctype html><meta charset=\"utf-8\"><title>Soukromí | Moje vychytávky</title><main><h1>Soukromí</h1><p>Tento katalog sám neobsahuje formuláře, uživatelské účty ani vlastní analytické cookies.</p><p>Při otevření odkazu na produkt přechází návštěvník na web daného obchodníka; jeho zásady soukromí platí samostatně.</p><p>Kontaktní e-mail bude doplněn před spuštěním partnerských odkazů.</p></main>""", encoding="utf-8")

(OUT / "affiliate.html").write_text("""<!doctype html><meta charset=\"utf-8\"><title>Partnerské odkazy | Moje vychytávky</title><main><h1>Partnerské odkazy</h1><p>Aktuálně tento web používá jen běžné odkazy na obchody, bez provizního měření.</p><p>Po schválení příslušných partnerských programů budou provizní odkazy zřetelně označeny. Nákup tím kupujícímu nezdraží.</p></main>""", encoding="utf-8")

print(f"static build: {OUT / 'index.html'}")
