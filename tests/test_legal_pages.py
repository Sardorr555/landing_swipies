import unittest
import os

class TestLegalPages(unittest.TestCase):
    def setUp(self):
        self.base_dir = os.path.join(os.path.dirname(__file__), '..')
        with open(os.path.join(self.base_dir, 'privacy.html'), 'r', encoding='utf-8') as f:
            self.privacy = f.read()
        with open(os.path.join(self.base_dir, 'terms.html'), 'r', encoding='utf-8') as f:
            self.terms = f.read()

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

if __name__ == '__main__':
    unittest.main()
