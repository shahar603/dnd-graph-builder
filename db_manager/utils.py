import sqlite3
import os
from flask import g, current_app

DATABASE = 'DB/dnd_database.db' # Define your database file name here

def get_db_connection():
    """
    Establishes a database connection or returns the existing one.
    This function is used to ensure a single database connection per request.
    """
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        # Enable foreign key support for this connection
        db.execute('PRAGMA foreign_keys = ON;')
        # Set row_factory to sqlite3.Row to allow accessing columns by name
        db.row_factory = sqlite3.Row
    return db

def close_db_connection(exception):
    """
    Closes the database connection at the end of the request.
    """
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db_schema():
    """
    Initializes the database by creating all tables defined in the schema from db_init.sql.
    This function should be called once when the app starts.
    """
    # Ensure the DB directory exists
    if not os.path.exists('DB'):
        os.makedirs('DB')

    conn = None # Initialize conn to None
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        with open('DB/db_init.sql', 'r') as f:
            sql_script = f.read()
        cursor.executescript(sql_script)
        conn.commit()
        print("Database schema initialized/verified successfully.")
    except sqlite3.Error as e:
        print(f"An SQLite error occurred during DB schema initialization: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during DB schema initialization: {e}")
    finally:
        if conn:
            conn.close()

def get_table_names():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    # Filter out internal SQLite tables (like sqlite_sequence)
    tables = [t for t in tables if not t.startswith('sqlite_')]
    return tables

