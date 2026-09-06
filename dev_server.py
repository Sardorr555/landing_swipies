#!/usr/bin/env python3
"""
dev_server.py — Local development server for Swipies AI (B2C + Enterprise + Admin)
Runs on:
  - Port 5005:
      * B2C Site:        http://localhost:5005/
      * Enterprise Site: http://localhost:5005/enterprise/
      * Admin Panel:     http://localhost:5005/admin
      * Shared API:      http://localhost:5005/api/*
  - Port 5006 (Simulating enterprise.swipies.app):
      * Enterprise Site: http://localhost:5006/
      * Shared API:      http://localhost:5006/api/*
"""

import os
import sys
import threading
from werkzeug.serving import run_simple
from flask import send_from_directory, redirect, request

# Add current dir to path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from api import app, init_db

@app.route('/')
def root():
    # If accessed on port 5006, serve Enterprise site as root
    host_port = request.host.split(':')[-1]
    if host_port == '5006':
        return send_from_directory(os.path.join(BASE_DIR, 'enterprise'), 'index.html')
    return send_from_directory(BASE_DIR, 'index.html')

@app.route('/b2c')
@app.route('/b2c/')
@app.route('/cloud')
@app.route('/cloud/')
def b2c_site():
    return send_from_directory(BASE_DIR, 'index.html')

@app.route('/enterprise/')
@app.route('/enterprise')
def enterprise_site():
    return send_from_directory(os.path.join(BASE_DIR, 'enterprise'), 'index.html')

@app.route('/admin')
def admin_redirect():
    return redirect('/admin.html')

@app.route('/<path:filename>')
def static_files(filename):
    # Check if file exists in enterprise subfolder
    if filename.startswith('enterprise/'):
        rel = filename[len('enterprise/'):]
        if not rel:
            return send_from_directory(os.path.join(BASE_DIR, 'enterprise'), 'index.html')
        ent_file = os.path.join(BASE_DIR, 'enterprise', rel)
        if os.path.exists(ent_file):
            return send_from_directory(os.path.join(BASE_DIR, 'enterprise'), rel)
        if os.path.exists(os.path.join(BASE_DIR, rel)):
            return send_from_directory(BASE_DIR, rel)
        return send_from_directory(os.path.join(BASE_DIR, 'enterprise'), rel)
    
    # If on port 5006, try enterprise folder first
    host_port = request.host.split(':')[-1]
    if host_port == '5006':
        if filename in ('b2c', 'cloud'):
            return send_from_directory(BASE_DIR, 'index.html')
        ent_file = os.path.join(BASE_DIR, 'enterprise', filename)
        if os.path.exists(ent_file):
            return send_from_directory(os.path.join(BASE_DIR, 'enterprise'), filename)

    return send_from_directory(BASE_DIR, filename)

def run_port_5006():
    run_simple('127.0.0.1', 5006, app, use_reloader=False, threaded=True)

if __name__ == '__main__':
    init_db()
    print("=" * 65)
    print("Swipies AI Local Dev Server Started!")
    print("=" * 65)
    print("B2C Site (Cloud SaaS):       http://localhost:5005/")
    print("Enterprise Site:             http://localhost:5005/enterprise/")
    print("Enterprise Site (Port 5006): http://localhost:5006/")
    print("Admin Panel:                 http://localhost:5005/admin")
    print("Unified API (Leads/DB):      http://localhost:5005/api/leads")
    print("=" * 65)

    # Start port 5006 in a background thread
    t = threading.Thread(target=run_port_5006, daemon=True)
    t.start()

    # Start main server on port 5005
    run_simple('127.0.0.1', 5005, app, use_reloader=False, threaded=True)
