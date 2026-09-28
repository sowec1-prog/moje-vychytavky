import unittest

from app import app
from catalog import CATEGORIES, PRODUCTS
from merchant_plan import MERCHANTS


class LaunchTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_catalogue_has_broad_structured_selection(self):
        self.assertGreaterEqual(len(PRODUCTS), 50)
        self.assertGreaterEqual(len(CATEGORIES), 5)
        self.assertEqual(len({item['url'] for item in PRODUCTS}), len(PRODUCTS))

    def test_home_and_category_filter_render(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'72 produkt', response.data)
        response = self.client.get('/?category=Do+auta')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.count(b'class="card"'), 6)

    def test_launch_safety_and_health(self):
        response = self.client.get('/')
        self.assertNotIn(b'eHUB', response.data)
        self.assertIn('Každá karta vede přímo'.encode(), response.data)
        self.assertEqual(len(MERCHANTS), 4)
        health = self.client.get('/healthz')
        self.assertEqual(health.status_code, 200)
        self.assertEqual(health.json['status'], 'ok')
        self.assertEqual(health.json['products'], len(PRODUCTS))


if __name__ == '__main__':
    unittest.main()
