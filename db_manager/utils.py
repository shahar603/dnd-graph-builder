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
