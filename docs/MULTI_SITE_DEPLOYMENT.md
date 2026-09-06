# Multi-Site Deployment & Lead Routing Guide

This document describes the dual-site architecture splitting Swipies AI into two distinct frontends:
1. **B2C Platform (`swipies.app`)** — Cloud SaaS for instant self-serve subscription, pre-packaged token tiers, chatbot embed scripts, and public integrations.
2. **Enterprise Portal (`enterprise.swipies.app`)** — On-premise RAG, data sovereignty, air-gapped installation (`install.sh`), hardware sizing, legal compliance (Uzbekistan Article 27.1), and "Talk to Sales" lead generation.

Both sites share a single backend API (`api.swipies.app`), single database (`database.sqlite`), and a single unified admin panel (`admin.html`).

---

## 1. Domain Architecture

| Domain / Subdomain | Target Audience | Root Directory | Port / Upstream |
| :--- | :--- | :--- | :--- |
| `swipies.app` | B2C / Cloud SaaS users | `/var/www/html` | Static HTML/JS |
| `enterprise.swipies.app` | Banks, Gov, Telecom, Enterprise | `/var/www/html/enterprise` | Static HTML/JS |
| `api.swipies.app` | Backend API & Services | N/A | Flask (port 5005) & RAG (port 9222) |
| `app.swipies.app` | Cloud Web Console | N/A | Port 9222 |

---

## 2. DNS Configuration

To activate the enterprise subdomain, create an **A Record** at your DNS registrar (Cloudflare, Reg.ru, Namecheap, etc.):

```text
Type:    A
Name:    enterprise
Value:   51.20.190.248
TTL:     Auto / 300
```

Verify DNS propagation:
```bash
dig +short enterprise.swipies.app
# Should return 51.20.190.248
```

---

## 3. SSL Certificate Setup (Certbot)

### Option A: Dedicated Subdomain Certificate (Recommended)
Run on the server:
```bash
sudo certbot certonly --nginx -d enterprise.swipies.app
```
Certificates will be saved to:
- `/etc/letsencrypt/live/enterprise.swipies.app/fullchain.pem`
- `/etc/letsencrypt/live/enterprise.swipies.app/privkey.pem`

### Option B: Automatic Fallback
`setup_nginx.py` automatically checks if `/etc/letsencrypt/live/enterprise.swipies.app/fullchain.pem` exists. If not, it falls back to `/etc/letsencrypt/live/swipies.app/fullchain.pem` so that Nginx reloads cleanly without downtime even before the dedicated certificate is created.

---

## 4. Nginx Routing Configuration

Nginx configuration is managed centrally via `setup_nginx.py`.

### Key Features:
- **B2C Site (`swipies.app`)**:
  - Serves from `/var/www/html`.
  - Redirects legacy `/enterprise` and `/enterprise/` URLs to `https://enterprise.swipies.app/` with HTTP 301.
  - Proxies `/api/` calls to `http://127.0.0.1:5005`.
  - Redirects `/admin` to `/admin.html`.
- **Enterprise Site (`enterprise.swipies.app`)**:
  - Serves from `/var/www/html/enterprise`.
  - Proxies `/api/` calls to the same shared Flask backend (`http://127.0.0.1:5005`).
  - Implements CORS headers and HTTP -> HTTPS redirect.
- **Cross-Site Navigation**:
  - `swipies.app` header contains `Enterprise Edition ↗` pointing to `https://enterprise.swipies.app`.
  - `enterprise.swipies.app` header contains `Cloud / Start Free →` pointing to `https://swipies.app`.

To test and reload Nginx on the server:
```bash
sudo python3 ~/landing_swipies/setup_nginx.py
sudo nginx -t && sudo systemctl reload nginx
```

---

## 5. Lead Routing & Shared Admin Panel

### Lead Capture:
- **B2C Site (`index.html`)**: The contact form submits to `/api/leads` with `source: 'b2c'`.
- **Enterprise Site (`enterprise/index.html`)**: The "Talk to Sales" form submits to `/api/leads` with `source: 'enterprise'`.

### Backend Processing (`api.py`):
- SQLite database `leads` table includes a `source` column (`b2c` or `enterprise`).
- Database schema migrations run automatically on startup via `init_db()`.
- Telegram notifications automatically include the channel in the message header:
  - `🔔 [B2C Lead] Новая заявка на Swipies AI`
  - `🏢 [Enterprise Lead] Новая заявка на Swipies AI`

### Unified Admin Panel (`admin.html`):
- Access: `https://swipies.app/admin.html` (or via `/admin`).
- Channel Filter dropdown allows filtering by:
  - **All Channels (All Leads)**
  - **Enterprise Leads (On-Premise)**
  - **B2C Leads (Cloud SaaS)**
- Table and overview widgets display color-coded badges:
  - `Enterprise` (Purple badge)
  - `B2C` (Blue badge)

---

## 6. Automated Deployment (GitHub Actions)

When changes are pushed to `swipies_25`, the workflow `.github/workflows/deploy.yml` automatically:
1. Pulls the latest code to `~/landing_swipies`.
2. Copies all files (including `enterprise/`) to `/var/www/html/`.
3. Sets permissions (`chown -R www-data:www-data /var/www/html`).
4. Restarts the Flask API systemd service (`swipies-api`).
5. Runs `setup_nginx.py` and reloads Nginx.

---

## 7. Verification Checklist

- [x] `index.html` canonical points to `https://swipies.app/`
- [x] `index.html` header links to `https://enterprise.swipies.app`
- [x] `index.html` contact form tags leads with `source: 'b2c'`
- [x] `enterprise/index.html` canonical points to `https://enterprise.swipies.app/`
- [x] `enterprise/index.html` header links back to `https://swipies.app`
- [x] `enterprise/index.html` contact form tags leads with `source: 'enterprise'`
- [x] Database migration adds `source` column to `leads`
- [x] `admin.html` displays channel badge and channel filter dropdown
- [x] `setup_nginx.py` contains server blocks for `swipies.app` and `enterprise.swipies.app`
- [x] Full test suite (26 tests) passes
