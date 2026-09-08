#!/usr/bin/env python3
"""
setup_nginx.py — Writes the correct Nginx config for swipies.app and enterprise.swipies.app
  - Serves B2C static files from /var/www/html (swipies.app)
  - Serves Enterprise static files from /var/www/html/enterprise (enterprise.swipies.app)
  - Proxies /api/* to Flask backend on port 5005 for both sites
  - Redirects swipies.app/enterprise -> enterprise.swipies.app
  - Redirects /admin -> /admin.html
"""

import os
import subprocess

# Check if a dedicated certificate for enterprise.swipies.app exists
ent_cert = '/etc/letsencrypt/live/enterprise.swipies.app/fullchain.pem'
ent_key = '/etc/letsencrypt/live/enterprise.swipies.app/privkey.pem'
if not (os.path.exists(ent_cert) and os.path.exists(ent_key)):
    # Fall back to main domain certificate (or wildcard)
    ent_cert = '/etc/letsencrypt/live/swipies.app/fullchain.pem'
    ent_key = '/etc/letsencrypt/live/swipies.app/privkey.pem'

def get_nginx_conf(ent_cert, ent_key):
    return f"""\
# ==============================================================================
# 1. B2C SITE: swipies.app (Cloud SaaS Platform)
# ==============================================================================
server {{
    listen 80;
    listen [::]:80;
    server_name swipies.app www.swipies.app 51.20.190.248;

    # Allow Let's Encrypt HTTP-01 verification
    location /.well-known/acme-challenge/ {{
        root /var/www/html;
    }}

    # Redirect HTTP to HTTPS
    location / {{
        return 301 https://$host$request_uri;
    }}
}}

server {{
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name swipies.app www.swipies.app 51.20.190.248;

    ssl_certificate     /etc/letsencrypt/live/swipies.app/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/swipies.app/privkey.pem;
    include             /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam         /etc/letsencrypt/ssl-dhparams.pem;

    root  /var/www/html;
    index index.html;

    # --- Redirect legacy /enterprise path to dedicated subdomain ---
    location = /enterprise {{
        return 301 https://enterprise.swipies.app/;
    }}
    location /enterprise/ {{
        return 301 https://enterprise.swipies.app/;
    }}

    # --- Exact redirect: /admin -> /admin.html ---
    location = /admin {{
        return 301 /admin.html;
    }}

    # --- Proxy API calls to the Flask backend (port 5005) ---
    location /api/ {{
        proxy_pass         http://127.0.0.1:5005;
        proxy_http_version 1.1;
        proxy_set_header   Host $host;
        proxy_set_header   X-Real-IP $remote_addr;
        proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto $scheme;

        # CORS headers
        add_header 'Access-Control-Allow-Origin'  '*' always;
        add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
        add_header 'Access-Control-Allow-Headers' 'Content-Type, Authorization' always;
        add_header 'Access-Control-Expose-Headers' 'Authorization' always;

        if ($request_method = 'OPTIONS') {{
            add_header 'Access-Control-Allow-Origin'  '*';
            add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS';
            add_header 'Access-Control-Allow-Headers' 'Content-Type, Authorization';
            add_header 'Content-Type' 'text/plain charset=UTF-8';
            add_header 'Content-Length' 0;
            return 204;
        }}
    }}

    # --- Static files ---
    location / {{
        try_files $uri $uri/ $uri.html =404;
    }}

    # Gzip
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml image/svg+xml;
    gzip_min_length 1000;
}}

# ==============================================================================
# 2. ENTERPRISE SITE: enterprise.swipies.app (On-Premise Solution)
# ==============================================================================
server {{
    listen 80;
    listen [::]:80;
    server_name enterprise.swipies.app;

    # Allow Let's Encrypt HTTP-01 verification
    location /.well-known/acme-challenge/ {{
        root /var/www/html;
    }}

    # Redirect HTTP to HTTPS
    location / {{
        return 301 https://$host$request_uri;
    }}
}}

server {{
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name enterprise.swipies.app;

    ssl_certificate     {ent_cert};
    ssl_certificate_key {ent_key};
    include             /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam         /etc/letsencrypt/ssl-dhparams.pem;

    root  /var/www/html/enterprise;
    index index.html;

    # --- Proxy API calls to the shared Flask backend (port 5005) ---
    location /api/ {{
        proxy_pass         http://127.0.0.1:5005;
        proxy_http_version 1.1;
        proxy_set_header   Host $host;
        proxy_set_header   X-Real-IP $remote_addr;
        proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto $scheme;

        # CORS headers
        add_header 'Access-Control-Allow-Origin'  '*' always;
        add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
        add_header 'Access-Control-Allow-Headers' 'Content-Type, Authorization' always;
        add_header 'Access-Control-Expose-Headers' 'Authorization' always;

        if ($request_method = 'OPTIONS') {{
            add_header 'Access-Control-Allow-Origin'  '*';
            add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS';
            add_header 'Access-Control-Allow-Headers' 'Content-Type, Authorization';
            add_header 'Content-Type' 'text/plain charset=UTF-8';
            add_header 'Content-Length' 0;
            return 204;
        }}
    }}

    # --- Shared Legal & Styles fallback ---
    location ~* ^/(terms(\\.html)?|privacy(\\.html)?|styles\\.css)$ {{
        root /var/www/html;
        try_files $uri $uri.html =404;
    }}

    # --- Static files ---
    location / {{
        try_files $uri $uri/ $uri.html =404;
    }}

    # Gzip
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml image/svg+xml;
    gzip_min_length 1000;
}}

# ==============================================================================
# 3. API & APP SUBDOMAINS: api.swipies.app, app.swipies.app
# ==============================================================================
server {{
    listen 80;
    listen [::]:80;
    server_name api.swipies.app;
    return 301 https://$host$request_uri;
}}

server {{
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name api.swipies.app;

    ssl_certificate     /etc/letsencrypt/live/swipies.app/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/swipies.app/privkey.pem;
    include             /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam         /etc/letsencrypt/ssl-dhparams.pem;

    location / {{
        proxy_pass         http://127.0.0.1:9222;
        proxy_http_version 1.1;
        proxy_set_header   Host $host;
        proxy_set_header   X-Real-IP $remote_addr;
        proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto $scheme;

        if ($request_method = 'OPTIONS') {{
            add_header 'Access-Control-Allow-Origin'  '*' always;
            add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
            add_header 'Access-Control-Allow-Headers' 'Content-Type, Authorization' always;
            add_header 'Content-Type' 'text/plain charset=UTF-8';
            add_header 'Content-Length' 0;
            return 204;
        }}
    }}
}}

server {{
    listen 80;
    listen [::]:80;
    server_name app.swipies.app;
    return 301 https://$host$request_uri;
}}

server {{
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name app.swipies.app;

    ssl_certificate     /etc/letsencrypt/live/swipies.app/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/swipies.app/privkey.pem;
    include             /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam         /etc/letsencrypt/ssl-dhparams.pem;

    location / {{
        proxy_pass         http://127.0.0.1:9222;
        proxy_http_version 1.1;
        proxy_set_header   Host $host;
        proxy_set_header   X-Real-IP $remote_addr;
        proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto $scheme;

        if ($request_method = 'OPTIONS') {{
            add_header 'Access-Control-Allow-Origin'  '*' always;
            add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
            add_header 'Access-Control-Allow-Headers' 'Content-Type, Authorization' always;
            add_header 'Content-Type' 'text/plain charset=UTF-8';
            add_header 'Content-Length' 0;
            return 204;
        }}
    }}
}}
"""

