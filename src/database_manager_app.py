from flask import Flask, session, redirect, url_for, request, render_template_string
import os

app = Flask(__name__)
# A secret key is required for session management.
# In a real application, use a strong, randomly generated key and keep it secret.
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

        <h2 class="text-2xl font-semibold text-gray-700 mb-4">Entity Management</h2>
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

        <a href="#" class="btn btn-special">Import Session Notes</a>
        <a href="/logout" class="btn btn-back">Change Role / Logout</a>
    </div>
</body>
</html>
'''





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

@app.route('/logout')
def logout():
    """
    Clears the session and redirects to the landing page.
    """
    session.pop('is_dm', None) # Remove the 'is_dm' key from the session
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