def get_table_columns(table_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = [row[1] for row in cursor.fetchall()]
    return columns

def get_table_data(table_name, filter_field=None, filter_value=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = f"SELECT * FROM {table_name}"
    params = []

    if filter_field and filter_value:
        query += f" WHERE {filter_field} LIKE ?"
        params.append(f"%{filter_value}%")

    try:
        cursor.execute(query, params)
        data = [list(row) for row in cursor.fetchall()]
        return data
    except sqlite3.OperationalError as e:
        # Log the error, but return empty list to prevent app crash
        current_app.logger.error(f"Error fetching data for table {table_name}: {e}")
        return []
    except Exception as e:
        current_app.logger.error(f"An unexpected error occurred while fetching data: {e}")
        return []

def get_graph_nodes():
    """
    Fetches all entities (Characters, Items, Locations, Events) to be used as nodes in the graph.
    Each node will have a unique ID (prefixed by type), name, and type.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    nodes = []

    # Fetch Characters
    cursor.execute("SELECT character_id, character_name, character_type FROM Character")
    for row in cursor.fetchall():
        nodes.append({
            'id': f"char_{row['character_id']}",
            'name': row['character_name'],
            'type': row['character_type'] if row['character_type'] else 'Character'
        })

    # Fetch Players (can be considered as a type of character or separate node)
    cursor.execute("SELECT player_id, player_name FROM Player")
    for row in cursor.fetchall():
        nodes.append({
            'id': f"player_{row['player_id']}",
            'name': row['player_name'],
            'type': 'Player'
        })

    # Fetch Items
    cursor.execute("SELECT item_id, item_name FROM Item")
    for row in cursor.fetchall():
        nodes.append({
            'id': f"item_{row['item_id']}",
            'name': row['item_name'],
            'type': 'Item'
        })

    # Fetch Locations
    cursor.execute("SELECT location_id, location_name FROM Location")
    for row in cursor.fetchall():
        nodes.append({
            'id': f"loc_{row['location_id']}",
            'name': row['location_name'],
            'type': 'Location'
        })

    # Fetch Events
    cursor.execute("SELECT event_id, event_description FROM Event")
    for row in cursor.fetchall():
        nodes.append({
            'id': f"event_{row['event_id']}",
            'name': row['event_description'] if row['event_description'] else f"Event {row['event_id']}",
            'type': 'Event'
        })

    return nodes

def get_graph_edges():
    """
    Fetches all relationships to be used as edges in the graph.
    This includes explicit foreign key relationships and generic relations.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    edges = []

    # Player_Characters relationship (Character plays as Player)
    cursor.execute("SELECT character_id, player_id FROM Player_Characters")
    for row in cursor.fetchall():
        edges.append({
            'source': f"char_{row['character_id']}",
            'target': f"player_{row['player_id']}",
            'type': 'plays_as',
            'description': 'Plays As'
        })

    # Item creator relationship (Character creates Item)
    cursor.execute("SELECT item_id, creator_id FROM Item WHERE creator_id IS NOT NULL")
    for row in cursor.fetchall():
        edges.append({
            'source': f"char_{row['creator_id']}",
            'target': f"item_{row['item_id']}",
            'type': 'creates',
            'description': 'Created By'
        })

    # Location ruler relationship (Character rules Location)
    cursor.execute("SELECT location_id, ruler FROM Location WHERE ruler IS NOT NULL")
    for row in cursor.fetchall():
        edges.append({
            'source': f"char_{row['ruler']}",
            'target': f"loc_{row['location_id']}",
            'type': 'rules',
            'description': 'Ruled By'
        })

    # Event_Participants relationship (Character participates in Event)
    cursor.execute("SELECT character_id, event_id FROM Event_Participants")
    for row in cursor.fetchall():
        edges.append({
            'source': f"char_{row['character_id']}",
            'target': f"event_{row['event_id']}",
            'type': 'participates_in',
            'description': 'Participates In'
        })

    # GenericRelation relationships
    # Need to map Table1Name/Table2Name to the correct prefix for node IDs
    entity_prefix_map = {
        'CHARACTER': 'char',
        'ITEM': 'item',
        'LOCATION': 'loc',
        'EVENT': 'event'
    }
    cursor.execute("SELECT Table1Name, Table1ID, Table2Name, Table2ID, relation_description FROM GenericRelation")
    for row in cursor.fetchall():
        source_prefix = entity_prefix_map.get(row['Table1Name'].upper())
        target_prefix = entity_prefix_map.get(row['Table2Name'].upper())

        if source_prefix and target_prefix:
            edges.append({
                'source': f"{source_prefix}_{row['Table1ID']}",
                'target': f"{target_prefix}_{row['Table2ID']}",
                'type': 'generic_relation',
                'description': row['relation_description'] if row['relation_description'] else 'Related To'
            })

    return edges


# --- Character CRUD Utilities ---

def get_character_by_id(character_id):
    """Fetches a single character by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Character WHERE character_id = ?", (character_id,))
    character = cursor.fetchone()
    return dict(character) if character else None

def get_all_characters():
    """Fetches all characters."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT character_id, character_name FROM Character") # Only fetch ID and name for dropdowns
    characters = cursor.fetchall()
    return [dict(row) for row in characters]

def add_character(name, description, char_type, alignment, access_level):
    """Adds a new character to the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Character (character_name, character_description, character_type, alignment, access_level) VALUES (?, ?, ?, ?, ?)",
        (name, description, char_type, alignment, access_level)
    )
    conn.commit()
    return cursor.lastrowid

def update_character(character_id, name=None, description=None, char_type=None, alignment=None, access_level=None):
    """Updates an existing character by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    updates = []
    params = []

    if name is not None:
        updates.append("character_name = ?")
        params.append(name)
    if description is not None:
        updates.append("character_description = ?")
        params.append(description)
    if char_type is not None:
        updates.append("character_type = ?")
        params.append(char_type)
    if alignment is not None:
        updates.append("alignment = ?")
        params.append(alignment)
    if access_level is not None:
        updates.append("access_level = ?")
        params.append(access_level)

    if not updates:
        return 0 # No fields to update

    params.append(character_id)
    cursor.execute(f"UPDATE Character SET {', '.join(updates)} WHERE character_id = ?", params)
    conn.commit()
    return cursor.rowcount

def delete_character(character_id):
    """Deletes a character by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Character WHERE character_id = ?", (character_id,))
    conn.commit()
    return cursor.rowcount

# --- Player CRUD Utilities ---
def get_player_by_id(player_id):
    """Fetches a single player by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Player WHERE player_id = ?", (player_id,))
    player = cursor.fetchone()
    return dict(player) if player else None

def get_all_players():
    """Fetches all players."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT player_id, player_name FROM Player")
    players = cursor.fetchall()
    return [dict(row) for row in players]

def add_player(player_name, access_level):
    """Adds a new player to the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Player (player_name, access_level) VALUES (?, ?)",
        (player_name, access_level)
    )
    conn.commit()
    return cursor.lastrowid

def update_player(player_id, player_name=None, access_level=None):
    """Updates an existing player by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    updates = []
    params = []
    if player_name is not None:
        updates.append("player_name = ?")
        params.append(player_name)
    if access_level is not None:
        updates.append("access_level = ?")
        params.append(access_level)
    if not updates: return 0
    params.append(player_id)
    cursor.execute(f"UPDATE Player SET {', '.join(updates)} WHERE player_id = ?", params)
    conn.commit()
    return cursor.rowcount

def delete_player(player_id):
    """Deletes a player by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Player WHERE player_id = ?", (player_id,))
    conn.commit()
    return cursor.rowcount

# --- Item CRUD Utilities ---
def get_item_by_id(item_id):
    """Fetches a single item by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Item WHERE item_id = ?", (item_id,))
    item = cursor.fetchone()
    return dict(item) if item else None

def add_item(item_name, item_description, value_in_gold, rarity, is_magical, creator_id=None):
    """Adds a new item to the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Item (item_name, item_description, value_in_gold, rarity, is_magical, creator_id) VALUES (?, ?, ?, ?, ?, ?)",
        (item_name, item_description, value_in_gold, rarity, is_magical, creator_id)
    )
    conn.commit()
    return cursor.lastrowid

