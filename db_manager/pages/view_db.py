from flask import Blueprint, render_template_string, request, session, redirect, url_for
from utils import get_table_names, get_table_columns, get_table_data

view_db_bp = Blueprint('view_db', __name__)

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

        <form action="{{ url_for('view_db.view_db') }}" method="get" id="viewForm">
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

        <a href="{{ url_for('dashboard.dashboard') }}" class="btn btn-back">Back to Dashboard</a>
    </div>
</body>
</html>
'''

@view_db_bp.route('/view_db')
def view_db():
    if 'is_dm' not in session:
        return redirect(url_for('auth.index'))

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
