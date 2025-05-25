from flask import Blueprint, render_template_string, request, session, redirect, url_for, current_app
from utils import add_character, add_player, add_item, add_location, add_event, add_player_character, add_event_participant, add_generic_relation, add_session, get_all_characters, get_all_players, get_all_events, get_all_sessions # Import all necessary add functions and lookup functions

create_entity_bp = Blueprint('create_entity', __name__)

CREATE_ENTITY_SELECT_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Create New Entity</title>
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
        <h1 class="text-3xl font-bold text-gray-800 mb-6">Create New Entity</h1>
        {% if message %}
            <div class="message {{ 'success' if 'successfully' in message else 'error' }}">
                <pre>{{ message }}</pre>
            </div>
        {% endif %}

        <form action="{{ url_for('create_entity.create_entity') }}" method="get" class="mb-6">
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

        {% if selected_entity == 'Character' %}
        <form action="{{ url_for('create_entity.create_entity') }}" method="post">
            <input type="hidden" name="entity_type" value="Character">
            <h2 class="text-2xl font-semibold text-gray-700 mb-4">Create Character</h2>
            <div class="form-group">
                <label for="character_name">Name:</label>
                <input type="text" id="character_name" name="character_name" placeholder="Aragorn" required>
            </div>
            <div class="form-group">
                <label for="character_description">Description:</label>
                <textarea id="character_description" name="character_description" rows="3" placeholder="A ranger, heir to Isildur..."></textarea>
            </div>
            <div class="form-group">
                <label for="character_type">Type:</label>
                <select id="character_type" name="character_type" required>
                    <option value="PC">PC</option>
                    <option value="NPC">NPC</option>
                    <option value="MONSTER">MONSTER</option>
                    <option value="DEITY">DEITY</option>
                    <option value="HISTORICAL_PC">HISTORICAL_PC</option>
                </select>
            </div>
            <div class="form-group">
                <label for="alignment">Alignment:</label>
                <select id="alignment" name="alignment" required>
                    <option value="GOOD">GOOD</option>
                    <option value="BAD">BAD</option>
                    <option value="LAWFUL">LAWFUL</option>
                    <option value="CHAOTIC">CHAOTIC</option>
                    <option value="GOOD_LAWFUL">GOOD_LAWFUL</option>
                    <option value="BAD_LAWFUL">BAD_LAWFUL</option>
                    <option value="GOOD_CHAOTIC">GOOD_CHAOTIC</option>
                    <option value="BAD_CHAOTIC">BAD_CHAOTIC</option>
                    <option value="NEUTRAL">NEUTRAL</option>
                    <option value="UNKNOWN">UNKNOWN</option>
                </select>
            </div>
            <div class="form-group">
                <label for="access_level">Access Level:</label>
                <select id="access_level" name="access_level" required>
                    <option value="ALL">ALL</option>
                    <option value="DM">DM</option>
                </select>
            </div>
            <button type="submit" class="btn btn-primary">Create Character</button>
        </form>
        {% elif selected_entity == 'Player' %}
        <form action="{{ url_for('create_entity.create_entity') }}" method="post">
            <input type="hidden" name="entity_type" value="Player">
            <h2 class="text-2xl font-semibold text-gray-700 mb-4">Create Player</h2>
            <div class="form-group">
                <label for="player_name">Player Name:</label>
                <input type="text" id="player_name" name="player_name" placeholder="Frodo Baggins Player" required>
            </div>
            <div class="form-group">
                <label for="access_level">Access Level:</label>
                <select id="access_level" name="access_level" required>
                    <option value="ALL">ALL</option>
                    <option value="DM">DM</option>
                </select>
            </div>
            <button type="submit" class="btn btn-primary">Create Player</button>
        </form>
        {% elif selected_entity == 'Item' %}
        <form action="{{ url_for('create_entity.create_entity') }}" method="post">
            <input type="hidden" name="entity_type" value="Item">
            <h2 class="text-2xl font-semibold text-gray-700 mb-4">Create Item</h2>
            <div class="form-group">
                <label for="item_name">Item Name:</label>
                <input type="text" id="item_name" name="item_name" placeholder="Sting" required>
            </div>
            <div class="form-group">
                <label for="item_description">Description:</label>
                <textarea id="item_description" name="item_description" rows="3" placeholder="A short sword that glows when orcs are near..."></textarea>
            </div>
            <div class="form-group">
                <label for="value_in_gold">Value (in Gold):</label>
                <input type="number" id="value_in_gold" name="value_in_gold" placeholder="100" required>
            </div>
            <div class="form-group">
                <label for="rarity">Rarity:</label>
                <select id="rarity" name="rarity" required>
                    <option value="COMMON">COMMON</option>
                    <option value="UNCOMMON">UNCOMMON</option>
                    <option value="RARE">RARE</option>
                    <option value="VERY_RARE">VERY_RARE</option>
                    <option value="LEGENDARY">LEGENDARY</option>
                </select>
            </div>
            <div class="form-group">
                <label for="is_magical">Is Magical?</label>
                <select id="is_magical" name="is_magical" required>
                    <option value="1">Yes</option>
                    <option value="0">No</option>
                </select>
            </div>
            <div class="form-group">
                <label for="creator_id">Creator Character ID (optional):</label>
                <select id="creator_id" name="creator_id">
                    <option value="">-- Select Character --</option>
                    {% for char in characters %}
                    <option value="{{ char.character_id }}">{{ char.character_name }} (ID: {{ char.character_id }})</option>
                    {% endfor %}
                </select>
            </div>
            <button type="submit" class="btn btn-primary">Create Item</button>
        </form>
        {% elif selected_entity == 'Location' %}
        <form action="{{ url_for('create_entity.create_entity') }}" method="post">
            <input type="hidden" name="entity_type" value="Location">
            <h2 class="text-2xl font-semibold text-gray-700 mb-4">Create Location</h2>
            <div class="form-group">
                <label for="location_name">Location Name:</label>
                <input type="text" id="location_name" name="location_name" placeholder="Shire" required>
            </div>
            <div class="form-group">
                <label for="location_description">Description:</label>
                <textarea id="location_description" name="location_description" rows="3" placeholder="A peaceful land..."></textarea>
            </div>
            <div class="form-group">
                <label for="region">Region:</label>
                <input type="text" id="region" name="region" placeholder="Middle-earth">
            </div>
            <div class="form-group">
                <label for="climate">Climate:</label>
                <input type="text" id="climate" name="climate" placeholder="Temperate">
            </div>
            <div class="form-group">
                <label for="ruler">Ruler Character ID (optional):</label>
                <select id="ruler" name="ruler">
                    <option value="">-- Select Character --</option>
                    {% for char in characters %}
                    <option value="{{ char.character_id }}">{{ char.character_name }} (ID: {{ char.character_id }})</option>
                    {% endfor %}
                </select>
            </div>
            <button type="submit" class="btn btn-primary">Create Location</button>
        </form>
        {% elif selected_entity == 'Event' %}
        <form action="{{ url_for('create_entity.create_entity') }}" method="post">
            <input type="hidden" name="entity_type" value="Event">
            <h2 class="text-2xl font-semibold text-gray-700 mb-4">Create Event</h2>
            <div class="form-group">
                <label for="event_description">Description:</label>
                <textarea id="event_description" name="event_description" rows="3" placeholder="The Battle of Helm's Deep..."></textarea>
            </div>
            <div class="form-group">
                <label for="event_type">Event Type:</label>
                <select id="event_type" name="event_type" required>
                    <option value="GENERAL">GENERAL</option>
                    <option value="HISTORICAL">HISTORICAL</option>
                    <option value="ENCOUNTER">ENCOUNTER</option>
                </select>
            </div>
            <div class="form-group">
                <label for="era">Era:</label>
                <input type="text" id="era" name="era" placeholder="Third Age">
            </div>
            <button type="submit" class="btn btn-primary">Create Event</button>
        </form>
        {% elif selected_entity == 'Session' %}
        <form action="{{ url_for('create_entity.create_entity') }}" method="post">
            <input type="hidden" name="entity_type" value="Session">
            <h2 class="text-2xl font-semibold text-gray-700 mb-4">Create Session</h2>
            <div class="form-group">
                <label for="session_description">Session Description:</label>
                <textarea id="session_description" name="session_description" rows="3" placeholder="Our heroes ventured into the goblin caves..."></textarea>
            </div>
            <button type="submit" class="btn btn-primary">Create Session</button>
        </form>
        {% elif selected_entity == 'Player_Characters' %}
        <form action="{{ url_for('create_entity.create_entity') }}" method="post">
            <input type="hidden" name="entity_type" value="Player_Characters">
            <h2 class="text-2xl font-semibold text-gray-700 mb-4">Link Player to Character</h2>
            <div class="form-group">
                <label for="pc_character_id">Character:</label>
                <select id="pc_character_id" name="character_id" required>
                    <option value="">-- Select Character --</option>
                    {% for char in characters %}
                    <option value="{{ char.character_id }}">{{ char.character_name }} (ID: {{ char.character_id }})</option>
                    {% endfor %}
                </select>
            </div>
            <div class="form-group">
                <label for="pc_player_id">Player:</label>
                <select id="pc_player_id" name="player_id" required>
                    <option value="">-- Select Player --</option>
                    {% for player in players %}
                    <option value="{{ player.player_id }}">{{ player.player_name }} (ID: {{ player.player_id }})</option>
                    {% endfor %}
                </select>
            </div>
            <div class="form-group">
                <label for="pc_access_level">Access Level:</label>
                <select id="pc_access_level" name="access_level" required>
                    <option value="ALL">ALL</option>
                    <option value="DM">DM</option>
                </select>
            </div>
            <button type="submit" class="btn btn-primary">Create Link</button>
        </form>
        {% elif selected_entity == 'Event_Participants' %}
        <form action="{{ url_for('create_entity.create_entity') }}" method="post">
            <input type="hidden" name="entity_type" value="Event_Participants">
            <h2 class="text-2xl font-semibold text-gray-700 mb-4">Link Character to Event</h2>
            <div class="form-group">
                <label for="ep_character_id">Character:</label>
                <select id="ep_character_id" name="character_id" required>
                    <option value="">-- Select Character --</option>
                    {% for char in characters %}
                    <option value="{{ char.character_id }}">{{ char.character_name }} (ID: {{ char.character_id }})</option>
                    {% endfor %}
                </select>
            </div>
            <div class="form-group">
                <label for="ep_event_id">Event:</label>
                <select id="ep_event_id" name="event_id" required>
                    <option value="">-- Select Event --</option>
                    {% for event in events %}
                    <option value="{{ event.event_id }}">{{ event.event_description }} (ID: {{ event.event_id }})</option>
                    {% endfor %}
                </select>
            </div>
            <button type="submit" class="btn btn-primary">Create Link</button>
        </form>
        {% elif selected_entity == 'GenericRelation' %}
        <form action="{{ url_for('create_entity.create_entity') }}" method="post">
            <input type="hidden" name="entity_type" value="GenericRelation">
            <h2 class="text-2xl font-semibold text-gray-700 mb-4">Create Generic Relation</h2>
            <div class="form-group">
                <label for="table1_name">Table 1 Name:</label>
                <select id="table1_name" name="Table1Name" required>
                    <option value="">-- Select Table --</option>
                    <option value="CHARACTER">CHARACTER</option>
                    <option value="ITEM">ITEM</option>
                    <option value="LOCATION">LOCATION</option>
                    <option value="EVENT">EVENT</option>
                </select>
            </div>
            <div class="form-group">
                <label for="table1_id">Table 1 ID:</label>
                <input type="number" id="table1_id" name="Table1ID" placeholder="1" required>
            </div>
            <div class="form-group">
                <label for="table2_name">Table 2 Name:</label>
                <select id="table2_name" name="Table2Name" required>
                    <option value="">-- Select Table --</option>
                    <option value="CHARACTER">CHARACTER</option>
                    <option value="ITEM">ITEM</option>
                    <option value="LOCATION">LOCATION</option>
                    <option value="EVENT">EVENT</option>
                </select>
            </div>
            <div class="form-group">
                <label for="table2_id">Table 2 ID:</label>
                <input type="number" id="table2_id" name="Table2ID" placeholder="2" required>
            </div>
            <div class="form-group">
                <label for="relation_description">Relation Description (optional):</label>
                <input type="text" id="relation_description" name="relation_description" placeholder="e.g., 'owns', 'is located in'">
            </div>
            <div class="form-group">
                <label for="relation_appearance">Relation Appearance Session ID (optional):</label>
                <select id="relation_appearance" name="relation_appearance">
                    <option value="">-- Select Session --</option>
                    {% for session_item in sessions %}
                    <option value="{{ session_item.session_id }}">{{ session_item.session_description }} (ID: {{ session_item.session_id }})</option>
                    {% endfor %}
                </select>
            </div>
            <button type="submit" class="btn btn-primary">Create Relation</button>
        </form>
        {% endif %}

        <a href="{{ url_for('dashboard.dashboard') }}" class="btn btn-back">Back to Dashboard</a>
    </div>
