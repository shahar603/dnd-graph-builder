from flask import Blueprint, render_template_string, request, session, redirect, url_for

auth_bp = Blueprint('auth', __name__)

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
        <form action="{{ url_for('auth.set_role') }}" method="post">
            <input type="hidden" name="role" value="dm">
            <button type="submit" class="btn btn-primary">Dungeon Master (DM)</button>
        </form>
        <form action="{{ url_for('auth.set_role') }}" method="post">
            <input type="hidden" name="role" value="player">
            <button type="submit" class="btn btn-secondary">Player</button>
        </form>
    </div>
</body>
</html>
'''

@auth_bp.route('/')
def index():
    """
    Landing page: Allows the user to choose between DM and Player roles.
    """
    return render_template_string(LANDING_PAGE_HTML)

@auth_bp.route('/set_role', methods=['POST'])
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
        return redirect(url_for('auth.index'))
    return redirect(url_for('dashboard.dashboard'))

@auth_bp.route('/logout')
def logout():
    """
    Clears the session and redirects to the landing page.
    """
    session.pop('is_dm', None) # Remove the 'is_dm' key from the session
    return redirect(url_for('auth.index'))
