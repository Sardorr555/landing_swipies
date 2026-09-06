import unittest
import os

class TestEnterpriseSite(unittest.TestCase):
    def setUp(self):
        self.ent_path = os.path.join(os.path.dirname(__file__), '..', 'enterprise', 'index.html')
        self.assertTrue(os.path.exists(self.ent_path), "enterprise/index.html must exist")
        with open(self.ent_path, 'r', encoding='utf-8') as f:
            self.content = f.read()

    def test_canonical_and_title(self):
        self.assertIn('<link rel="canonical" href="https://enterprise.swipies.app/">', self.content)
        self.assertIn('Enterprise', self.content)

    def test_cross_nav_backlink_to_b2c(self):
        # Header must have link back to main cloud site
        self.assertIn('https://swipies.app', self.content)

    def test_enterprise_sections(self):
        self.assertIn('id="problem"', self.content)
        self.assertIn('Why Standard AI Fails Enterprise', self.content)
        self.assertIn('id="solution"', self.content)
        self.assertIn('id="how"', self.content)
        self.assertIn('id="selfhosted"', self.content)
        self.assertIn('id="cases"', self.content)
        self.assertIn('id="pricing"', self.content)
        self.assertIn('id="faq"', self.content)
        self.assertIn('id="contact"', self.content)

    def test_lead_submission_tags_enterprise(self):
        self.assertIn("source: 'enterprise'", self.content)

    def test_install_command_present(self):
        self.assertIn('install.sh', self.content)
        self.assertIn('curl -fsSL', self.content)

    def test_hardware_specs_table(self):
        self.assertIn('specs-table', self.content)
        self.assertIn('NVIDIA', self.content)

    def test_uzbekistan_compliance_mentioned(self):
        self.assertIn('Uzbekistan', self.content)
        self.assertIn('27.1', self.content)

    def test_no_cloud_subscription_internal_section(self):
        self.assertNotIn('<section id="cloud-subscription"', self.content)

if __name__ == '__main__':
    unittest.main()