</body>
</html>
'''

@create_entity_bp.route('/create_entity', methods=['GET', 'POST'])
def create_entity():
    if 'is_dm' not in session:
        return redirect(url_for('auth.index'))

    message = None
    selected_entity = request.args.get('entity_type') # For GET requests (selecting type)

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

    if request.method == 'POST':
        entity_type = request.form['entity_type']
        try:
            new_id = None
            if entity_type == 'Character':
                name = request.form['character_name']
                description = request.form['character_description']
                char_type = request.form['character_type']
                alignment = request.form['alignment']
                access_level = request.form['access_level']
                new_id = add_character(name, description, char_type, alignment, access_level)
                message = f"Character '{name}' created successfully with ID: {new_id}!"
            elif entity_type == 'Player':
                player_name = request.form['player_name']
                access_level = request.form['access_level']
                new_id = add_player(player_name, access_level)
                message = f"Player '{player_name}' created successfully with ID: {new_id}!"
            elif entity_type == 'Item':
                item_name = request.form['item_name']
                item_description = request.form['item_description']
                value_in_gold = request.form['value_in_gold']
                rarity = request.form['rarity']
                is_magical = request.form['is_magical']
                creator_id = request.form.get('creator_id') # Can be empty
                new_id = add_item(item_name, item_description, value_in_gold, rarity, is_magical, creator_id if creator_id else None)
                message = f"Item '{item_name}' created successfully with ID: {new_id}!"
            elif entity_type == 'Location':
                location_name = request.form['location_name']
                location_description = request.form['location_description']
                region = request.form['region']
                climate = request.form['climate']
                ruler = request.form.get('ruler') # Can be empty
                new_id = add_location(location_name, location_description, region, climate, ruler if ruler else None)
                message = f"Location '{location_name}' created successfully with ID: {new_id}!"
            elif entity_type == 'Event':
                event_description = request.form['event_description']
                event_type = request.form['event_type']
                era = request.form['era']
                new_id = add_event(event_description, event_type, era)
                message = f"Event '{event_description}' created successfully with ID: {new_id}!"
            elif entity_type == 'Session':
                session_description = request.form['session_description']
                new_id = add_session(session_description)
                message = f"Session '{session_description}' created successfully with ID: {new_id}!"
            elif entity_type == 'Player_Characters':
                character_id = request.form['character_id']
                player_id = request.form['player_id']
                access_level = request.form['access_level']
                new_id = add_player_character(character_id, player_id, access_level)
                message = f"Player Character link created successfully (Char ID: {character_id}, Player ID: {player_id})!"
            elif entity_type == 'Event_Participants':
                character_id = request.form['character_id']
                event_id = request.form['event_id']
                new_id = add_event_participant(character_id, event_id)
                message = f"Event Participant link created successfully (Char ID: {character_id}, Event ID: {event_id})!"
            elif entity_type == 'GenericRelation':
                table1_name = request.form['Table1Name']
                table1_id = request.form['Table1ID']
                table2_name = request.form['Table2Name']
                table2_id = request.form['Table2ID']
                relation_description = request.form.get('relation_description')
                relation_appearance = request.form.get('relation_appearance')
                new_id = add_generic_relation(table1_name, table1_id, table2_name, table2_id,
                                            relation_description if relation_description else None,
                                            relation_appearance if relation_appearance else None)
                message = f"Generic Relation created successfully (ID: {new_id})!"
            else:
                message = "Invalid entity type selected."

        except Exception as e:
            message = f"Error creating {entity_type} record: {e}"
            current_app.logger.error(f"Error creating {entity_type} record: {e}")

        # After POST, re-render the form for the selected entity type,
        # and re-fetch lookup data if necessary
        selected_entity = entity_type
        if selected_entity in ['Item', 'Location', 'Player_Characters', 'Event_Participants', 'GenericRelation']:
            characters = get_all_characters()
            players = get_all_players()
            sessions = get_all_sessions()
            events = get_all_events()

    return render_template_string(CREATE_ENTITY_SELECT_HTML,
                                  selected_entity=selected_entity,
                                  message=message,
                                  characters=characters,
                                  players=players,
                                  sessions=sessions,
                                  events=events)
