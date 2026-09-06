import unittest
import os

class TestAdminDashboard(unittest.TestCase):
    def test_admin_has_lead_source_filter_and_badge(self):
        admin_path = os.path.join(os.path.dirname(__file__), '..', 'admin.html')
        with open(admin_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Must have filter dropdown for lead sources
        self.assertIn('leadSourceFilter', content)
        # Must handle source mapping in mapDatabaseLeads
        self.assertIn('source: sub.source', content)
        # Must define and display Enterprise / B2C badges
        self.assertIn('badge-enterprise', content)
        self.assertIn('badge-b2c', content)

if __name__ == '__main__':
    unittest.main()