def update_item(item_id, item_name=None, item_description=None, value_in_gold=None, rarity=None, is_magical=None, creator_id=None):
    """Updates an existing item by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    updates = []
    params = []
    if item_name is not None: updates.append("item_name = ?"); params.append(item_name)
    if item_description is not None: updates.append("item_description = ?"); params.append(item_description)
    if value_in_gold is not None: updates.append("value_in_gold = ?"); params.append(value_in_gold)
    if rarity is not None: updates.append("rarity = ?"); params.append(rarity)
    if is_magical is not None: updates.append("is_magical = ?"); params.append(is_magical)
    if creator_id is not None: updates.append("creator_id = ?"); params.append(creator_id)
    if not updates: return 0
    params.append(item_id)
    cursor.execute(f"UPDATE Item SET {', '.join(updates)} WHERE item_id = ?", params)
    conn.commit()
    return cursor.rowcount

def delete_item(item_id):
    """Deletes an item by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Item WHERE item_id = ?", (item_id,))
    conn.commit()
    return cursor.rowcount

# --- Location CRUD Utilities ---
def get_location_by_id(location_id):
    """Fetches a single location by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Location WHERE location_id = ?", (location_id,))
    location = cursor.fetchone()
    return dict(location) if location else None

def add_location(location_name, location_description, region, climate, ruler=None):
    """Adds a new location to the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Location (location_name, location_description, region, climate, ruler) VALUES (?, ?, ?, ?, ?)",
        (location_name, location_description, region, climate, ruler)
    )
    conn.commit()
    return cursor.lastrowid

def update_location(location_id, location_name=None, location_description=None, region=None, climate=None, ruler=None):
    """Updates an existing location by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    updates = []
    params = []
    if location_name is not None: updates.append("location_name = ?"); params.append(location_name)
    if location_description is not None: updates.append("location_description = ?"); params.append(location_description)
    if region is not None: updates.append("region = ?"); params.append(region)
    if climate is not None: updates.append("climate = ?"); params.append(climate)
    if ruler is not None: updates.append("ruler = ?"); params.append(ruler)
    if not updates: return 0
    params.append(location_id)
    cursor.execute(f"UPDATE Location SET {', '.join(updates)} WHERE location_id = ?", params)
    conn.commit()
    return cursor.rowcount

def delete_location(location_id):
    """Deletes a location by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Location WHERE location_id = ?", (location_id,))
    conn.commit()
    return cursor.rowcount

# --- Event CRUD Utilities ---
def get_event_by_id(event_id):
    """Fetches a single event by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Event WHERE event_id = ?", (event_id,))
    event = cursor.fetchone()
    return dict(event) if event else None

def get_all_events():
    """Fetches all events."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT event_id, event_description FROM Event")
    events = cursor.fetchall()
    return [dict(row) for row in events]

def add_event(event_description, event_type, era):
    """Adds a new event to the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Event (event_description, event_type, era) VALUES (?, ?, ?)",
        (event_description, event_type, era)
    )
    conn.commit()
    return cursor.lastrowid

def update_event(event_id, event_description=None, event_type=None, era=None):
    """Updates an existing event by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    updates = []
    params = []
    if event_description is not None: updates.append("event_description = ?"); params.append(event_description)
    if event_type is not None: updates.append("event_type = ?"); params.append(event_type)
    if era is not None: updates.append("era = ?"); params.append(era)
    if not updates: return 0
    params.append(event_id)
    cursor.execute(f"UPDATE Event SET {', '.join(updates)} WHERE event_id = ?", params)
    conn.commit()
    return cursor.rowcount

def delete_event(event_id):
    """Deletes an event by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Event WHERE event_id = ?", (event_id,))
    conn.commit()
    return cursor.rowcount

# --- Session CRUD Utilities ---
def get_session_by_id(session_id):
    """Fetches a single session by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Session WHERE session_id = ?", (session_id,))
    session_data = cursor.fetchone()
    return dict(session_data) if session_data else None

def get_all_sessions():
    """Fetches all sessions."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT session_id, session_description FROM Session")
    sessions = cursor.fetchall()
    return [dict(row) for row in sessions]

def add_session(session_description):
    """Adds a new session to the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Session (session_description) VALUES (?)",
        (session_description,)
    )
    conn.commit()
    return cursor.lastrowid

