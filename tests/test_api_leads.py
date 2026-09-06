import unittest
import json
import os
import sqlite3
import tempfile
import sys
import gc

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import api

class TestLeadSource(unittest.TestCase):
    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp()
        os.close(self.db_fd)
        api.DB_FILE = self.db_path
        api.init_db()
        self.client = api.app.test_client()

    def tearDown(self):
        gc.collect()
        if os.path.exists(self.db_path):
            try:
                os.unlink(self.db_path)
            except PermissionError:
                pass

    def test_create_b2c_lead_default(self):
        payload = {
            "company": "B2C User Co",
            "name": "John Doe",
            "email": "john@example.com",
            "message": "Interested in Pro plan"
        }
        resp = self.client.post('/api/leads', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(resp.status_code, 201)
        
        get_resp = self.client.get('/api/leads')
        data = json.loads(get_resp.data)
        self.assertEqual(data['code'], 0)
        self.assertEqual(len(data['data']), 1)
        self.assertEqual(data['data'][0].get('source'), 'b2c')

    def test_create_enterprise_lead(self):
        payload = {
            "company": "Enterprise Bank Corp",
            "name": "Jane Smith",
            "email": "jane@bank.uz",
            "message": "Need on-premise RAG deployment",
            "source": "enterprise"
        }
        resp = self.client.post('/api/leads', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(resp.status_code, 201)
        
        get_resp = self.client.get('/api/leads')
        data = json.loads(get_resp.data)
        self.assertEqual(data['code'], 0)
        lead = [l for l in data['data'] if l['email'] == 'jane@bank.uz'][0]
        self.assertEqual(lead.get('source'), 'enterprise')

    def test_leads_table_migration_existing_db(self):
        # Create an old database without 'source' column
        old_db_fd, old_db_path = tempfile.mkstemp()
        os.close(old_db_fd)
        try:
            with sqlite3.connect(old_db_path) as conn:
                conn.execute('''
                    CREATE TABLE leads (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        company TEXT NOT NULL,
                        name TEXT NOT NULL,
                        email TEXT NOT NULL,
                        phone TEXT,
                        message TEXT,
                        referral_code TEXT,
                        status TEXT DEFAULT '1',
                        create_date TEXT NOT NULL
                    )
                ''')
                conn.execute('''
                    INSERT INTO leads (company, name, email, phone, message, referral_code, create_date)
                    VALUES ('Old Co', 'Old User', 'old@co.com', '123', 'Old msg', 'REF', '2026-01-01')
                ''')
                conn.commit()

            api.DB_FILE = old_db_path
            # Run init_db which should migrate the table
            api.init_db()

            with sqlite3.connect(old_db_path) as conn:
                conn.row_factory = sqlite3.Row
                row = conn.execute('SELECT * FROM leads WHERE email = "old@co.com"').fetchone()
                self.assertIn('source', row.keys())
                self.assertEqual(row['source'], 'b2c')
        finally:
            gc.collect()
            if os.path.exists(old_db_path):
                try:
                    os.unlink(old_db_path)
                except PermissionError:
                    pass

if __name__ == '__main__':
    unittest.main()
