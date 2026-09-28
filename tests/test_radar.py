import unittest

from radar import extract_offer, affiliate_url, choose_alert


class RadarTests(unittest.TestCase):
    def test_extracts_czk_offer_from_json_ld(self):
        html = '''<script type="application/ld+json">{
          "@context":"https://schema.org", "@type":"Product", "name":"ESP32-C3 SuperMini",
          "offers":{"@type":"Offer","price":"89.90","priceCurrency":"CZK","availability":"https://schema.org/InStock"}
        }</script>'''
        offer = extract_offer(html, "https://shop.example/esp32")
        self.assertEqual(offer["title"], "ESP32-C3 SuperMini")
        self.assertEqual(offer["price_czk"], 89.90)
        self.assertTrue(offer["in_stock"])

    def test_extracts_single_unit_vat_inclusive_price_from_public_price_cell(self):
        html = '''<html><head><title>LM2596 DC-DC | shop</title></head><body>
        <table><tr><td>Množstevní slevy: 10 ks a více 25 Kč s DPH / ks</td></tr>
        <tr><td>Cena s DPH:</td><td><span class="hodnota">31</span> Kč</td></tr>
        <tr><td>Cena bez DPH:</td><td class="cena"><span id="cena" class="hodnota">26</span> Kč</td></tr></table>
        </body></html>'''
        offer = extract_offer(html, "https://shop.example/lm2596")
        self.assertEqual(offer["title"], "LM2596 DC-DC")
        self.assertEqual(offer["price_czk"], 31.0)

    def test_affiliate_link_is_plain_url_without_partner_id(self):
        self.assertEqual(
            affiliate_url("https://shop.example/p?id=7", ""),
            "https://shop.example/p?id=7",
        )

    def test_alert_only_when_price_enters_target(self):
        self.assertTrue(choose_alert(previous_price=120, current_price=99, target_price=100))
        self.assertFalse(choose_alert(previous_price=99, current_price=98, target_price=100))
        self.assertFalse(choose_alert(previous_price=120, current_price=101, target_price=100))


if __name__ == "__main__":
    unittest.main()
