from flask import Blueprint, render_template_string, request, session, redirect, url_for, current_app
from utils import (
    get_character_by_id, update_character, get_all_characters,
    get_player_by_id, update_player, get_all_players,
    get_item_by_id, update_item,
    get_location_by_id, update_location,
    get_event_by_id, update_event, get_all_events,
    get_session_by_id, update_session, get_all_sessions,
    get_player_character_by_ids, update_player_character,
    get_event_participant_by_ids, update_event_participant,
    get_generic_relation_by_id, update_generic_relation
)

update_entity_bp = Blueprint('update_entity', __name__)

UPDATE_ENTITY_SELECT_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Update Existing Entity</title>
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
            max-width: 800px;
            padding: 2.5rem;
            background-color: #ffffff;
            border-radius: 0.75rem;
            box-shadow: 0 10px 15px rgba(0, 0, 0, 0.1);
            text-align: center;
        }
        .form-group {
            margin-bottom: 1rem;
            text-align: left;
        }
        label {
            display: block;
            margin-bottom: 0.5rem;
            font-weight: 500;
            color: #374151;
        }
        input[type="text"], input[type="number"], select, textarea {
            width: 100%;
            padding: 0.75rem;
            border: 1px solid #d1d5db;
            border-radius: 0.5rem;
            font-size: 1rem;
            transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
        }
        input[type="text"]:focus, input[type="number"]:focus, select:focus, textarea:focus {
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
        <h1 class="text-3xl font-bold text-gray-800 mb-6">Update Existing Entity</h1>
        {% if message %}
            <div class="message {{ 'success' if 'successfully' in message else 'error' }}">
                <pre>{{ message }}</pre>
            </div>
        {% endif %}

        <form action="{{ url_for('update_entity.update_entity_route') }}" method="get" class="mb-6">
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
        <h2 class="text-2xl font-semibold text-gray-700 mb-4">Update {{ selected_entity.replace('_', ' ').title() }}</h2>
        <form action="{{ url_for('update_entity.update_entity_route') }}" method="post">
            <input type="hidden" name="entity_type" value="{{ selected_entity }}">

            {% if selected_entity in ['Character', 'Player', 'Item', 'Location', 'Event', 'Session', 'GenericRelation'] %}
            <div class="form-group">
                <label for="entity_id">ID to Update:</label>
                <input type="number" id="entity_id" name="id" placeholder="e.g., 1" value="{{ entity.get(primary_key_name) if entity }}" required>
            </div>
            {% elif selected_entity == 'Player_Characters' %}
            <div class="form-group">
                <label for="pc_character_id">Character ID:</label>
                <input type="number" id="pc_character_id" name="character_id" placeholder="e.g., 1" value="{{ entity.character_id if entity }}" required>
            </div>
            <div class="form-group">
                <label for="pc_player_id">Player ID:</label>
                <input type="number" id="pc_player_id" name="player_id" placeholder="e.g., 1" value="{{ entity.player_id if entity }}" required>
            </div>
            {% elif selected_entity == 'Event_Participants' %}
            <div class="form-group">
                <label for="ep_character_id">Character ID:</label>
                <input type="number" id="ep_character_id" name="character_id" placeholder="e.g., 1" value="{{ entity.character_id if entity }}" required>
            </div>
            <div class="form-group">
                <label for="ep_event_id">Event ID:</label>
                <input type="number" id="ep_event_id" name="event_id" placeholder="e.g., 1" value="{{ entity.event_id if entity }}" required>
            </div>
            {% endif %}

            <button type="submit" name="action" value="load" class="btn btn-primary">Load {{ selected_entity.replace('_', ' ').title() }}</button>
            <hr class="my-4">

            {% if entity %}
                {% if selected_entity == 'Character' %}
                <div class="form-group">
                    <label for="character_name">Name:</label>
                    <input type="text" id="character_name" name="character_name" value="{{ entity.character_name }}">
                </div>
                <div class="form-group">
                    <label for="character_description">Description:</label>
                    <textarea id="character_description" name="character_description" rows="3">{{ entity.character_description }}</textarea>
                </div>
                <div class="form-group">
                    <label for="character_type">Type:</label>
                    <select id="character_type" name="character_type">
                        <option value="PC" {% if entity.character_type == 'PC' %}selected{% endif %}>PC</option>
                        <option value="NPC" {% if entity.character_type == 'NPC' %}selected{% endif %}>NPC</option>
                        <option value="MONSTER" {% if entity.character_type == 'MONSTER' %}selected{% endif %}>MONSTER</option>
                        <option value="DEITY" {% if entity.character_type == 'DEITY' %}selected{% endif %}>DEITY</option>
                        <option value="HISTORICAL_PC" {% if entity.character_type == 'HISTORICAL_PC' %}selected{% endif %}>HISTORICAL_PC</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="alignment">Alignment:</label>
                    <select id="alignment" name="alignment">
                        <option value="GOOD" {% if entity.alignment == 'GOOD' %}selected{% endif %}>GOOD</option>
                        <option value="BAD" {% if entity.alignment == 'BAD' %}selected{% endif %}>BAD</option>
                        <option value="LAWFUL" {% if entity.alignment == 'LAWFUL' %}selected{% endif %}>LAWFUL</option>
                        <option value="CHAOTIC" {% if entity.alignment == 'CHAOTIC' %}selected{% endif %}>CHAOTIC</option>
                        <option value="GOOD_LAWFUL" {% if entity.alignment == 'GOOD_LAWFUL' %}selected{% endif %}>GOOD_LAWFUL</option>
                        <option value="BAD_LAWFUL" {% if entity.alignment == 'BAD_LAWFUL' %}selected{% endif %}>BAD_LAWFUL</option>
                        <option value="GOOD_CHAOTIC" {% if entity.alignment == 'GOOD_CHAOTIC' %}selected{% endif %}>GOOD_CHAOTIC</option>
                        <option value="BAD_CHAOTIC" {% if entity.alignment == 'BAD_CHAOTIC' %}selected{% endif %}>BAD_CHAOTIC</option>
                        <option value="NEUTRAL" {% if entity.alignment == 'NEUTRAL' %}selected{% endif %}>NEUTRAL</option>
                        <option value="UNKNOWN" {% if entity.alignment == 'UNKNOWN' %}selected{% endif %}>UNKNOWN</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="access_level">Access Level:</label>
                    <select id="access_level" name="access_level">
                        <option value="ALL" {% if entity.access_level == 'ALL' %}selected{% endif %}>ALL</option>
                        <option value="DM" {% if entity.access_level == 'DM' %}selected{% endif %}>DM</option>
                    </select>
                </div>
                {% elif selected_entity == 'Player' %}
                <div class="form-group">
                    <label for="player_name">Player Name:</label>
                    <input type="text" id="player_name" name="player_name" value="{{ entity.player_name }}">
                </div>
                <div class="form-group">
                    <label for="access_level">Access Level:</label>
                    <select id="access_level" name="access_level">
                        <option value="ALL" {% if entity.access_level == 'ALL' %}selected{% endif %}>ALL</option>
                        <option value="DM" {% if entity.access_level == 'DM' %}selected{% endif %}>DM</option>
                    </select>
                </div>
                {% elif selected_entity == 'Item' %}
                <div class="form-group">
                    <label for="item_name">Item Name:</label>
                    <input type="text" id="item_name" name="item_name" value="{{ entity.item_name }}">
                </div>
                <div class="form-group">
                    <label for="item_description">Description:</label>
                    <textarea id="item_description" name="item_description" rows="3">{{ entity.item_description }}</textarea>
                </div>
                <div class="form-group">
                    <label for="value_in_gold">Value (in Gold):</label>
                    <input type="number" id="value_in_gold" name="value_in_gold" value="{{ entity.value_in_gold }}">
                </div>
                <div class="form-group">
                    <label for="rarity">Rarity:</label>
                    <select id="rarity" name="rarity">
                        <option value="COMMON" {% if entity.rarity == 'COMMON' %}selected{% endif %}>COMMON</option>
                        <option value="UNCOMMON" {% if entity.rarity == 'UNCOMMON' %}selected{% endif %}>UNCOMMON</option>
                        <option value="RARE" {% if entity.rarity == 'RARE' %}selected{% endif %}>RARE</option>
                        <option value="VERY_RARE" {% if entity.rarity == 'VERY_RARE' %}selected{% endif %}>VERY_RARE</option>
                        <option value="LEGENDARY" {% if entity.rarity == 'LEGENDARY' %}selected{% endif %}>LEGENDARY</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="is_magical">Is Magical?</label>
                    <select id="is_magical" name="is_magical">
                        <option value="1" {% if entity.is_magical == 1 %}selected{% endif %}>Yes</option>
                        <option value="0" {% if entity.is_magical == 0 %}selected{% endif %}>No</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="creator_id">Creator Character ID (optional):</label>
                    <select id="creator_id" name="creator_id">
                        <option value="">-- Select Character --</option>
                        {% for char in characters %}
                        <option value="{{ char.character_id }}" {% if entity.creator_id == char.character_id %}selected{% endif %}>{{ char.character_name }} (ID: {{ char.character_id }})</option>
                        {% endfor %}
                    </select>
                </div>
                {% elif selected_entity == 'Location' %}
                <div class="form-group">
                    <label for="location_name">Location Name:</label>
                    <input type="text" id="location_name" name="location_name" value="{{ entity.location_name }}">
                </div>
                <div class="form-group">
                    <label for="location_description">Description:</label>
                    <textarea id="location_description" name="location_description" rows="3">{{ entity.location_description }}</textarea>
                </div>
                <div class="form-group">
                    <label for="region">Region:</label>
                    <input type="text" id="region" name="region" value="{{ entity.region }}">
                </div>
                <div class="form-group">
                    <label for="climate">Climate:</label>
                    <input type="text" id="climate" name="climate" value="{{ entity.climate }}">
                </div>
                <div class="form-group">
                    <label for="ruler">Ruler Character ID (optional):</label>
                    <select id="ruler" name="ruler">
                        <option value="">-- Select Character --</option>
                        {% for char in characters %}
                        <option value="{{ char.character_id }}" {% if entity.ruler == char.character_id %}selected{% endif %}>{{ char.character_name }} (ID: {{ char.character_id }})</option>
                        {% endfor %}
                    </select>
                </div>
                {% elif selected_entity == 'Event' %}
                <div class="form-group">
                    <label for="event_description">Description:</label>
                    <textarea id="event_description" name="event_description" rows="3">{{ entity.event_description }}</textarea>
                </div>
                <div class="form-group">
                    <label for="event_type">Event Type:</label>
                    <select id="event_type" name="event_type">
                        <option value="GENERAL" {% if entity.event_type == 'GENERAL' %}selected{% endif %}>GENERAL</option>
                        <option value="HISTORICAL" {% if entity.event_type == 'HISTORICAL' %}selected{% endif %}>HISTORICAL</option>
                        <option value="ENCOUNTER" {% if entity.event_type == 'ENCOUNTER' %}selected{% endif %}>ENCOUNTER</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="era">Era:</label>
                    <input type="text" id="era" name="era" value="{{ entity.era }}">
                </div>
                {% elif selected_entity == 'Session' %}
                <div class="form-group">
                    <label for="session_description">Session Description:</label>
                    <textarea id="session_description" name="session_description" rows="3">{{ entity.session_description }}</textarea>
                </div>
                {% elif selected_entity == 'Player_Characters' %}
                <div class="form-group">
                    <label for="pc_access_level">Access Level:</label>
                    <select id="pc_access_level" name="access_level">
                        <option value="ALL" {% if entity.access_level == 'ALL' %}selected{% endif %}>ALL</option>
                        <option value="DM" {% if entity.access_level == 'DM' %}selected{% endif %}>DM</option>
                    </select>
                </div>
                {% elif selected_entity == 'GenericRelation' %}
                <div class="form-group">
                    <label for="table1_name">Table 1 Name:</label>
                    <select id="table1_name" name="Table1Name">
                        <option value="CHARACTER" {% if entity.Table1Name == 'CHARACTER' %}selected{% endif %}>CHARACTER</option>
                        <option value="ITEM" {% if entity.Table1Name == 'ITEM' %}selected{% endif %}>ITEM</option>
                        <option value="LOCATION" {% if entity.Table1Name == 'LOCATION' %}selected{% endif %}>LOCATION</option>
                        <option value="EVENT" {% if entity.Table1Name == 'EVENT' %}selected{% endif %}>EVENT</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="table1_id">Table 1 ID:</label>
                    <input type="number" id="table1_id" name="Table1ID" value="{{ entity.Table1ID }}">
                </div>
                <div class="form-group">
                    <label for="table2_name">Table 2 Name:</label>
                    <select id="table2_name" name="Table2Name">
                        <option value="CHARACTER" {% if entity.Table2Name == 'CHARACTER' %}selected{% endif %}>CHARACTER</option>
                        <option value="ITEM" {% if entity.Table2Name == 'ITEM' %}selected{% endif %}>ITEM</option>
                        <option value="LOCATION" {% if entity.Table2Name == 'LOCATION' %}selected{% endif %}>LOCATION</option>
                        <option value="EVENT" {% if entity.Table2Name == 'EVENT' %}selected{% endif %}>EVENT</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="table2_id">Table 2 ID:</label>
                    <input type="number" id="table2_id" name="Table2ID" value="{{ entity.Table2ID }}">
                </div>
                <div class="form-group">
                    <label for="relation_description">Relation Description (optional):</label>
                    <input type="text" id="relation_description" name="relation_description" value="{{ entity.relation_description }}">
                </div>
                <div class="form-group">
                    <label for="relation_appearance">Relation Appearance Session ID (optional):</label>
                    <select id="relation_appearance" name="relation_appearance">
                        <option value="">-- Select Session --</option>
                        {% for session_item in sessions %}
                        <option value="{{ session_item.session_id }}" {% if entity.relation_appearance == session_item.session_id %}selected{% endif %}>{{ session_item.session_description }} (ID: {{ session_item.session_id }})</option>
                        {% endfor %}
                    </select>
                </div>
                {% endif %}
                <button type="submit" name="action" value="update" class="btn btn-primary">Update {{ selected_entity.replace('_', ' ').title() }}</button>
            {% endif %}
        </form>
        {% endif %}
        <a href="{{ url_for('dashboard.dashboard') }}" class="btn btn-back">Back to Dashboard</a>
    </div>
</body>
</html>
'''

@update_entity_bp.route('/update_entity', methods=['GET', 'POST'])
def update_entity_route():
    if 'is_dm' not in session:
        return redirect(url_for('auth.index'))

    message = None
    selected_entity = request.args.get('entity_type')
    entity = None
    primary_key_name = None # To store the name of the primary key for single-ID entities

    characters = []
    players = []
    sessions = []
    events = []

    # Fetch lookup data if an entity type is selected that needs it
    if selected_entity in ['Item', 'Location', 'Player_Characters', 'Event_Participants', 'GenericRelation']:
        characters = get_all_characters()
        players = get_all_players()
        sessions = get_all_sessions()
        events = get_all_events()

    if request.method == 'GET' and selected_entity:
        # Handle loading an entity for update
        if selected_entity == 'Character':
            primary_key_name = 'character_id'
            entity_id = request.args.get('id', type=int)
            if entity_id: entity = get_character_by_id(entity_id)
        elif selected_entity == 'Player':
            primary_key_name = 'player_id'
            entity_id = request.args.get('id', type=int)
            if entity_id: entity = get_player_by_id(entity_id)
        elif selected_entity == 'Item':
            primary_key_name = 'item_id'
            entity_id = request.args.get('id', type=int)
            if entity_id: entity = get_item_by_id(entity_id)
        elif selected_entity == 'Location':
            primary_key_name = 'location_id'
            entity_id = request.args.get('id', type=int)
            if entity_id: entity = get_location_by_id(entity_id)
        elif selected_entity == 'Event':
            primary_key_name = 'event_id'
            entity_id = request.args.get('id', type=int)
            if entity_id: entity = get_event_by_id(entity_id)
        elif selected_entity == 'Session':
            primary_key_name = 'session_id'
            entity_id = request.args.get('id', type=int)
            if entity_id: entity = get_session_by_id(entity_id)
        elif selected_entity == 'GenericRelation':
            primary_key_name = 'relation_id'
            entity_id = request.args.get('id', type=int)
            if entity_id: entity = get_generic_relation_by_id(entity_id)
        elif selected_entity == 'Player_Characters':
            char_id = request.args.get('character_id', type=int)
            player_id = request.args.get('player_id', type=int)
            if char_id and player_id: entity = get_player_character_by_ids(char_id, player_id)
        elif selected_entity == 'Event_Participants':
            char_id = request.args.get('character_id', type=int)
            event_id = request.args.get('event_id', type=int)
            if char_id and event_id: entity = get_event_participant_by_ids(char_id, event_id)

        if request.args.get('action') == 'load' and not entity:
            if selected_entity in ['Player_Characters', 'Event_Participants']:
                message = f"Link not found with provided IDs."
            else:
                message = f"{selected_entity.replace('_', ' ').title()} with ID {entity_id} not found."


    elif request.method == 'POST' and request.form.get('action') == 'update':
        entity_type = request.form['entity_type']
        try:
            row_count = 0
            if entity_type == 'Character':
                char_id = request.form.get('id', type=int)
                update_data = {k: request.form[k] for k in request.form if k not in ['entity_type', 'id', 'action'] and request.form[k]}
                row_count = update_character(
                    char_id,
                    name=update_data.get('character_name'),
                    description=update_data.get('character_description'),
                    char_type=update_data.get('character_type'),
                    alignment=update_data.get('alignment'),
                    access_level=update_data.get('access_level')
                )
                if row_count > 0: message = f"Character with ID {char_id} updated successfully!"
                entity = get_character_by_id(char_id) # Reload for display
                primary_key_name = 'character_id'
            elif entity_type == 'Player':
                player_id = request.form.get('id', type=int)
                update_data = {k: request.form[k] for k in request.form if k not in ['entity_type', 'id', 'action'] and request.form[k]}
                row_count = update_player(
                    player_id,
                    player_name=update_data.get('player_name'),
                    access_level=update_data.get('access_level')
                )
                if row_count > 0: message = f"Player with ID {player_id} updated successfully!"
                entity = get_player_by_id(player_id)
                primary_key_name = 'player_id'
            elif entity_type == 'Item':
                item_id = request.form.get('id', type=int)
                update_data = {k: request.form[k] for k in request.form if k not in ['entity_type', 'id', 'action'] and request.form[k]}
                row_count = update_item(
                    item_id,
                    item_name=update_data.get('item_name'),
                    item_description=update_data.get('item_description'),
                    value_in_gold=update_data.get('value_in_gold', type=int),
                    rarity=update_data.get('rarity'),
                    is_magical=update_data.get('is_magical', type=int),
                    creator_id=update_data.get('creator_id', type=int) if update_data.get('creator_id') else None
                )
                if row_count > 0: message = f"Item with ID {item_id} updated successfully!"
                entity = get_item_by_id(item_id)
                primary_key_name = 'item_id'
            elif entity_type == 'Location':
                location_id = request.form.get('id', type=int)
                update_data = {k: request.form[k] for k in request.form if k not in ['entity_type', 'id', 'action'] and request.form[k]}
                row_count = update_location(
                    location_id,
                    location_name=update_data.get('location_name'),
                    location_description=update_data.get('location_description'),
                    region=update_data.get('region'),
                    climate=update_data.get('climate'),
                    ruler=update_data.get('ruler', type=int) if update_data.get('ruler') else None
                )
                if row_count > 0: message = f"Location with ID {location_id} updated successfully!"
                entity = get_location_by_id(location_id)
                primary_key_name = 'location_id'
            elif entity_type == 'Event':
                event_id = request.form.get('id', type=int)
                update_data = {k: request.form[k] for k in request.form if k not in ['entity_type', 'id', 'action'] and request.form[k]}
                row_count = update_event(
                    event_id,
                    event_description=update_data.get('event_description'),
                    event_type=update_data.get('event_type'),
                    era=update_data.get('era')
                )
                if row_count > 0: message = f"Event with ID {event_id} updated successfully!"
                entity = get_event_by_id(event_id)
                primary_key_name = 'event_id'
            elif entity_type == 'Session':
                session_id = request.form.get('id', type=int)
                update_data = {k: request.form[k] for k in request.form if k not in ['entity_type', 'id', 'action'] and request.form[k]}
                row_count = update_session(
                    session_id,
                    session_description=update_data.get('session_description')
                )
                if row_count > 0: message = f"Session with ID {session_id} updated successfully!"
                entity = get_session_by_id(session_id)
                primary_key_name = 'session_id'
            elif entity_type == 'Player_Characters':
                char_id = request.form.get('character_id', type=int)
                player_id = request.form.get('player_id', type=int)
                access_level = request.form.get('access_level')
                row_count = update_player_character(char_id, player_id, access_level)
                if row_count > 0: message = f"Player Character link (Char ID: {char_id}, Player ID: {player_id}) updated successfully!"
                entity = get_player_character_by_ids(char_id, player_id)
            elif entity_type == 'Event_Participants':
                char_id = request.form.get('character_id', type=int)
                event_id = request.form.get('event_id', type=int)
                # No updatable fields for Event_Participants beyond composite PK
                message = "Event Participant link has no updatable fields other than its composite primary key."
                entity = get_event_participant_by_ids(char_id, event_id)
            elif entity_type == 'GenericRelation':
                relation_id = request.form.get('id', type=int)
                update_data = {k: request.form[k] for k in request.form if k not in ['entity_type', 'id', 'action'] and request.form[k]}
                row_count = update_generic_relation(
                    relation_id,
                    table1_name=update_data.get('Table1Name'),
                    table1_id=update_data.get('Table1ID', type=int),
                    table2_name=update_data.get('Table2Name'),
                    table2_id=update_data.get('Table2ID', type=int),
                    relation_description=update_data.get('relation_description'),
                    relation_appearance=update_data.get('relation_appearance', type=int) if update_data.get('relation_appearance') else None
                )
                if row_count > 0: message = f"Generic Relation with ID {relation_id} updated successfully!"
                entity = get_generic_relation_by_id(relation_id)
                primary_key_name = 'relation_id'
            else:
                message = "Invalid entity type selected for update."

            if row_count == 0 and not message: # Only set if no specific message was already set
                if entity_type in ['Player_Characters', 'Event_Participants']:
                    message = f"Link not found or no changes were made."
                else:
                    message = f"{entity_type.replace('_', ' ').title()} not found or no changes were made."

        except Exception as e:
            message = f"Error updating {entity_type} record: {e}"
            current_app.logger.error(f"Error updating {entity_type} record: {e}")

        # Re-fetch lookup data after POST
        if selected_entity in ['Item', 'Location', 'Player_Characters', 'Event_Participants', 'GenericRelation']:
            characters = get_all_characters()
            players = get_all_players()
            sessions = get_all_sessions()
            events = get_all_events()

    return render_template_string(UPDATE_ENTITY_SELECT_HTML,
                                  selected_entity=selected_entity,
                                  entity=entity,
                                  message=message,
                                  primary_key_name=primary_key_name,
                                  characters=characters,
                                  players=players,
                                  sessions=sessions,
                                  events=events)
