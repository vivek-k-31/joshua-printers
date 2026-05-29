from flask import Flask, request, jsonify, render_template, redirect, url_for
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)

DB_PATH = 'enquiries.db'

# ─── DB SETUP ───
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS enquiries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            contact TEXT NOT NULL,
            service TEXT NOT NULL,
            message TEXT,
            submitted_at TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# ─── HOME PAGE ───
@app.route('/')
def index():
    return render_template('index.html')

# ─── FORM SUBMIT ───
@app.route('/submit', methods=['POST'])
def submit():
    data = request.get_json()

    name    = data.get('name', '').strip()
    contact = data.get('contact', '').strip()
    service = data.get('service', '').strip()
    message = data.get('message', '').strip()

    if not name or not contact or not service:
        return jsonify({'success': False, 'error': 'Required fields missing'}), 400

    submitted_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO enquiries (name, contact, service, message, submitted_at)
        VALUES (?, ?, ?, ?, ?)
    ''', (name, contact, service, message, submitted_at))
    conn.commit()
    conn.close()

    return jsonify({'success': True, 'message': "Thank you! We'll get back to you shortly."})

# ─── ADMIN PAGE ───
@app.route('/admin')
def admin():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM enquiries ORDER BY submitted_at DESC')
    enquiries = c.fetchall()
    conn.close()
    return render_template('admin.html', enquiries=enquiries)

# ─── DELETE ENQUIRY ───
@app.route('/admin/delete/<int:id>', methods=['POST'])
def delete_enquiry(id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('DELETE FROM enquiries WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)