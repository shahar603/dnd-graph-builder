from flask import Blueprint, render_template_string, request, session, redirect, url_for, current_app
import sqlite3
import os
from utils import get_db_connection

import_notes_bp = Blueprint('import_notes', __name__)

UPLOAD_SESSION_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Import Session Notes</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Inter', sans-serif;
            background-color: #f3f4f6;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
        }
        .container {
            max-width: 500px;
            padding: 2.5rem;
            background-color: #ffffff;
            border-radius: 0.75rem;
            box-shadow: 0 10px 15px rgba(0, 0, 0, 0.1);
            text-align: center;
        }
        .btn {
            padding: 0.75rem 1.5rem;
            border-radius: 0.5rem;
            font-weight: 600;
            cursor: pointer;
            transition: background-color 0.15s ease-in-out, border-color 0.15s ease-in-out, color 0.15s ease-in-out;
            text-decoration: none;
            display: inline-block;
            text-align: center;
            margin-top: 1rem;
        }
        .btn-primary {
            background-color: #6366f1;
            color: #ffffff;
            border: 1px solid #6366f1;
        }
        .btn-primary:hover {
            background-color: #4f46e5;
        }
        .btn-back {
            background-color: #9ca3af;
            color: #ffffff;
            border: 1px solid #9ca3af;
            margin-left: 1rem;
        }
        .btn-back:hover {
            background-color: #6b7280;
        }
        .message {
            margin-top: 1.5rem;
            padding: 1rem;
            border-radius: 0.5rem;
            font-weight: 500;
            text-align: left; /* Align text left for better readability of error messages */
            word-wrap: break-word; /* Ensure long messages wrap */
        }
        .message.success {
            background-color: #d1fae5; /* green-100 */
            color: #065f46; /* green-700 */
        }
        .message.error {
            background-color: #fee2e2; /* red-100 */
            color: #991b1b; /* red-700 */
        }
        .form-group {
            margin-bottom: 1.5rem;
        }
        .form-group input[type="file"] {
            width: 100%;
            padding: 0.75rem;
            border: 1px solid #d1d5db;
            border-radius: 0.5rem;
            font-size: 1rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="text-3xl font-bold text-gray-800 mb-6">Import Session Notes</h1>
        {% if message %}
            <div class="message {{ 'success' if 'successfully' in message else 'error' }}">
                <pre>{{ message }}</pre> </div>
        {% endif %}
        <form action="{{ url_for('import_notes.upload_session') }}" method="post" enctype="multipart/form-data">
            <div class="form-group">
                <label for="session_file" class="sr-only">Upload SQL file</label>
                <input type="file" name="session_file" id="session_file" accept=".sql,.txt" required>
            </div>
            <button type="submit" class="btn btn-primary">Upload and Import</button>
        </form>
        <a href="{{ url_for('dashboard.dashboard') }}" class="btn btn-back">Back to Dashboard</a>
    </div>
</body>
</html>
'''

@import_notes_bp.route('/upload_session', methods=['GET', 'POST'])
def upload_session():
    if 'is_dm' not in session:
        return redirect(url_for('auth.index'))

    message = None

    if request.method == 'POST':
        if 'session_file' not in request.files:
            message = "No file part"
            return render_template_string(UPLOAD_SESSION_HTML, message=message)

        file = request.files['session_file']

        if file.filename == '':
            message = "No selected file"
            return render_template_string(UPLOAD_SESSION_HTML, message=message)

        if file:
            try:
                sql_script = file.read().decode('utf-8')

                conn = get_db_connection()
                cursor = conn.cursor()

                # Execute the entire script. PRAGMA foreign_keys = ON; needs to be first if present.
                cursor.executescript(sql_script)
                conn.commit()
                # Removed conn.close() as connection is managed by app.teardown_appcontext
                message = "Session notes imported successfully!"
            except sqlite3.Error as e:
                # Catch specific SQLite errors and provide the full error message
                message = f"Database error: {e}. Please check your SQL script for syntax errors or constraint violations."
                current_app.logger.error(f"Error importing session notes: {e}")
            except Exception as e:
                # Catch any other unexpected errors
                message = f"An unexpected error occurred: {e}"
                current_app.logger.error(f"Unexpected error during session import: {e}")

    return render_template_string(UPLOAD_SESSION_HTML, message=message)
