import sqlite3
import os

DATABASE = 'DB\database.db'

def init_db():
    """
    Initializes the database by creating all tables defined in the schema.
    It also enables foreign key support.
    """
    conn = None # Initialize conn to None
    try:
        # Check if database file already exists
        db_exists = os.path.exists(DATABASE)

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        # Enable foreign key support
        cursor.execute('PRAGMA foreign_keys = ON;')

        # Create Character table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Character (
                character_id INTEGER PRIMARY KEY AUTOINCREMENT,
                character_name TEXT,
                character_description TEXT,
                character_type TEXT CHECK (character_type IN ('DEITY', 'MONSTER', 'NPC', 'PC', 'HISTORICAL_PC')),
                alignment TEXT CHECK (alignment IN ('GOOD', 'BAD', 'LAWFUL', 'CHAOTIC', 'GOOD_LAWFUL', 'BAD_LAWFUL', 'GOOD_CHAOTIC', 'BAD_CHAOTIC', 'NEUTRAL', 'UNKNOWN')),
                access_level TEXT DEFAULT 'ALL' CHECK (access_level IN ('ALL', 'DM'))
            )
        ''')

        # Create Player table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Player (
                player_id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_name TEXT,
                access_level TEXT DEFAULT 'ALL' CHECK (access_level IN ('ALL', 'DM'))
            )
        ''')

        # Create Player_Characters table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Player_Characters (
                character_id INTEGER UNIQUE,
                player_id INTEGER,
                access_level TEXT DEFAULT 'ALL' CHECK (access_level IN ('ALL', 'DM')),
                PRIMARY KEY (character_id, player_id),
                FOREIGN KEY (character_id) REFERENCES Character (character_id),
                FOREIGN KEY (player_id) REFERENCES Player (player_id)
            )
        ''')

        # Create Item table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Item (
                item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_name TEXT,
                item_description TEXT,
                value_in_gold INTEGER,
                rarity TEXT CHECK (rarity IN ('COMMON', 'UNCOMMON', 'RARE', 'VERY_RARE', 'LEGENDARY')),
                is_magical INTEGER, -- Using INTEGER for boolean (0 for false, 1 for true)
                creator_id INTEGER,
                FOREIGN KEY (creator_id) REFERENCES Character (character_id)
            )
        ''')

        # Create Location table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Location (
                location_id INTEGER PRIMARY KEY AUTOINCREMENT,
                location_name TEXT,
                location_description TEXT,
                region TEXT,
                climate TEXT,
                ruler INTEGER,
                FOREIGN KEY (ruler) REFERENCES Character (character_id)
            )
        ''')

        # Create Event table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Event (
                event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_description TEXT,
                event_type TEXT CHECK (event_type IN ('GENERAL', 'HISTORICAL', 'ENCOUNTER')),
                era TEXT
            )
        ''')

        # Create Event_Participants table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Event_Participants (
                character_id INTEGER,
                event_id INTEGER,
                PRIMARY KEY (character_id, event_id),
                FOREIGN KEY (character_id) REFERENCES Character (character_id),
                FOREIGN KEY (event_id) REFERENCES Event (event_id)
            )
        ''')

        # Create Session table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Session (
                session_id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_description TEXT
            )
        ''')

        # Create GenericRelation table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS GenericRelation (
                relation_id INTEGER PRIMARY KEY AUTOINCREMENT,
                Table1Name TEXT NOT NULL CHECK (Table1Name IN ('CHARACTER', 'ITEM', 'LOCATION', 'EVENT')),
                Table1ID INTEGER NOT NULL,
                Table2Name TEXT NOT NULL CHECK (Table2Name IN ('CHARACTER', 'ITEM', 'LOCATION', 'EVENT')),
                Table2ID INTEGER NOT NULL,
                relation_description TEXT,
                relation_appearance INTEGER,
                FOREIGN KEY (relation_appearance) REFERENCES Session (session_id)
            )
        ''')

        conn.commit()

        if db_exists:
            print(f"Database '{DATABASE}' already exists. Ensured all tables are present.")
        else:
            print(f"Database '{DATABASE}' created and tables initialized successfully!")

    except sqlite3.Error as e:
        print(f"An SQLite error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    init_db()