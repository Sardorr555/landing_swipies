import unittest
import os

class TestB2CSite(unittest.TestCase):
    def setUp(self):
        self.index_path = os.path.join(os.path.dirname(__file__), '..', 'index.html')
        with open(self.index_path, 'r', encoding='utf-8') as f:
            self.content = f.read()

    def test_canonical_and_title(self):
        self.assertIn('<link rel="canonical" href="https://swipies.app/">', self.content)
        self.assertIn('Swipies AI', self.content)

    def test_has_enterprise_nav_link(self):
        # Must link to enterprise.swipies.app in header
        self.assertIn('https://enterprise.swipies.app', self.content)

    def test_has_enterprise_upsell_section(self):
        # Must have section guiding to enterprise
        self.assertIn('id="enterprise-upsell"', self.content)

    def test_removed_heavy_onprem_rag_problem(self):
        # Problem section 'Why Standard AI Fails Enterprise' moved to enterprise site
        self.assertNotIn('Why Standard AI Fails Enterprise', self.content)

    def test_lead_submission_tags_b2c(self):
        self.assertIn("source: 'b2c'", self.content)

    def test_favicon_links_present(self):
        self.assertIn('/favicon/favicon-96x96.png', self.content)
        self.assertIn('/favicon/favicon.svg', self.content)
        self.assertIn('/favicon/favicon.ico', self.content)
        self.assertIn('/favicon/apple-touch-icon.png', self.content)
        self.assertIn('/favicon/site.webmanifest', self.content)

if __name__ == '__main__':
    unittest.main()
