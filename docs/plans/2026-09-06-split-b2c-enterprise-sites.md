# Split Swipies AI into B2C (swipies.app) and Enterprise (enterprise.swipies.app) Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Split the unified Swipies AI platform into two dedicated, reciprocally-linked websites: `swipies.app` for B2C/Cloud SaaS and `enterprise.swipies.app` for Enterprise/On-Premise, powered by a single backend API, shared admin dashboard with lead filtering, and tailored Nginx routing.

**Architecture:** 
- The root project serves `swipies.app` (B2C Cloud SaaS) from `index.html`.
- A dedicated `enterprise/` subdirectory serves `enterprise.swipies.app` from `enterprise/index.html`.
- Both frontends share the same backend (`api.swipies.app`) and database (`database.sqlite`), where leads are tagged with `source: 'b2c'` or `source: 'enterprise'`.
- The single existing admin dashboard (`admin.html`) displays lead source badges and provides filtering without duplicating the admin panel.
- `setup_nginx.py` configures virtual hosts for both domains with 301 redirects from `swipies.app/enterprise` to `enterprise.swipies.app`.

**Tech Stack:**
- Frontend: Semantic HTML5, Vanilla CSS3 (Custom Design System: Technical Dark Slate + Solar Amber / Emerald accents), Vanilla JavaScript with multi-language i18n (EN, RU, UZ).
- Backend: Python 3, Flask, SQLite3, Telegram Bot API notification.
- Infrastructure: Nginx, Systemd, GitHub Actions (`deploy.yml`), Let's Encrypt SSL.

---

### Task 1: Backend API Lead Source Tracking & Database Migration

**Files:**
- Modify: `api.py`
- Create: `tests/test_api_leads.py`

**Step 1: Write the failing test**

Create `tests/test_api_leads.py` to test that `/api/leads` saves and returns `source` (`b2c` vs `enterprise`):

```python
import unittest
import json
import os
import sqlite3
import tempfile
import sys

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import api

class TestLeadSource(unittest.TestCase):
    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp()
        api.DB_FILE = self.db_path
        api.init_db()
        self.client = api.app.test_client()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(self.db_path)

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
        self.assertEqual(data['data'][0]['source'], 'b2c')

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
        self.assertEqual(lead['source'], 'enterprise')

if __name__ == '__main__':
    unittest.main()
```

**Step 2: Run test to verify it fails**

Run: `python -m unittest tests/test_api_leads.py`
Expected: FAIL (KeyError: 'source' or column not present).

**Step 3: Update `api.py` with automatic migration and source support**

- In `init_db()`:
  Check if `source` column exists in `leads` table; if not, execute:
  `ALTER TABLE leads ADD COLUMN source TEXT DEFAULT 'b2c'`
- In `create_lead()`:
  Extract `source = data.get('source', 'b2c')`.
  Insert `source` into `INSERT INTO leads (..., source)`.
  Include `🌐 Source: Enterprise (enterprise.swipies.app)` or `🌐 Source: B2C (swipies.app)` in Telegram notification.

**Step 4: Run test to verify it passes**

Run: `python -m unittest tests/test_api_leads.py`
Expected: PASS with 2 passed tests.

**Step 5: Commit**

```bash
git add api.py tests/test_api_leads.py
git commit -m "feat(api): add source tag and db migration for b2c and enterprise leads"
```

---

### Task 2: Admin Dashboard Lead Source Badges & Filter

**Files:**
- Modify: `admin.html`
- Create: `tests/test_admin_ui.py`

**Step 1: Write test to verify admin markup and logic**

Create `tests/test_admin_ui.py`:

```python
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
        self.assertIn('source:', content)
        # Must display Enterprise / B2C badges
        self.assertIn('badge-enterprise', content)
        self.assertIn('badge-b2c', content)

if __name__ == '__main__':
    unittest.main()
```

**Step 2: Run test to verify it fails**

Run: `python -m unittest tests/test_admin_ui.py`
Expected: FAIL with `AssertionError: 'leadSourceFilter' not found in content`.

**Step 3: Implement changes in `admin.html`**

- In CSS inside `admin.html`:
  Add badge styles `.badge-enterprise` (amber/purple subtle gradient with crisp border) and `.badge-b2c` (cyan/blue subtle badge).
- In Submissions Header / Toolbar:
  Add filter `<select id="leadSourceFilter" class="filter-select" onchange="filterSubmissionsBySource()">`:
  - `All Channels (B2C & Enterprise)`
  - `Enterprise Leads (enterprise.swipies.app)`
  - `B2C Leads (swipies.app)`
- In `mapDatabaseLeads(leads)`:
  Include `source: sub.source || 'b2c'`.
- In `renderSubmissionsTable()`:
  Filter rows based on `leadSourceFilter` value.
  Render source badge next to company / name.
- In Overview dashboard stats:
  Display enterprise leads count indicator.

**Step 4: Run test to verify it passes**

