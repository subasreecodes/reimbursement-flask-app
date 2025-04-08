#import all the required modules
from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import os
import uuid
from werkzeug.utils import secure_filename
from datetime import datetime

#initialize the application
app = Flask(__name__)
app.secret_key = 'secret_key'

UPLOAD_FOLDER = 'upload'
ALLOWED_MIME = 'application/pdf'
DB_PATH = 'database.db'

if not os.path.exists(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)

#database setup
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reimbursements (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   email TEXT NOT NULL,
                   date TEXT NOT NULL,
                   amount REAL NOT NULL,
                   description TEXT NOT NULL,
                   file_path TEXT NOT NULL
                   )
                   ''')
    conn.commit()
    conn.close()

#routes for three pages 
#home page
@app.route('/', methods = ['POST', 'GET'])
def index():
    if request.method == 'POST':
        email = request.form['email']
        if '@' not in email or '.' not in email:
            flash("🧐 Hmmm...can you enter a valid email address")
            return redirect(url_for('index'))
        session['email'] = email 
        return redirect(url_for('form'))
    return render_template('index.html')

#reimbursement form submission page
@app.route('/form', methods = ['GET', 'POST'])
def form():
    email = session.get('email')
    if not email:
        return redirect(url_for('index'))
    if request.method == 'POST':
        date = request.form['date']
        amount = request.form['amount']
        description = request.form['description']
        file_upload = request.files['file']

        #if file not uploaded
        if file_upload.filename == '':
            flash("🤔you forgot to upload the file...")
            return redirect(url_for('form'))

        #file can have a .pdf acceptable format
        if file_upload.mimetype != 'application/pdf':
            flash("Almost there, make sure it is a PDF formatted file")
            return redirect(url_for('form'))
        
        #save the uploaded file
        filename = secure_filename(file_upload.filename)
        similar_file_name = f"{uuid.uuid4().hex}_{filename}"
        filepath = os.path.join(UPLOAD_FOLDER, similar_file_name)
        file_upload.save(filepath)

        #data in database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO reimbursements (email, date, amount, description, file_path) VALUES (?, ?, ?, ?, ?)
                        ''', (email,date, float(amount), description, filepath))
        conn.commit()
        conn.close()

        return render_template('confirmation.html')
    return render_template('form.html')
#confirmation page
@app.route('/confirmation')
def confirmation():
    return render_template('confirmation.html')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)