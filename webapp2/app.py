from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
from google.cloud import storage
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Predefined users for authentication
users = {
    'user1': 'password1',
    'user2': 'password2'
}

# Google Cloud Storage configuration
bucket_name = 'wildbucket46'
data_folder = 'data/'

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def do_login():
    username = request.form['username']
    password = request.form['password']
    if username in users and users[username] == password:
        session['username'] = username
        return redirect(url_for('files'))
    else:
        return 'Invalid credentials', 401

@app.route('/files')
def files():
    if 'username' not in session:
        return redirect(url_for('login'))

    client = storage.Client()
    bucket = client.get_bucket(bucket_name)
    blobs = bucket.list_blobs(prefix=data_folder)

    files_dict = {}
    for blob in blobs:
        folder = blob.time_created.strftime('%Y-%m-%d')
        if folder not in files_dict:
            files_dict[folder] = []
        files_dict[folder].append(blob.name[len(data_folder):])

    return render_template('files.html', files=files_dict)

@app.route('/download/<path:filename>')
def download_file(filename):
    client = storage.Client()
    bucket = client.get_bucket(bucket_name)
    blob = bucket.blob(data_folder + filename)

    download_dir = '/tmp'
    file_path = os.path.join(download_dir, filename)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    blob.download_to_filename(file_path)

    return send_from_directory(download_dir, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