Run: `python -m unittest tests/test_admin_ui.py`
Expected: PASS.

**Step 5: Commit**

```bash
git add admin.html tests/test_admin_ui.py
git commit -m "feat(admin): add enterprise vs b2c lead filter and source badges"
```

---

### Task 3: Refactor B2C Website (`index.html`) for Cloud SaaS Focus

**Files:**
- Modify: `index.html`
- Create: `tests/test_b2c_site.py`

**Step 1: Write test for B2C site structure**

Create `tests/test_b2c_site.py`:

```python
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

if __name__ == '__main__':
    unittest.main()
```

**Step 2: Run test to verify it fails**

Run: `python -m unittest tests/test_b2c_site.py`
Expected: FAIL.

**Step 3: Refactor `index.html`**

- Update canonical link: `<link rel="canonical" href="https://swipies.app/">`.
- Update header navigation:
  - Add "Enterprise" navigation link with external arrow indicator linking to `https://enterprise.swipies.app`.
  - Keep: Cloud Features (`#cloud-subscription`), Supported Models (`#partners`), Pricing (`#pricing`), FAQ (`#faq`), "Try Free" button (`login.html`).
- Hero section:
  - Focus on creating AI agents & chatbots in minutes without managing servers.
  - CTAs: "Start Free" (`login.html`) and "Explore Plans" (`#pricing`).
- Streamlined sections:
  - Section 01: Instant Cloud SaaS (Create agents in minutes, connect any model, universal integrations).
  - Section 02: Universal Integrations & Supported Models (React, Flutter, Telegram, WhatsApp, OpenAI, Claude, DeepSeek, Grok).
  - Section 03: Pricing (Basic $20/mo, Pro $40/mo, Self-Hosted License $199/yr, + Enterprise banner directing to `enterprise.swipies.app`).
  - Section 04: Dedicated Enterprise Upsell Section (`#enterprise-upsell`):
    - "Need an On-Premise Solution?" / "Нужно On-Premise решение для компании?"
    - Highlights: 100% data sovereignty, air-gapped deployment, custom LLM integration, SLA guarantee.
    - CTA button: "Learn About Enterprise →" (`https://enterprise.swipies.app`).
  - Section 05: FAQ tailored for Cloud SaaS (Limits, datasets, model keys, security, support).
  - Section 06: Contact form sending `source: 'b2c'`.
- Remove from `index.html`:
  - Problem section ("Why Standard AI Fails Enterprise")
  - Heavy On-Premise RAG architecture section
  - 1-day deployment SLA corporate section
  - Air-gapped server requirements section
  - Corporate Use cases (Banks, Legal, Large Enterprise)
- Update multi-language dictionaries (`T.en`, `T.ru`, `T.uz`) to match B2C content.

**Step 4: Run test to verify it passes**

Run: `python -m unittest tests/test_b2c_site.py`
Expected: PASS.

**Step 5: Commit**

```bash
git add index.html tests/test_b2c_site.py
git commit -m "feat(b2c): streamline swipies.app for cloud saas with enterprise upsell and cross-navigation"
```

---

### Task 4: Build Enterprise Website (`enterprise/index.html`)

**Files:**
- Create: `enterprise/index.html`
- Create: `tests/test_enterprise_site.py`

**Step 1: Write test for Enterprise site structure**

Create `tests/test_enterprise_site.py`:

```python
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

    def test_has_cloud_backlink(self):
        # Must have link back to swipies.app
        self.assertIn('https://swipies.app', self.content)

    def test_has_enterprise_core_sections(self):
        self.assertIn('Why Standard AI Fails Enterprise', self.content)
        self.assertIn('On-Premise RAG', self.content)
        self.assertIn('install.sh', self.content)
        self.assertIn('Minimum Server Requirements', self.content)

    def test_lead_submission_tags_enterprise(self):
        self.assertIn("source: 'enterprise'", self.content)

if __name__ == '__main__':
    unittest.main()
```

**Step 2: Run test to verify it fails**

Run: `python -m unittest tests/test_enterprise_site.py`
Expected: FAIL (`enterprise/index.html must exist`).

**Step 3: Create `enterprise/index.html`**

