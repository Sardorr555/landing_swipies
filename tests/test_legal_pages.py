import unittest
import os

class TestLegalPages(unittest.TestCase):
    def setUp(self):
        self.base_dir = os.path.join(os.path.dirname(__file__), '..')
        with open(os.path.join(self.base_dir, 'privacy.html'), 'r', encoding='utf-8') as f:
            self.privacy = f.read()
        with open(os.path.join(self.base_dir, 'terms.html'), 'r', encoding='utf-8') as f:
            self.terms = f.read()
        with open(os.path.join(self.base_dir, 'offer.html'), 'r', encoding='utf-8') as f:
            self.offer = f.read()
        with open(os.path.join(self.base_dir, 'enterprise', 'offer.html'), 'r', encoding='utf-8') as f:
            self.ent_offer = f.read()
        with open(os.path.join(self.base_dir, 'index.html'), 'r', encoding='utf-8') as f:
            self.index = f.read()
        with open(os.path.join(self.base_dir, 'enterprise', 'index.html'), 'r', encoding='utf-8') as f:
            self.ent_index = f.read()
        with open(os.path.join(self.base_dir, 'setup_nginx.py'), 'r', encoding='utf-8') as f:
            self.nginx = f.read()

    def test_privacy_atmos_and_platform_mentions(self):
        self.assertIn('atmos.uz', self.privacy)
        self.assertIn('api.swipies.app', self.privacy)
        self.assertIn('Uzcard', self.privacy)
        self.assertIn('Humo', self.privacy)
        self.assertIn('Visa', self.privacy)
        self.assertIn('Mastercard', self.privacy)
        self.assertIn('PCI DSS', self.privacy)

    def test_privacy_cookie_and_security_telemetry(self):
        self.assertIn('swipies_cookie_consent', self.privacy)
        self.assertIn('swipies_lang', self.privacy)
        self.assertIn('swipies_currency', self.privacy)
        self.assertIn('CSRF', self.privacy)
        self.assertIn('Google Analytics', self.privacy)

    def test_privacy_trilingual_parity(self):
        self.assertIn('Payment Processing & Atmos Gateway (atmos.uz)', self.privacy)
        self.assertIn('Обработка платежей через платежный сервис Atmos (atmos.uz)', self.privacy)
        self.assertIn("To'lovlarni qayta ishlash va Atmos tizimi (atmos.uz)", self.privacy)

    def test_terms_atmos_and_platform_checkout(self):
        self.assertIn('atmos.uz', self.terms)
        self.assertIn('api.swipies.app', self.terms)
        self.assertIn('Uzcard', self.terms)
        self.assertIn('Humo', self.terms)
        self.assertIn('Visa', self.terms)
        self.assertIn('Mastercard', self.terms)
        self.assertIn('PCI DSS', self.terms)

    def test_terms_electronic_fulfillment_and_refunds(self):
        self.assertIn('14', self.terms)
        self.assertIn('support@swipies.app', self.terms)
        self.assertIn('Docker', self.terms)

    def test_terms_trilingual_parity(self):
        self.assertIn('Payment Processing via Atmos Gateway (atmos.uz)', self.terms)
        self.assertIn('Условия оплаты и платежный шлюз Atmos (atmos.uz)', self.terms)
        self.assertIn("To'lov shartlari va Atmos to'lov tizimi (atmos.uz)", self.terms)
        self.assertIn('Refund Policy (Atmos.uz Compliance)', self.terms)
        self.assertIn('Политика возврата средств (в соответствии с Atmos.uz)', self.terms)
        self.assertIn("Mablag'larni qaytarish siyosati (Atmos.uz talablari asosida)", self.terms)

    def test_public_offer_compliance_and_tariffs(self):
        # Atmos gateway & platform references
        self.assertIn('atmos.uz', self.offer)
        self.assertIn('api.swipies.app', self.offer)
        self.assertIn('Uzcard', self.offer)
        self.assertIn('Humo', self.offer)
        self.assertIn('Visa', self.offer)
        self.assertIn('Mastercard', self.offer)
        self.assertIn('PCI DSS', self.offer)

        # Uzbekistan legal citations
        self.assertIn('367', self.offer)
        self.assertIn('369', self.offer)

        # Tariffs & National Currency equivalents
        self.assertIn('199 000', self.offer)
        self.assertIn('399 000', self.offer)
        self.assertIn('1 990 000', self.offer)
        self.assertIn('20', self.offer)
        self.assertIn('40', self.offer)
        self.assertIn('199', self.offer)

        # Refund terms
        self.assertIn('14', self.offer)
        self.assertIn('support@swipies.app', self.offer)

        # Enterprise offer mirror
        self.assertIn('atmos.uz', self.ent_offer)
        self.assertIn('1 990 000', self.ent_offer)

    def test_public_offer_trilingual_parity(self):
        # Headers & key phrases in RU, EN, UZ
        self.assertIn('Публичная оферта', self.offer)
        self.assertIn('Public Offer Agreement', self.offer)
        self.assertIn('Ommaviy oferta shartnomasi', self.offer)

    def test_pricing_national_currency_equivalents_on_landing_pages(self):
        # index.html
        self.assertIn('price-equiv-row', self.index)
        self.assertIn('price-equiv-badge', self.index)
        self.assertIn('price-equiv-usd', self.index)
        self.assertIn('price-equiv-uzs', self.index)
        self.assertIn('pricing-compliance-banner', self.index)
        self.assertIn('199 000', self.index)
        self.assertIn('399 000', self.index)
        self.assertIn('1 990 000', self.index)
        self.assertIn('offer.html', self.index)
        self.assertIn('footer_offer', self.index)

        # enterprise/index.html
        self.assertIn('price-equiv-row', self.ent_index)
        self.assertIn('price-equiv-badge', self.ent_index)
        self.assertIn('pricing-compliance-banner', self.ent_index)
        self.assertIn('1 990 000', self.ent_index)
        self.assertIn('offer.html', self.ent_index)
        self.assertIn('footer_offer', self.ent_index)

    def test_nginx_offer_routing(self):
        self.assertIn('offer', self.nginx)
        self.assertIn('offer(\\\\.html)?', self.nginx)

if __name__ == '__main__':
    unittest.main()
