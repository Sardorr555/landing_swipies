import sqlite3
from flask import Flask, request, jsonify
import datetime

app = Flask(__name__)

DB_FILE = 'database.sqlite'

def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company TEXT NOT NULL,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT,
                message TEXT,
                referral_code TEXT,
                status TEXT DEFAULT '1', -- 1 = unread, 2 = read
                create_date TEXT NOT NULL
            )
        ''')
        conn.commit()

@app.route('/api/leads', methods=['POST'])
def create_lead():
    data = request.json
    company = data.get('company', '')
    name = data.get('name', '')
    email = data.get('email', '')
    phone = data.get('phone', '')
    message = data.get('message', '')
    referral_code = data.get('referral_code', '')
    create_date = datetime.datetime.utcnow().isoformat() + "Z"
    
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO leads (company, name, email, phone, message, referral_code, create_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (company, name, email, phone, message, referral_code, create_date))
        conn.commit()
        lead_id = cursor.lastrowid
        
    return jsonify({"code": 0, "message": "Success", "data": {"id": lead_id}}), 201

@app.route('/api/leads', methods=['GET'])
def get_leads():
    with sqlite3.connect(DB_FILE) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM leads ORDER BY id DESC')
        rows = cursor.fetchall()
        
    leads = [dict(row) for row in rows]
    return jsonify({"code": 0, "data": leads})

@app.route('/api/leads/<int:lead_id>', methods=['PUT'])
def update_lead(lead_id):
    data = request.json
    new_status = data.get('status')
    if not new_status:
        return jsonify({"code": 1, "message": "Status required"}), 400
        
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE leads SET status = ? WHERE id = ?', (new_status, lead_id))
        conn.commit()
        
    return jsonify({"code": 0, "message": "Updated"})

@app.route('/api/leads/<int:lead_id>', methods=['DELETE'])
def delete_lead(lead_id):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM leads WHERE id = ?', (lead_id,))
        conn.commit()
        
    return jsonify({"code": 0, "message": "Deleted"})

if __name__ == '__main__':
    init_db()
    print(f"Server starting on http://0.0.0.0:5005")
    print(f"Database file: {DB_FILE}")
    app.run(host='0.0.0.0', port=5005)