- Build full standalone HTML5 document using the unified Swipies design system with a more executive, high-trust tone:
  - Canonical: `https://enterprise.swipies.app/`
  - Header with Enterprise badge and backlink: `<a href="https://swipies.app" class="nav-cloud-link">Cloud SaaS / Start Free →</a>`
  - Hero: Private Enterprise AI & On-Premise RAG on Your Infrastructure. CTA: "Talk to Sales / Request Audit" (`#contact`).
  - Section 01: Why Standard AI Fails Enterprise (Data leaves perimeter, generic AI, no control over stack).
  - Section 02: On-Premise RAG Solution (Full pipeline, works with internal data, any LLM/air-gapped, white-label OEM, Uzbekistan local server deployment).
  - Section 03: Deployment Process (1 business day audit -> deployment -> go live).
  - Section 04: Self-Hosted Server Requirements & Automated Setup (`install.sh`, 6 cores, 16 GB RAM, offline autonomy).
  - Section 05: Industry Use Cases (SaaS/ERP platforms, Banks & Finance, Legal & Compliance, Large Enterprises).
  - Section 06: Supported AI Engines (OpenAI, Claude, Grok, DeepSeek, Ollama, vLLM, private models).
  - Section 07: Enterprise Pricing (Self-Hosted License $199/yr + Enterprise Custom with dedicated SLA and on-premise installation).
  - Section 08: Enterprise FAQ (Data sovereignty, SLA guarantees, Uzbekistan Law on Personal Data compliance, white-label).
  - Section 09: Contact / "Talk to Sales" form submitting to `/api/leads` with `source: 'enterprise'`.
  - Multi-language support (EN, RU, UZ) with dedicated enterprise translations dictionary.

**Step 4: Run test to verify it passes**

Run: `python -m unittest tests/test_enterprise_site.py`
Expected: PASS.

**Step 5: Commit**

```bash
git add enterprise/index.html tests/test_enterprise_site.py
git commit -m "feat(enterprise): create enterprise.swipies.app frontend with on-premise focus and cloud back-link"
```

---

### Task 5: Nginx Configuration & Multi-Domain Routing

**Files:**
- Modify: `setup_nginx.py`
- Modify: `.github/workflows/deploy.yml`
- Create: `tests/test_nginx_config.py`

**Step 1: Write test for Nginx configuration generator**

Create `tests/test_nginx_config.py`:

```python
import unittest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import setup_nginx

class TestNginxConfig(unittest.TestCase):
    def test_nginx_contains_both_domains_and_redirect(self):
        conf = setup_nginx.NGINX_CONF
        
        # B2C site
        self.assertIn('server_name swipies.app', conf)
        # Enterprise site
        self.assertIn('server_name enterprise.swipies.app', conf)
        # Root paths
        self.assertIn('/var/www/html', conf)
        self.assertIn('enterprise', conf)
        # Redirect swipies.app/enterprise to enterprise.swipies.app
        self.assertIn('enterprise.swipies.app', conf)
        # API proxy
        self.assertIn('proxy_pass         http://127.0.0.1:5005', conf)

if __name__ == '__main__':
    unittest.main()
```

**Step 2: Run test to verify it fails**

Run: `python -m unittest tests/test_nginx_config.py`
Expected: FAIL (`enterprise.swipies.app not in conf`).

**Step 3: Implement changes in `setup_nginx.py` & `.github/workflows/deploy.yml`**

- In `setup_nginx.py`:
  - Add 301 redirect inside `swipies.app` server block:
    ```nginx
    location = /enterprise {
        return 301 https://enterprise.swipies.app/;
    }
    location = /enterprise/ {
        return 301 https://enterprise.swipies.app/;
    }
    ```
  - Add virtual host server block for `enterprise.swipies.app`:
    - Port 80 redirect to HTTPS.
    - Port 443 SSL server block with `root /var/www/html/enterprise;`.
    - Handle SSL certificates dynamically (use `enterprise.swipies.app` cert if exists, or fallback to wildcard / `swipies.app` cert).
    - API proxy to port 5005 with full CORS headers.
    - Gzip compression, static file caching, and try_files fallback.
- In `.github/workflows/deploy.yml`:
  - Verify static file copy copies both `index.html` and `enterprise/` directory to `/var/www/html/`.

**Step 4: Run test to verify it passes**

Run: `python -m unittest tests/test_nginx_config.py`
Expected: PASS.

**Step 5: Commit**

```bash
git add setup_nginx.py .github/workflows/deploy.yml tests/test_nginx_config.py
git commit -m "feat(nginx): configure enterprise.swipies.app virtual host and 301 redirects"
```

---

### Task 6: End-to-End Verification & Documentation

**Files:**
- Create: `tests/test_e2e_split.py`
- Create: `docs/MULTI_SITE_DEPLOYMENT.md`

**Step 1: Write end-to-end integrity test**

Verify:
- All required files exist.
- No broken links between `swipies.app` and `enterprise.swipies.app`.
- Translations dictionaries on both sites have identical key structure for shared components.
- API endpoints handle both channels with full test coverage.

**Step 2: Run all tests in repository**

Run: `python -m unittest discover -s tests -p "test_*.py"`
Expected: All tests pass.

**Step 3: Document deployment and DNS guide**

Create `docs/MULTI_SITE_DEPLOYMENT.md` detailing:
- DNS configuration (A / CNAME for `enterprise.swipies.app`).
- Certbot instructions for SSL certificate on `enterprise.swipies.app`.
- How Nginx routes each subdomain.
- How the shared admin panel manages leads from both channels.

**Step 4: Commit**

```bash
git add tests/test_e2e_split.py docs/MULTI_SITE_DEPLOYMENT.md
git commit -m "docs: add multi-site architecture documentation and e2e validation suite"
```
