from flask import Blueprint, render_template_string, request, session, redirect, url_for
from utils import (
    delete_character,
    delete_player,
    delete_item,
    delete_location,
    delete_event,
    delete_session,
    delete_player_character,
    delete_event_participant,
    delete_generic_relation
)

delete_entity_bp = Blueprint('delete_entity', __name__)

DELETE_ENTITY_SELECT_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Delete Existing Entity</title>
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
        .form-group {
            margin-bottom: 1.5rem;
            text-align: left;
        }
        label {
            display: block;
            margin-bottom: 0.5rem;
            font-weight: 500;
            color: #374151;
        }
        input[type="number"] {
            width: 100%;
            padding: 0.75rem;
            border: 1px solid #d1d5db;
            border-radius: 0.5rem;
            font-size: 1rem;
            transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
        }
        input[type="number"]:focus {
            border-color: #6366f1;
            outline: 0;
            box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.25);
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
        .btn-danger {
            background-color: #ef4444;
            color: #fef2f2;
            border: 1px solid #ef4444;
        }
        .btn-danger:hover {
            background-color: #dc2626;
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
            text-align: left;
            word-wrap: break-word;
        }
        .message.success {
            background-color: #d1fae5;
            color: #065f46;
        }
        .message.error {
            background-color: #fee2e2;
            color: #991b1b;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="text-3xl font-bold text-gray-800 mb-6">Delete Existing Entity</h1>
        {% if message %}
            <div class="message {{ 'success' if 'successfully' in message else 'error' }}">
                <pre>{{ message }}</pre>
            </div>
        {% endif %}

        <form action="{{ url_for('delete_entity.delete_entity_route') }}" method="get" class="mb-6">
            <div class="form-group">
                <label for="entity_type">Select Entity Type:</label>
                <select name="entity_type" id="entity_type" onchange="this.form.submit()">
                    <option value="">-- Select Type --</option>
                    <option value="Character" {% if selected_entity == 'Character' %}selected{% endif %}>Character</option>
                    <option value="Player" {% if selected_entity == 'Player' %}selected{% endif %}>Player</option>
                    <option value="Item" {% if selected_entity == 'Item' %}selected{% endif %}>Item</option>
                    <option value="Location" {% if selected_entity == 'Location' %}selected{% endif %}>Location</option>
                    <option value="Event" {% if selected_entity == 'Event' %}selected{% endif %}>Event</option>
                    <option value="Session" {% if selected_entity == 'Session' %}selected{% endif %}>Session</option>
                    <option value="Player_Characters" {% if selected_entity == 'Player_Characters' %}selected{% endif %}>Player Character Link</option>
                    <option value="Event_Participants" {% if selected_entity == 'Event_Participants' %}selected{% endif %}>Event Participant Link</option>
                    <option value="GenericRelation" {% if selected_entity == 'GenericRelation' %}selected{% endif %}>Generic Relation</option>
                </select>
            </div>
        </form>

        {% if selected_entity %}
        <h2 class="text-2xl font-semibold text-gray-700 mb-4">Delete {{ selected_entity.replace('_', ' ').title() }}</h2>
        <form action="{{ url_for('delete_entity.delete_entity_route') }}" method="post">
            <input type="hidden" name="entity_type" value="{{ selected_entity }}">

            {% if selected_entity in ['Character', 'Player', 'Item', 'Location', 'Event', 'Session', 'GenericRelation'] %}
            <div class="form-group">
                <label for="entity_id">ID to Delete:</label>
                <input type="number" id="entity_id" name="id" placeholder="e.g., 1" required>
            </div>
            {% elif selected_entity == 'Player_Characters' %}
            <div class="form-group">
                <label for="pc_character_id">Character ID:</label>
                <input type="number" id="pc_character_id" name="character_id" placeholder="e.g., 1" required>
            </div>
            <div class="form-group">
                <label for="pc_player_id">Player ID:</label>
                <input type="number" id="pc_player_id" name="player_id" placeholder="e.g., 1" required>
            </div>
            {% elif selected_entity == 'Event_Participants' %}
            <div class="form-group">
                <label for="ep_character_id">Character ID:</label>
                <input type="number" id="ep_character_id" name="character_id" placeholder="e.g., 1" required>
            </div>
            <div class="form-group">
                <label for="ep_event_id">Event ID:</label>
                <input type="number" id="ep_event_id" name="event_id" placeholder="e.g., 1" required>
            </div>
            {% endif %}

            <button type="submit" class="btn btn-danger">Delete {{ selected_entity.replace('_', ' ').title() }}</button>
        </form>
        {% endif %}
        <a href="{{ url_for('dashboard.dashboard') }}" class="btn btn-back">Back to Dashboard</a>
    </div>
</body>
</html>
'''

@delete_entity_bp.route('/delete_entity', methods=['GET', 'POST'])
def delete_entity_route():
    if 'is_dm' not in session:
        return redirect(url_for('auth.index'))

    message = None
    selected_entity = request.args.get('entity_type') # For GET requests (selecting type)

    if request.method == 'POST':
        entity_type = request.form['entity_type']
        row_count = 0
        try:
            if entity_type == 'Character':
                entity_id = request.form.get('id', type=int)
                if not entity_id: message = "Character ID is required."
                else: row_count = delete_character(entity_id)
            elif entity_type == 'Player':
                entity_id = request.form.get('id', type=int)
                if not entity_id: message = "Player ID is required."
                else: row_count = delete_player(entity_id)
            elif entity_type == 'Item':
                entity_id = request.form.get('id', type=int)
                if not entity_id: message = "Item ID is required."
                else: row_count = delete_item(entity_id)
            elif entity_type == 'Location':
                entity_id = request.form.get('id', type=int)
                if not entity_id: message = "Location ID is required."
                else: row_count = delete_location(entity_id)
            elif entity_type == 'Event':
                entity_id = request.form.get('id', type=int)
                if not entity_id: message = "Event ID is required."
                else: row_count = delete_event(entity_id)
            elif entity_type == 'Session':
                entity_id = request.form.get('id', type=int)
                if not entity_id: message = "Session ID is required."
                else: row_count = delete_session(entity_id)
            elif entity_type == 'Player_Characters':
                char_id = request.form.get('character_id', type=int)
                player_id = request.form.get('player_id', type=int)
                if not char_id or not player_id: message = "Character ID and Player ID are required."
                else: row_count = delete_player_character(char_id, player_id)
            elif entity_type == 'Event_Participants':
                char_id = request.form.get('character_id', type=int)
                event_id = request.form.get('event_id', type=int)
                if not char_id or not event_id: message = "Character ID and Event ID are required."
                else: row_count = delete_event_participant(char_id, event_id)
            elif entity_type == 'GenericRelation':
                entity_id = request.form.get('id', type=int)
                if not entity_id: message = "Relation ID is required."
                else: row_count = delete_generic_relation(entity_id)
            else:
                message = "Invalid entity type selected for deletion."

            if message is None: # Only set success/not found message if no specific error message was already set
                if row_count > 0:
                    message = f"{entity_type.replace('_', ' ').title()} deleted successfully!"
                else:
                    if entity_type in ['Player_Characters', 'Event_Participants']:
                        message = f"Link not found with provided IDs."
                    else:
                        message = f"{entity_type.replace('_', ' ').title()} not found."

        except Exception as e:
            message = f"Error deleting {entity_type} record: {e}"
            current_app.logger.error(f"Error deleting {entity_type} record: {e}")

    return render_template_string(DELETE_ENTITY_SELECT_HTML,
                                  selected_entity=selected_entity,
                                  message=message)
