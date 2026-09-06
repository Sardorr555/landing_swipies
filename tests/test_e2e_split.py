import unittest
import os
import sys
import json
import sqlite3
import tempfile
import gc

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from api import app, init_db

class TestE2ESplit(unittest.TestCase):
    def setUp(self):
        self.root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        
        # Paths to files
        self.b2c_path = os.path.join(self.root_dir, 'index.html')
        self.ent_path = os.path.join(self.root_dir, 'enterprise', 'index.html')
        self.admin_path = os.path.join(self.root_dir, 'admin.html')
        self.nginx_path = os.path.join(self.root_dir, 'setup_nginx.py')

        # Load file contents
        with open(self.b2c_path, 'r', encoding='utf-8') as f:
            self.b2c_html = f.read()
        with open(self.ent_path, 'r', encoding='utf-8') as f:
            self.ent_html = f.read()
        with open(self.admin_path, 'r', encoding='utf-8') as f:
            self.admin_html = f.read()
        with open(self.nginx_path, 'r', encoding='utf-8') as f:
            self.nginx_script = f.read()

        # Set up temporary database for Flask API integration
        self.db_fd, self.db_path = tempfile.mkstemp(suffix='.sqlite')
        os.close(self.db_fd)
        
        import api
        self.original_db = api.DB_FILE
        api.DB_FILE = self.db_path
        init_db()

        app.config['TESTING'] = True
        self.client = app.test_client()

    def tearDown(self):
        import api
        api.DB_FILE = self.original_db
        gc.collect()
        if os.path.exists(self.db_path):
            try:
                os.unlink(self.db_path)
            except Exception:
                pass

    def test_cross_navigation_integrity(self):
        # 1. B2C site must link to enterprise subdomain
        self.assertIn('https://enterprise.swipies.app', self.b2c_html)
        self.assertIn('id="enterprise-upsell"', self.b2c_html)

        # 2. Enterprise site must link back to B2C site
        self.assertIn('https://swipies.app', self.ent_html)
        self.assertIn('nav-b2c-backlink', self.ent_html)

    def test_b2c_and_enterprise_lead_tagging_in_frontend(self):
        # B2C frontend sends source: 'b2c'
        self.assertIn("source: 'b2c'", self.b2c_html)

        # Enterprise frontend sends source: 'enterprise'
        self.assertIn("source: 'enterprise'", self.ent_html)

    def test_full_lead_lifecycle_b2c_and_enterprise(self):
        # Submit a lead from B2C site
        b2c_payload = {
            "company": "Startup Corp",
            "name": "Jane User",
            "email": "jane@startup.com",
            "phone": "+998901234567",
            "message": "Interested in B2C Pro subscription",
            "source": "b2c"
        }
        res1 = self.client.post('/api/leads', data=json.dumps(b2c_payload), content_type='application/json')
        self.assertEqual(res1.status_code, 201)

        # Submit a lead from Enterprise site
        ent_payload = {
            "company": "National Bank",
            "name": "Head of IT",
            "email": "it@bank.uz",
            "phone": "+998909876543",
            "message": "Need on-premise RAG deployment for 500 branch staff",
            "source": "enterprise"
        }
        res2 = self.client.post('/api/leads', data=json.dumps(ent_payload), content_type='application/json')
        self.assertEqual(res2.status_code, 201)

        # Retrieve all leads via GET /api/leads
        get_res = self.client.get('/api/leads')
        data = json.loads(get_res.data)
        self.assertEqual(data.get('code'), 0)
        leads = data.get('data', [])

        sources = {lead['email']: lead.get('source') for lead in leads}
        self.assertEqual(sources.get('jane@startup.com'), 'b2c')
        self.assertEqual(sources.get('it@bank.uz'), 'enterprise')

    def test_admin_panel_supports_filtering_both_sources(self):
        self.assertIn('id="leadSourceFilter"', self.admin_html)
        self.assertIn('badge-enterprise', self.admin_html)
        self.assertIn('badge-b2c', self.admin_html)
        self.assertIn('source: sub.source', self.admin_html)

    def test_nginx_routing_integrity(self):
        # Main B2C domain
        self.assertIn('server_name swipies.app', self.nginx_script)
        # Dedicated Enterprise domain
        self.assertIn('server_name enterprise.swipies.app', self.nginx_script)
        # Enterprise root directory
        self.assertIn('/var/www/html/enterprise', self.nginx_script)
        # Legacy path redirect
        self.assertIn('location = /enterprise', self.nginx_script)
        self.assertIn('https://enterprise.swipies.app/', self.nginx_script)

if __name__ == '__main__':
    unittest.main()