def update_session(session_id, session_description=None):
    """Updates an existing session by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    updates = []
    params = []
    if session_description is not None: updates.append("session_description = ?"); params.append(session_description)
    if not updates: return 0
    params.append(session_id)
    cursor.execute(f"UPDATE Session SET {', '.join(updates)} WHERE session_id = ?", params)
    conn.commit()
    return cursor.rowcount

def delete_session(session_id):
    """Deletes a session by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Session WHERE session_id = ?", (session_id,))
    conn.commit()
    return cursor.rowcount

# --- Player_Characters CRUD Utilities ---
def get_player_character_by_ids(character_id, player_id):
    """Fetches a single Player_Characters link by IDs."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Player_Characters WHERE character_id = ? AND player_id = ?", (character_id, player_id))
    link = cursor.fetchone()
    return dict(link) if link else None

def add_player_character(character_id, player_id, access_level):
    """Links a player to a character."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Player_Characters (character_id, player_id, access_level) VALUES (?, ?, ?)",
        (character_id, player_id, access_level)
    )
    conn.commit()
    return cursor.lastrowid # Note: This will return the rowid, not the composite PK

def update_player_character(character_id, player_id, access_level=None):
    """Updates an existing Player_Characters link by IDs."""
    conn = get_db_connection()
    cursor = conn.cursor()
    updates = []
    params = []
    if access_level is not None: updates.append("access_level = ?"); params.append(access_level)
    if not updates: return 0
    params.append(character_id)
    params.append(player_id)
    cursor.execute(f"UPDATE Player_Characters SET {', '.join(updates)} WHERE character_id = ? AND player_id = ?", params)
    conn.commit()
    return cursor.rowcount

def delete_player_character(character_id, player_id):
    """Deletes a Player_Characters link by IDs."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Player_Characters WHERE character_id = ? AND player_id = ?", (character_id, player_id))
    conn.commit()
    return cursor.rowcount

# --- Event_Participants CRUD Utilities ---
def get_event_participant_by_ids(character_id, event_id):
    """Fetches a single Event_Participants link by IDs."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Event_Participants WHERE character_id = ? AND event_id = ?", (character_id, event_id))
    link = cursor.fetchone()
    return dict(link) if link else None

def add_event_participant(character_id, event_id):
    """Links a character to an event."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Event_Participants (character_id, event_id) VALUES (?, ?)",
        (character_id, event_id)
    )
    conn.commit()
    return cursor.lastrowid # Note: This will return the rowid, not the composite PK

def update_event_participant(character_id, event_id):
    """Updates an existing Event_Participants link by IDs. (No updatable fields other than PK)"""
    # This table only has composite PK, so update means no change if PK matches.
    # If there were other fields, they would be added here.
    return 0 # No updatable fields for this table beyond its composite PK

def delete_event_participant(character_id, event_id):
    """Deletes an Event_Participants link by IDs."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Event_Participants WHERE character_id = ? AND event_id = ?", (character_id, event_id))
    conn.commit()
    return cursor.rowcount

# --- GenericRelation CRUD Utilities ---
def get_generic_relation_by_id(relation_id):
    """Fetches a single GenericRelation by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM GenericRelation WHERE relation_id = ?", (relation_id,))
    relation = cursor.fetchone()
    return dict(relation) if relation else None

def add_generic_relation(table1_name, table1_id, table2_name, table2_id, relation_description=None, relation_appearance=None):
    """Adds a generic relation between two entities."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO GenericRelation (Table1Name, Table1ID, Table2Name, Table2ID, relation_description, relation_appearance) VALUES (?, ?, ?, ?, ?, ?)",
        (table1_name, table1_id, table2_name, table2_id, relation_description, relation_appearance)
    )
    conn.commit()
    return cursor.lastrowid

def update_generic_relation(relation_id, table1_name=None, table1_id=None, table2_name=None, table2_id=None, relation_description=None, relation_appearance=None):
    """Updates an existing generic relation by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    updates = []
    params = []
    if table1_name is not None: updates.append("Table1Name = ?"); params.append(table1_name)
    if table1_id is not None: updates.append("Table1ID = ?"); params.append(table1_id)
    if table2_name is not None: updates.append("Table2Name = ?"); params.append(table2_name)
    if table2_id is not None: updates.append("Table2ID = ?"); params.append(table2_id)
    if relation_description is not None: updates.append("relation_description = ?"); params.append(relation_description)
    if relation_appearance is not None: updates.append("relation_appearance = ?"); params.append(relation_appearance)
    if not updates: return 0
    params.append(relation_id)
    cursor.execute(f"UPDATE GenericRelation SET {', '.join(updates)} WHERE relation_id = ?", params)
    conn.commit()
    return cursor.rowcount

def delete_generic_relation(relation_id):
    """Deletes a generic relation by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM GenericRelation WHERE relation_id = ?", (relation_id,))
    conn.commit()
    return cursor.rowcount
