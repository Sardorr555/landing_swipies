import unittest
import os

class TestNginxConfig(unittest.TestCase):
    def setUp(self):
        self.nginx_script = os.path.join(os.path.dirname(__file__), '..', 'setup_nginx.py')
        with open(self.nginx_script, 'r', encoding='utf-8') as f:
            self.content = f.read()

    def test_setup_nginx_contains_enterprise_server(self):
        self.assertIn('enterprise.swipies.app', self.content)

    def test_setup_nginx_enterprise_root(self):
        self.assertIn('/var/www/html/enterprise', self.content)

    def test_setup_nginx_enterprise_api_proxy(self):
        self.assertIn('proxy_pass         http://127.0.0.1:5005', self.content)

    def test_setup_nginx_b2c_enterprise_redirect(self):
        self.assertIn('https://enterprise.swipies.app', self.content)
        self.assertIn('location = /enterprise', self.content)

if __name__ == '__main__':
    unittest.main()
