import unittest
import os
import sys
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from api import app, init_db

class TestGeoPricing(unittest.TestCase):
    def setUp(self):
        self.root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        self.b2c_path = os.path.join(self.root_dir, 'index.html')
        self.ent_path = os.path.join(self.root_dir, 'enterprise', 'index.html')

        with open(self.b2c_path, 'r', encoding='utf-8') as f:
            self.b2c_html = f.read()
        with open(self.ent_path, 'r', encoding='utf-8') as f:
            self.ent_html = f.read()

        app.config['TESTING'] = True
        self.client = app.test_client()

    def test_api_geo_endpoint(self):
        res = self.client.get('/api/geo')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data.get('code'), 0)
        self.assertIn('currency', data)
        self.assertIn('country', data)
        self.assertIn('is_uz', data)
        self.assertIn(data.get('currency'), ['USD', 'UZS'])

    def test_b2c_pricing_values_usd_and_uzs(self):
        # Check basic tier:  and 199 000 сум
        self.assertIn('', self.b2c_html)
        self.assertIn('199 000 сум', self.b2c_html)

        # Check pro tier:  and 399 000 сум
        self.assertIn('', self.b2c_html)
        self.assertIn('399 000 сум', self.b2c_html)

        # Check license tier:  and 1.99 млн сум
        self.assertIn('', self.b2c_html)
        self.assertIn('1.99 млн сум', self.b2c_html)

    def test_b2c_currency_switcher_markup(self):
        self.assertIn('pricing-currency-wrap', self.b2c_html)
        self.assertIn('data-currency="usd"', self.b2c_html)
        self.assertIn('data-currency="uzs"', self.b2c_html)
        self.assertIn('setPricingCurrency', self.b2c_html)
        self.assertIn('updatePricingDisplay', self.b2c_html)

    def test_b2c_geo_detection_engine(self):
        # Timezone zero-latency check
        self.assertIn('Asia/Tashkent', self.b2c_html)
        self.assertIn('Asia/Samarkand', self.b2c_html)
        # First-party API check
        self.assertIn('/api/geo', self.b2c_html)
        # LocalStorage persistence
        self.assertIn('swipies_currency', self.b2c_html)

    def test_enterprise_pricing_values_and_switcher(self):
        # Check license tier:  and 1.99 млн сум
        self.assertIn('', self.ent_html)
        self.assertIn('1.99 млн сум', self.ent_html)

        # Cross-sell card
        self.assertIn('', self.ent_html)
        self.assertIn('199 000 сум', self.ent_html)

        # Currency Switcher
        self.assertIn('pricing-currency-wrap', self.ent_html)
        self.assertIn('data-currency="usd"', self.ent_html)
        self.assertIn('data-currency="uzs"', self.ent_html)
        self.assertIn('setPricingCurrency', self.ent_html)

        # Timezone and API detection
        self.assertIn('Asia/Tashkent', self.ent_html)
        self.assertIn('/api/geo', self.ent_html)

    def test_i18n_dictionary_contains_prices_and_toggles(self):
        # B2C i18n
        self.assertIn('basic_price_usd', self.b2c_html)
        self.assertIn('basic_price_uzs', self.b2c_html)
        self.assertIn('starter_price_usd', self.b2c_html)
        self.assertIn('starter_price_uzs', self.b2c_html)
        self.assertIn('license_price_usd', self.b2c_html)
        self.assertIn('license_price_uzs', self.b2c_html)

        # Enterprise i18n
        self.assertIn('license_price_usd', self.ent_html)
        self.assertIn('license_price_uzs', self.ent_html)

if __name__ == '__main__':
    unittest.main()