NGINX_CONF = get_nginx_conf(ent_cert, ent_key)

conf_path = '/etc/nginx/sites-available/swipies'
enabled_path = '/etc/nginx/sites-enabled/swipies'

# Remove default site if present
default_enabled = '/etc/nginx/sites-enabled/default'
if os.path.exists(default_enabled):
    try:
        os.remove(default_enabled)
        print(f"Removed default nginx site: {default_enabled}")
    except Exception as e:
        print(f"Notice: could not remove default site: {e}")

# Write new config
try:
    with open(conf_path, 'w') as f:
        f.write(NGINX_CONF)
    print(f"Written nginx config: {conf_path}")

    # Enable site
    if not os.path.exists(enabled_path):
        os.symlink(conf_path, enabled_path)
        print(f"Enabled nginx site: {enabled_path}")
    else:
        print(f"Nginx site already enabled: {enabled_path}")
except Exception as e:
    print(f"Local test or execution notice: {e}")

# Automatic Certbot Issuance for enterprise.swipies.app if dedicated cert doesn't exist
ent_target_cert = '/etc/letsencrypt/live/enterprise.swipies.app/fullchain.pem'
ent_target_key = '/etc/letsencrypt/live/enterprise.swipies.app/privkey.pem'
if not (os.path.exists(ent_target_cert) and os.path.exists(ent_target_key)):
    print("Dedicated cert for enterprise.swipies.app not found. Attempting certbot issuance...")
    try:
        subprocess.run(['nginx', '-t'], check=False)
        subprocess.run(['systemctl', 'reload', 'nginx'], check=False)

        res = subprocess.run([
            'certbot', 'certonly', '--webroot',
            '-w', '/var/www/html',
            '-d', 'enterprise.swipies.app',
            '--non-interactive', '--agree-tos',
            '-m', 'info@swipies.app'
        ], capture_output=True, text=True)
        print("Certbot returncode:", res.returncode)
        if res.stdout:
            print("Certbot stdout:", res.stdout[:500])
        if res.stderr:
            print("Certbot stderr:", res.stderr[:500])

        if os.path.exists(ent_target_cert) and os.path.exists(ent_target_key):
            print("Successfully acquired dedicated cert for enterprise.swipies.app! Updating Nginx...")
            with open(conf_path, 'w') as f:
                f.write(get_nginx_conf(ent_target_cert, ent_target_key))
            subprocess.run(['nginx', '-t'], check=False)
            subprocess.run(['systemctl', 'reload', 'nginx'], check=False)
            print("Nginx reloaded with dedicated enterprise certificate.")
    except Exception as e:
        print(f"Notice: certbot issuance attempt: {e}")

print("=== SSL CERTIFICATES ===")
if os.path.exists('/etc/letsencrypt/live'):
    print(os.listdir('/etc/letsencrypt/live'))
    # Print certificate details for swipies.app
    cert_path = '/etc/letsencrypt/live/swipies.app/fullchain.pem'
    if os.path.exists(cert_path):
        try:
            out = subprocess.check_output(['openssl', 'x509', '-in', cert_path, '-text', '-noout'], stderr=subprocess.STDOUT).decode('utf-8')
            for line in out.split('\n'):
                if 'DNS:' in line:
                    print("swipies.app cert covers:", line.strip())
        except Exception as e:
            print("Error reading cert:", e)
else:
    print("No /etc/letsencrypt/live directory")

print("=== AVAILABLE NGINX SITES ===")
if os.path.exists('/etc/nginx/sites-available'):
    print(os.listdir('/etc/nginx/sites-available'))
else:
    print("No /etc/nginx/sites-available directory")

print("Nginx config written successfully. Run: sudo nginx -t && sudo systemctl reload nginx")
