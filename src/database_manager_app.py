from flask import Flask, session, redirect, url_for, request, render_template_string
import os
import sqlite3
import re # Import the regular expression module

app = Flask(__name__)
app.secret_key = os.urandom(24)

# --- HTML Templates (Embedded for simplicity) ---

# Landing page HTML with DM/Player choice
LANDING_PAGE_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Choose Your Role</title>
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
            max-width: 400px;
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
            width: 100%;
            margin-bottom: 1rem;
        }
        .btn-primary {
            background-color: #6366f1;
            color: #ffffff;
            border: 1px solid #6366f1;
        }
        .btn-primary:hover {
            background-color: #4f46e5;
        }
        .btn-secondary {
            background-color: #e5e7eb;
            color: #374151;
            border: 1px solid #e5e7eb;
        }
        .btn-secondary:hover {
            background-color: #d1d5db;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="text-3xl font-bold text-gray-800 mb-6">Welcome to D&D Manager</h1>
        <p class="text-gray-600 mb-8">Please choose your role to proceed:</p>
        <form action="/set_role" method="post">
            <input type="hidden" name="role" value="dm">
            <button type="submit" class="btn btn-primary">Dungeon Master (DM)</button>
        </form>
        <form action="/set_role" method="post">
            <input type="hidden" name="role" value="player">
            <button type="submit" class="btn btn-secondary">Player</button>
        </form>
    </div>
</body>
</html>
'''

# Dashboard page HTML with entity/connection options
DASHBOARD_PAGE_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>D&D Dashboard</title>
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
            max-width: 600px;
            padding: 2.5rem;
            background-color: #ffffff;
            border-radius: 0.75rem;
            box-shadow: 0 10px 15px rgba(0, 0, 0, 0.1);
            text-align: center;
        }
        .btn-group {
            display: grid;
            grid-template-columns: 1fr;
            gap: 1rem;
            margin-top: 2rem;
        }
        @media (min-width: 640px) {
            .btn-group {
                grid-template-columns: 1fr 1fr;
            }
        }
        .btn {
            padding: 0.75rem 1.5rem;
            border-radius: 0.5rem;
            font-weight: 600;
            cursor: pointer;
            transition: background-color 0.15s ease-in-out, border-color 0.15s ease-in-out, color 0.15s ease-in-out;
            text-decoration: none; /* For links */
            display: block; /* For links to behave like buttons */
            text-align: center;
        }
        .btn-action {
            background-color: #4ade80; /* Green */
            color: #166534;
            border: 1px solid #4ade80;
        }
        .btn-action:hover {
            background-color: #22c55e;
        }
        .btn-info {
            background-color: #60a5fa; /* Blue */
            color: #1e40af;
            border: 1px solid #60a5fa;
        }
        .btn-info:hover {
            background-color: #3b82f6;
        }
        .btn-danger {
            background-color: #ef4444; /* Red */
            color: #fef2f2;
            border: 1px solid #ef4444;
        }
        .btn-danger:hover {
            background-color: #dc2626;
        }
        .btn-back {
            background-color: #9ca3af; /* Gray */
            color: #ffffff;
            border: 1px solid #9ca3af;
            margin-top: 2rem;
        }
        .btn-back:hover {
            background-color: #6b7280;
        }
        .btn-special {
            background-color: #facc15; /* Yellow */
            color: #78350f;
            border: 1px solid #facc15;
            margin-top: 2rem;
        }
        .btn-special:hover {
            background-color: #eab308;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="text-3xl font-bold text-gray-800 mb-4">D&D Dashboard</h1>
        <p class="text-lg text-gray-700 mb-8">You are logged in as: <span class="font-semibold text-indigo-600">{{ role_display }}</span></p>

        <h2 class="text-2xl font-semibold text-gray-700 mb-4">Database Management</h2>
        <div class="btn-group">
            <a href="/view_db" class="btn btn-info">View Database</a>
        </div>

        <h2 class="text-2xl font-semibold text-gray-700 mt-8 mb-4">Entity Management</h2>
        <div class="btn-group">
            <a href="#" class="btn btn-action">Create New Entity</a>
            <a href="#" class="btn btn-info">Update Existing Entity</a>
            <a href="#" class="btn btn-danger">Delete Existing Entity</a>
        </div>

        <h2 class="text-2xl font-semibold text-gray-700 mt-8 mb-4">Connection Management</h2>
        <div class="btn-group">
            <a href="#" class="btn btn-action">Create New Connection</a>
            <a href="#" class="btn btn-info">Update Existing Connection</a>
            <a href="#" class="btn btn-danger">Delete Existing Connection</a>
        </div>

        <a href="/upload_session" class="btn btn-special">Import Session Notes</a>
        <a href="/logout" class="btn btn-back">Change Role / Logout</a>
    </div>
</body>
</html>
'''

VIEW_DB_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>View Database</title>
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
            max-width: 900px;
            padding: 2.5rem;
            background-color: #ffffff;
            border-radius: 0.75rem;
            box-shadow: 0 10px 15px rgba(0, 0, 0, 0.1);
            text-align: center;
        }
        .form-group {
            margin-bottom: 1.5rem;
        }
        .form-group label {
            display: block;
            margin-bottom: 0.5rem;
            font-weight: 600;
            color: #374151;
        }
        .form-group select, .form-group input[type="text"] {
            width: 100%;
            padding: 0.75rem;
            border: 1px solid #d1d5db;
            border-radius: 0.5rem;
            font-size: 1rem;
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
            margin-top: 1rem;
        }
        .btn-back:hover {
            background-color: #6b7280;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 2rem;
        }
        th, td {
            border: 1px solid #e5e7eb;
            padding: 0.75rem;
            text-align: left;
        }
        th {
            background-color: #f9fafb;
            font-weight: 600;
            color: #374151;
        }
        tr:nth-child(even) {
            background-color: #f3f4f6;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="text-3xl font-bold text-gray-800 mb-6">View Database Tables</h1>

        <form action="/view_db" method="get" id="viewForm">
            <div class="form-group">
                <label for="table_name">Select Table:</label>
                <select name="table_name" id="table_name" onchange="this.form.submit()">
                    <option value="">-- Select a Table --</option>
                    {% for table in tables %}
                        <option value="{{ table }}" {% if table == selected_table %}selected{% endif %}>{{ table }}</option>
                    {% endfor %}
                </select>
            </div>
            {% if selected_table and columns %}
            <div class="form-group">
                <label for="filter_field">Filter by Field:</label>
                <select name="filter_field" id="filter_field">
                    <option value="">-- No Filter --</option>
                    {% for col in columns %}
                        <option value="{{ col }}" {% if col == selected_filter_field %}selected{% endif %}>{{ col }}</option>
                    {% endfor %}
                </select>
            </div>
            <div class="form-group">
                <label for="filter_value">Filter Value:</label>
                <input type="text" name="filter_value" id="filter_value" value="{{ selected_filter_value if selected_filter_value else '' }}">
            </div>
            <button type="submit" class="btn btn-primary">Apply Filter</button>
            {% endif %}
        </form>

        {% if data %}
            <h2 class="text-2xl font-semibold text-gray-700 mt-8 mb-4">Data for {{ selected_table }}</h2>
            <table>
                <thead>
                    <tr>
                        {% for col in columns %}
                            <th>{{ col }}</th>
                        {% endfor %}
                    </tr>
                </thead>
                <tbody>
                    {% for row in data %}
                        <tr>
                            {% for cell in row %}
                                <td>{{ cell }}</td>
                            {% endfor %}
                        </tr>
                    {% endfor %}
                </tbody>
            </table>
        {% elif selected_table and not data and (selected_filter_field or selected_filter_value) %}
            <p class="text-gray-600 mt-4">No data found for {{ selected_table }} with the applied filters.</p>
        {% elif selected_table and not data %}
             <p class="text-gray-600 mt-4">The table '{{ selected_table }}' is empty.</p>
        {% endif %}

        <a href="/dashboard" class="btn btn-back">Back to Dashboard</a>
    </div>
</body>
</html>
'''

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
                {{ message }}
            </div>
        {% endif %}
        <form action="/upload_session" method="post" enctype="multipart/form-data">
            <div class="form-group">
                <label for="session_file" class="sr-only">Upload SQL file</label>
                <input type="file" name="session_file" id="session_file" accept=".sql,.txt" required>
            </div>
            <button type="submit" class="btn btn-primary">Upload and Import</button>
        </form>
        <a href="/dashboard" class="btn btn-back">Back to Dashboard</a>
    </div>
</body>
</html>
'''

DATABASE = 'DB/dnd_database.db' # Define your database file name here

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row # This allows access to columns by name
    return conn

def get_table_names():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    return tables

def get_table_columns(table_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = [row[1] for row in cursor.fetchall()]
    conn.close()
    return columns

def get_table_data(table_name, filter_field=None, filter_value=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = f"SELECT * FROM {table_name}"
    params = []

    if filter_field and filter_value:
        query += f" WHERE {filter_field} LIKE ?"
        params.append(f"%{filter_value}%")

    cursor.execute(query, params)
    data = [list(row) for row in cursor.fetchall()]
    conn.close()
    return data

# --- Flask Routes ---

@app.route('/')
def index():
    """
    Landing page: Allows the user to choose between DM and Player roles.
    """
    return render_template_string(LANDING_PAGE_HTML)

@app.route('/set_role', methods=['POST'])
def set_role():
    """
    Receives the chosen role (DM or Player) and stores it in the session.
    Redirects to the dashboard.
    """
    role = request.form.get('role')
    if role == 'dm':
        session['is_dm'] = True
    elif role == 'player':
        session['is_dm'] = False
    else:
        # Handle invalid role, redirect back to index
        return redirect(url_for('index'))
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    """
    Dashboard page: Displays options based on the chosen role.
    Requires a role to be set in the session.
    """
    if 'is_dm' not in session:
        # If no role is set, redirect back to the landing page
        return redirect(url_for('index'))

    is_dm = session['is_dm']
    role_display = "Dungeon Master" if is_dm else "Player"

    # Render the dashboard HTML, passing the role for display
    return render_template_string(DASHBOARD_PAGE_HTML, role_display=role_display)

@app.route('/view_db')
def view_db():
    if 'is_dm' not in session:
        return redirect(url_for('index'))

    tables = get_table_names()
    selected_table = request.args.get('table_name')
    data = None
    columns = None
    selected_filter_field = request.args.get('filter_field')
    selected_filter_value = request.args.get('filter_value')

    if selected_table:
        columns = get_table_columns(selected_table)
        data = get_table_data(selected_table, selected_filter_field, selected_filter_value)

    return render_template_string(VIEW_DB_HTML,
                                  tables=tables,
                                  selected_table=selected_table,
                                  columns=columns,
                                  data=data,
                                  selected_filter_field=selected_filter_field,
                                  selected_filter_value=selected_filter_value)
    
@app.route('/upload_session', methods=['GET', 'POST'])
def upload_session():
    if 'is_dm' not in session:
        return redirect(url_for('index'))

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
                # Read the entire file content as a single string
                # executescript can handle comments and multiple statements directly.
                sql_script = file.read().decode('utf-8')

                conn = get_db_connection()
                cursor = conn.cursor()

                # Execute the entire script. PRAGMA foreign_keys = ON; needs to be first if present.
                cursor.executescript(sql_script)
                conn.commit()
                conn.close()
                message = "Session notes imported successfully!"
            except sqlite3.Error as e:
                # Catch specific SQLite errors
                message = f"Database error: {e}"
                app.logger.error(f"Error importing session notes: {e}")
            except Exception as e:
                # Catch any other unexpected errors
                message = f"An unexpected error occurred: {e}"
                app.logger.error(f"Unexpected error during session import: {e}")

    return render_template_string(UPLOAD_SESSION_HTML, message=message)

    

@app.route('/logout')
def logout():
    """
    Clears the session and redirects to the landing page.
    """
    session.pop('is_dm', None) # Remove the 'is_dm' key from the session
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Create the database and tables if they don't exist
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    with open('DB/db_init.sql', 'r') as f:
        sql_script = f.read()
    cursor.executescript(sql_script)
    conn.close()
    app.run(debug=True)